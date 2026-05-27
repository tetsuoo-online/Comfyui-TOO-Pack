"""
LoRA Grid Tester — TOO-Pack
Compatible avec les modeles image classiques (SD, SDXL, FLUX)
et les modeles Cosmos/Anima (latent 5D avec T=1).

Sources de LoRA (cumulatives) :
1. Widget texte multiligne "loras" : une entree par ligne
   chemin:str_model
2. Interface JS du node (lora_entries serialisees dans le workflow)

Regles de fusion :
- Widget seul -> widget uniquement
- JS seul -> JS uniquement
- Les deux -> widget d'abord, JS ensuite

Format widget :
chemin/vers/lora.safetensors
chemin/vers/lora.safetensors:1.0
chemin/vers/lora.safetensors:"label"  -> lora weight=0, label personnalise
"""

import os
import json
import hashlib
import re
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import folder_paths
import comfy.utils
import comfy.sd
import comfy.samplers
import torch
from nodes import common_ksampler

class LoraGrid:

    _cache: dict = {}

    @staticmethod
    def _obj_sig(obj):
        """Signature stable basee sur les poids reels, pas l'adresse du wrapper Python."""
        try:
            p = next(iter(obj.parameters()))
            return p.data_ptr()
        except Exception:
            return id(obj)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model":         ("MODEL",),
                "clip":          ("CLIP",),
                "vae":           ("VAE",),
                "positive":      ("CONDITIONING",),
                "negative":      ("CONDITIONING",),
                "latent_image":  ("LATENT",),
                "loras": ("STRING", {
                    "multiline": True,
                    "default":   "# path:str_model\n# ex: my_lora.safetensors:1.0\n# ex: my_lora.safetensors:\"no lora\""
                }),
                "seed":          ("INT",   {"default": 0,    "min": 0,   "max": 0xffffffffffffffff}),
                "steps":         ("INT",   {"default": 20,   "min": 1,   "max": 10000}),
                "cfg":           ("FLOAT", {"default": 7.0,  "min": 0.0, "max": 100.0, "step": 0.1}),
                "sampler_name":  (comfy.samplers.KSampler.SAMPLERS,),
                "scheduler":     (comfy.samplers.KSampler.SCHEDULERS,),
                "denoise":       ("FLOAT", {"default": 1.0,  "min": 0.0, "max": 1.0,   "step": 0.01}),
                "grid_cols":     ("INT",   {"default": 4,    "min": 1,   "max": 16}),
                "grid_padding":  ("INT",   {"default": 4,    "min": 0,   "max": 64}),
                "add_labels":    ("BOOLEAN", {"default": True}),
                "label_height":  ("INT",   {"default": 24,   "min": 12,  "max": 64}),
                "font_size":     ("INT",   {"default": 14,   "min": 8,   "max": 48}),
                "label_color":   ("STRING", {"default": "#ffffff"}),
                "bg_color":      ("STRING", {"default": "#111111"}),
                "footer_text":        ("STRING", {"default": ""}),
            },
            "hidden": {
                "extra_pnginfo": "EXTRA_PNGINFO",
                "unique_id":     "UNIQUE_ID",
            },
        }

    RETURN_TYPES  = ("IMAGE", "IMAGE")
    RETURN_NAMES  = ("grid", "images")
    FUNCTION      = "generate_grid"
    CATEGORY      = "\U0001f535TOO-Pack/utils"

    @classmethod
    def IS_CHANGED(cls, model, clip, vae, positive, negative, latent_image,
                   loras, seed, steps, cfg, sampler_name, scheduler, denoise,
                   grid_cols, grid_padding, add_labels, label_height,
                   font_size, label_color, bg_color, footer,
                   extra_pnginfo=None, unique_id=None):
        latent_hash = hashlib.md5(
            latent_image["samples"].cpu().numpy().tobytes()
        ).hexdigest()[:8]
        js_str = cls._get_js_entries_raw(extra_pnginfo, unique_id)
        key = (unique_id,
               LoraGrid._obj_sig(model), LoraGrid._obj_sig(clip), LoraGrid._obj_sig(vae),
               LoraGrid._obj_sig(positive), LoraGrid._obj_sig(negative),
               loras.strip(), seed, steps, round(cfg, 4),
               sampler_name, scheduler, round(denoise, 4),
               latent_hash, js_str, (footer or "").strip("\n").rstrip())
        return hashlib.md5(str(key).encode()).hexdigest()

    # ── lecture lora_entries depuis le workflow JSON ──────────────

    @staticmethod
    def _find_node_in_workflow(extra_pnginfo, unique_id):
        if not extra_pnginfo or not unique_id:
            return None
        try:
            uid = int(unique_id)
            workflow = extra_pnginfo.get("workflow", extra_pnginfo)
            for node in workflow.get("nodes", []):
                if int(node.get("id", -1)) == uid:
                    return node
        except Exception as e:
            print(f"[LoraGrid] _find_node_in_workflow : {e}")
        return None

    @classmethod
    def _get_js_entries_raw(cls, extra_pnginfo, unique_id):
        node = cls._find_node_in_workflow(extra_pnginfo, unique_id)
        if node is None:
            return ""
        entries = node.get("lora_entries",
                  node.get("properties", {}).get("lora_entries", []))
        try:
            return json.dumps(entries, sort_keys=True)
        except:
            return str(entries)

    @classmethod
    def _get_js_entries(cls, extra_pnginfo, unique_id):
        node = cls._find_node_in_workflow(extra_pnginfo, unique_id)
        if node is None:
            return []
        raw = node.get("lora_entries",
              node.get("properties", {}).get("lora_entries", []))
        if not raw:
            return []
        entries = []
        for e in raw:
            path_full = str(e.get("path", "")).strip()
            if not path_full:
                continue

            m = re.search(r':"([^"]*)"$', path_full)
            display_label = None
            is_null = False
            if m:
                display_label = m.group(1)
                is_null = True
                path_full = path_full[:m.start()].strip()

            if is_null:
                sm = 0.0
            else:
                try: sm = float(e.get("strength_model", 1.0))
                except: sm = 1.0

            entries.append({"path": path_full, "strength_model": sm,
                            "display_label": display_label, "is_null": is_null})
        print(f"[LoraGrid] JS entries : {len(entries)}")
        return entries

    # ── parsing widget texte ──────────────────────────────────────

    @staticmethod
    def _parse_loras_text(text):
        entries = []
        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            m = re.search(r':"([^"]*)"$', line)
            display_label = None
            is_null = False
            if m:
                display_label = m.group(1)
                is_null = True
                line = line[:m.start()]

            parts = line.split(":")
            path = parts[0].strip()
            if not path:
                continue

            if is_null:
                sm = 0.0
            else:
                try:    sm = float(parts[1]) if len(parts) > 1 and parts[1].strip() else 1.0
                except: sm = 1.0

            entries.append({"path": path, "strength_model": sm, "display_label": display_label, "is_null": is_null})
        return entries

    @staticmethod
    def _merge_entries(text_entries, js_entries):
        if text_entries and js_entries:
            print(f"[LoraGrid] fusion : {len(text_entries)} widget + {len(js_entries)} JS")
        elif text_entries:
            print(f"[LoraGrid] source : widget ({len(text_entries)})")
        elif js_entries:
            print(f"[LoraGrid] source : JS ({len(js_entries)})")
        return text_entries + js_entries

    # ── cle de cache ─────────────────────────────────────────────

    @staticmethod
    def _cache_key(unique_id, model, clip, vae, positive, negative, loras, seed, steps, cfg,
                   sampler_name, scheduler, denoise, latent_image, js_str):
        latent_hash = hashlib.md5(
            latent_image["samples"].cpu().numpy().tobytes()
        ).hexdigest()[:8]
        raw = (unique_id,
               LoraGrid._obj_sig(model), LoraGrid._obj_sig(clip), LoraGrid._obj_sig(vae),
               LoraGrid._obj_sig(positive), LoraGrid._obj_sig(negative),
               loras.strip(), seed, steps, round(cfg, 4),
               sampler_name, scheduler, round(denoise, 4),
               latent_hash, js_str)
        return hashlib.md5(str(raw).encode()).hexdigest()

    # ── recherche fichier LoRA ────────────────────────────────────

    @staticmethod
    def _find_lora(path_str):
        candidates = [path_str]
        if not any(path_str.lower().endswith(e)
                   for e in (".safetensors", ".pt", ".ckpt", ".bin")):
            candidates += [path_str + e for e in (".safetensors", ".pt", ".ckpt")]
        base, ext = os.path.splitext(path_str)
        if ext:
            candidates.append(base)
        for c in candidates:
            full = folder_paths.get_full_path("loras", c)
            if full and os.path.isfile(full):
                return full
        return None

    # ── decode VAE ───────────────────────────────────────────────

    @staticmethod
    def _vae_decode(vae, latent_out):
        images = vae.decode(latent_out["samples"])
        if len(images.shape) == 5:
            images = images.reshape(-1, images.shape[-3], images.shape[-2], images.shape[-1])
        return images

    # ── assemblage grille ─────────────────────────────────────────

    @staticmethod
    def _hex_to_rgb(h):
        h = h.lstrip("#")
        if len(h) == 3: h = h[0]*2 + h[1]*2 + h[2]*2
        try:    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
        except: return (0, 0, 0)

    @staticmethod
    def _tensor_to_pil(t):
        if t.ndim == 4: t = t[0]
        arr = (t.cpu().float().numpy() * 255.0).clip(0, 255).astype(np.uint8)
        if arr.shape[2] == 1: arr = np.repeat(arr, 3, axis=2)
        return Image.fromarray(arr[:, :, :3])

    def _assemble_grid(self, tensors, labels, cols, padding,
                       add_labels, label_height, font_size, fg_hex, bg_hex, footer=""):
        pil_images = [self._tensor_to_pil(t) for t in tensors]
        n    = len(pil_images)
        cols = max(1, min(cols, n))
        rows = (n + cols - 1) // cols

        cell_w, cell_h = pil_images[0].size
        lh      = label_height if add_labels else 0

        footer = (footer or "").strip("\n").rstrip()

        total_w = cols * cell_w + (cols + 1) * padding
        total_h_base = rows * (cell_h + lh) + (rows + 1) * padding

        bg_rgb    = self._hex_to_rgb(bg_hex)
        label_rgb = self._hex_to_rgb(fg_hex)

        # Charger la police en avance pour calculer footer_h
        font = None
        if add_labels or footer:
            for name in ("arial.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf"):
                try: font = ImageFont.truetype(name, font_size); break
                except: pass
            if font is None:
                font = ImageFont.load_default()

        # Calcul dynamique de la hauteur du footer (wrap + multilignes)
        footer_lines = []
        footer_h = 0
        if footer:
            line_h = font_size + 4
            for raw_line in footer.split("\n"):
                raw_line = raw_line.rstrip()
                if not raw_line:
                    footer_lines.append("")
                    continue
                # wrap si le texte dépasse la largeur
                words = raw_line.split(" ")
                current = ""
                for word in words:
                    test = (current + " " + word).strip()
                    try:
                        bb = ImageDraw.Draw(Image.new("RGB", (1, 1))).textbbox((0, 0), test, font=font)
                        tw = bb[2] - bb[0]
                    except Exception:
                        tw = len(test) * font_size // 2
                    if tw <= total_w - 2 * padding or not current:
                        current = test
                    else:
                        footer_lines.append(current)
                        current = word
                if current:
                    footer_lines.append(current)
            footer_h = len(footer_lines) * line_h + padding * 2 if footer_lines else 0

        total_h = total_h_base + footer_h

        grid = Image.new("RGB", (total_w, total_h), bg_rgb)
        draw = ImageDraw.Draw(grid)

        for idx, (img, lbl) in enumerate(zip(pil_images, labels)):
            col = idx % cols
            row = idx // cols
            x   = padding + col * (cell_w + padding)
            y   = padding + row * (cell_h + lh + padding)
            grid.paste(img, (x, y))
            if add_labels and lbl:
                try:
                    bb = draw.textbbox((0, 0), lbl, font=font)
                    tw, th = bb[2]-bb[0], bb[3]-bb[1]
                except Exception:
                    tw, th = len(lbl)*font_size//2, font_size
                draw.text((x+(cell_w-tw)//2, y+cell_h+(lh-th)//2),
                          lbl, fill=label_rgb, font=font)

        if footer_lines:
            line_h = font_size + 4
            fy = total_h_base + padding
            for line in footer_lines:
                if line:
                    try:
                        bb = draw.textbbox((0, 0), line, font=font)
                        tw = bb[2] - bb[0]
                    except Exception:
                        tw = len(line) * font_size // 2
                    draw.text(((total_w - tw) // 2, fy), line, fill=label_rgb, font=font)
                fy += line_h

        arr = np.array(grid).astype(np.float32) / 255.0
        return torch.from_numpy(arr).unsqueeze(0)

    # ── main ──────────────────────────────────────────────────────

    def generate_grid(self, model, clip, vae, positive, negative, latent_image,
                      loras, seed, steps, cfg, sampler_name, scheduler, denoise,
                      grid_cols, grid_padding, add_labels, label_height,
                      font_size, label_color, bg_color, footer,
                      extra_pnginfo=None, unique_id=None):

        text_entries = self._parse_loras_text(loras)
        js_entries   = self._get_js_entries(extra_pnginfo, unique_id)
        lora_entries = self._merge_entries(text_entries, js_entries)

        print(f"[LoraGrid] {len(lora_entries)} LoRA au total")
        if not lora_entries:
            print("[LoraGrid] Aucune entree LoRA.")
            blank = torch.zeros(1, 64, 64, 3)
            return (blank, blank)

        js_str    = self._get_js_entries_raw(extra_pnginfo, unique_id)
        cache_key = self._cache_key(unique_id, model, clip, vae, positive, negative, loras,
                                    seed, steps, cfg, sampler_name, scheduler, denoise,
                                    latent_image, js_str)

        if cache_key in LoraGrid._cache:
            print(f"[LoraGrid] cache HIT ({cache_key[:8]}…)")
            cached = LoraGrid._cache[cache_key]
        else:
            print(f"[LoraGrid] cache MISS ({cache_key[:8]}…) — sampling")
            cached = []

            for i, entry in enumerate(lora_entries):
                path_raw = entry["path"]
                sm       = entry["strength_model"]
                is_null  = entry.get("is_null", False)
                dlabel   = entry.get("display_label")

                lbl = dlabel if dlabel is not None \
                      else os.path.splitext(os.path.basename(path_raw))[0]

                if is_null:
                    print(f"[LoraGrid] #{i} null slot → '{lbl}'")
                    try:
                        latent_out = common_ksampler(
                            model, seed, steps, cfg,
                            sampler_name, scheduler,
                            positive, negative, latent_image,
                            denoise=denoise)[0]
                    except Exception as e:
                        import traceback
                        print(f"[LoraGrid] erreur sampling null #{i} : {e}")
                        traceback.print_exc()
                        continue
                    try:
                        decoded = self._vae_decode(vae, latent_out)
                    except Exception as e:
                        print(f"[LoraGrid] erreur VAE decode null #{i} : {e}")
                        continue
                    cached.append((decoded[0].clone(), lbl))
                    print(f"[LoraGrid] OK #{len(cached)} (null) {decoded.shape}")
                    continue

                lora_full = self._find_lora(path_raw)
                if not lora_full:
                    print(f"[LoraGrid] #{i} introuvable : {path_raw!r}")
                    continue

                print(f"[LoraGrid] #{i} {os.path.basename(lora_full)} sm={sm}")

                try:
                    weights = comfy.utils.load_torch_file(lora_full, safe_load=True)
                    model_lora, _ = comfy.sd.load_lora_for_models(
                        model, clip, weights, sm, 1.0)
                except Exception as e:
                    print(f"[LoraGrid] erreur chargement #{i} : {e}")
                    continue

                try:
                    latent_out = common_ksampler(
                        model_lora, seed, steps, cfg,
                        sampler_name, scheduler,
                        positive, negative, latent_image,
                        denoise=denoise)[0]
                except Exception as e:
                    import traceback
                    print(f"[LoraGrid] erreur sampling #{i} : {e}")
                    traceback.print_exc()
                    continue

                try:
                    decoded = self._vae_decode(vae, latent_out)
                except Exception as e:
                    import traceback
                    print(f"[LoraGrid] erreur VAE decode #{i} : {e}")
                    traceback.print_exc()
                    continue

                cached.append((decoded[0].clone(), lbl))
                print(f"[LoraGrid] OK #{len(cached)} {decoded.shape}")

            LoraGrid._cache[cache_key] = cached
            print(f"[LoraGrid] {len(cached)} images en cache ({cache_key[:8]}…)")

        if not cached:
            print("[LoraGrid] Aucune image produite.")
            blank = torch.zeros(1, 64, 64, 3)
            return (blank, blank)

        image_tensors = [t for t, _ in cached]
        labels        = [l for _, l in cached]
        images_batch  = torch.stack(image_tensors, dim=0)

        grid = self._assemble_grid(
            image_tensors, labels, grid_cols, grid_padding,
            add_labels, label_height, font_size, label_color, bg_color, footer)

        print(f"[LoraGrid] grille {grid.shape}, batch {images_batch.shape}")
        return (grid, images_batch)


NODE_CLASS_MAPPINGS = {
    "LoRA Grid": LoraGrid,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LoRA Grid": "\U0001f9ea TOO LoRA Grid",
}
