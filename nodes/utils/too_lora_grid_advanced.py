"""
LoRA Grid Tester (Advanced) — TOO-Pack
Variante de LoRA Grid pour les pipelines de sampling avances
(RandomNoise / GUIDER / SamplerCustomAdvanced), incompatibles
avec common_ksampler (cfg/sampler_name/scheduler/denoise).

Le node prend directement noise/guider/sampler/sigmas en entree.
Pour chaque LoRA, TOUS les ModelPatcher portes par le guider sont
detectes par introspection (attribut "model_patcher", mais aussi
"uncond_model_patcher" pour Guider_DualModel, etc.) puis clones et
patches avec le LoRA. Un nouveau guider (copie superficielle) reutilise
ensuite les conds/cfg deja en place — sans avoir besoin de connaitre
le type exact du guider ni de le reconstruire depuis zero.

Sources de LoRA :
Widget texte multiligne "loras" : une entree par ligne
   chemin:str_model

Format :
chemin/vers/lora.safetensors
chemin/vers/lora.safetensors:1.0
chemin/vers/lora.safetensors:"label"  -> lora weight=0, label personnalise
"""

import os
import re
import copy
import hashlib
import numpy as np
import torch
import folder_paths
import comfy.utils
import comfy.sd
import comfy.sample
import comfy.model_management
import comfy.model_patcher
from PIL import Image, ImageDraw, ImageFont


class LoraGridAdvanced:

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
                "vae":           ("VAE",),
                "noise":         ("NOISE",),
                "guider":        ("GUIDER",),
                "sampler":       ("SAMPLER",),
                "sigmas":        ("SIGMAS",),
                "latent_image":  ("LATENT",),
                "loras": ("STRING", {
                    "multiline": True,
                    "default":   "# path:str_model\n# ex: my_lora.safetensors:1.0\n# ex: my_lora.safetensors:\"no lora\""
                }),
                "grid_cols":     ("INT",   {"default": 4,    "min": 1,   "max": 16}),
                "grid_padding":  ("INT",   {"default": 4,    "min": 0,   "max": 64}),
                "add_labels":    ("BOOLEAN", {"default": True}),
                "label_height":  ("INT",   {"default": 24,   "min": 12,  "max": 64}),
                "font_size":     ("INT",   {"default": 30,   "min": 8,   "max": 48}),
                "label_color":   ("STRING", {"default": "#ffffff"}),
                "bg_color":      ("STRING", {"default": "#111111"}),
                "footer_text":        ("STRING", {"default": ""}),
            },

        }

    RETURN_TYPES  = ("IMAGE", "IMAGE")
    RETURN_NAMES  = ("grid", "images")
    FUNCTION      = "generate_grid"
    CATEGORY      = "\U0001f535TOO-Pack/utils"

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
                has_explicit_weight = False
            else:
                if len(parts) > 1 and parts[1].strip():
                    try:    sm = float(parts[1]); has_explicit_weight = True
                    except: sm = 1.0; has_explicit_weight = False
                else:
                    sm = 1.0; has_explicit_weight = False
            entries.append({"path": path, "strength_model": sm, "display_label": display_label, "is_null": is_null, "has_explicit_weight": has_explicit_weight})
        return entries

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
                       add_labels, label_height, font_size, fg_hex, bg_hex, footer_text=""):
        pil_images = [self._tensor_to_pil(t) for t in tensors]
        n    = len(pil_images)
        cols = max(1, min(cols, n))
        rows = (n + cols - 1) // cols

        cell_w, cell_h = pil_images[0].size
        lh      = label_height if add_labels else 0

        footer_text = (footer_text or "").strip("\n").rstrip()

        total_w = cols * cell_w + (cols + 1) * padding
        total_h_base = rows * (cell_h + lh) + (rows + 1) * padding

        bg_rgb    = self._hex_to_rgb(bg_hex)
        label_rgb = self._hex_to_rgb(fg_hex)

        font = None
        if add_labels or footer_text:
            for name in ("arial.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf"):
                try: font = ImageFont.truetype(name, font_size); break
                except: pass
            if font is None:
                font = ImageFont.load_default()

        footer_lines = []
        footer_h = 0
        if footer_text:
            line_h = font_size + 4
            for raw_line in footer_text.split("\n"):
                raw_line = raw_line.rstrip()
                if not raw_line:
                    footer_lines.append("")
                    continue
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

    # ── introspection des ModelPatcher portes par le guider ─────────

    @staticmethod
    def _model_patcher_attrs(guider):
        """Detecte tous les attributs ModelPatcher du guider (model_patcher,
        uncond_model_patcher pour Guider_DualModel, etc.) afin de patcher le
        LoRA sur tous les modeles reellement utilises au sampling, quel que
        soit le type de guider (CFGGuider, Guider_DualModel, ou autre)."""
        return [name for name, value in vars(guider).items()
                if isinstance(value, comfy.model_patcher.ModelPatcher)]

    @classmethod
    def IS_CHANGED(cls, vae, noise, guider, sampler, sigmas, latent_image,
                   loras, grid_cols, grid_padding, add_labels, label_height,
                   font_size, label_color, bg_color, footer_text):
        latent_hash = hashlib.md5(
            latent_image["samples"].cpu().numpy().tobytes()
        ).hexdigest()[:8]
        sigmas_hash = hashlib.md5(sigmas.cpu().numpy().tobytes()).hexdigest()[:8]
        model_sigs = tuple(cls._obj_sig(getattr(guider, n)) for n in cls._model_patcher_attrs(guider))
        key = (model_sigs, cls._obj_sig(vae), cls._obj_sig(sampler),
               sigmas_hash, getattr(noise, "seed", None),
               loras.strip(), latent_hash,
               (footer_text or "").strip("\n").rstrip())
        return hashlib.md5(str(key).encode()).hexdigest()

    # ── cle de cache ─────────────────────────────────────────────

    @classmethod
    def _cache_key(cls, guider, sampler, sigmas, noise, loras, latent_image):
        latent_hash = hashlib.md5(
            latent_image["samples"].cpu().numpy().tobytes()
        ).hexdigest()[:8]
        sigmas_hash = hashlib.md5(sigmas.cpu().numpy().tobytes()).hexdigest()[:8]
        model_sigs = tuple(cls._obj_sig(getattr(guider, n)) for n in cls._model_patcher_attrs(guider))
        raw = (model_sigs, cls._obj_sig(sampler),
               sigmas_hash, getattr(noise, "seed", None),
               loras.strip(), latent_hash)
        return hashlib.md5(str(raw).encode()).hexdigest()

    # ── sampling via guider ────────────────────────────────────────

    @staticmethod
    def _run_sample(active_guider, noise, latent, sampler, sigmas, noise_mask):
        gen_noise = noise.generate_noise(latent)
        disable_pbar = not comfy.utils.PROGRESS_BAR_ENABLED
        samples = active_guider.sample(
            gen_noise, latent["samples"], sampler, sigmas,
            denoise_mask=noise_mask, callback=None,
            disable_pbar=disable_pbar, seed=getattr(noise, "seed", None))
        samples = samples.to(comfy.model_management.intermediate_device())
        out = latent.copy()
        out["samples"] = samples
        return out

    @staticmethod
    def _build_lora_guider(guider, model_attrs, weights, sm):
        """Clone le guider et patche le LoRA sur chacun de ses ModelPatcher
        (model_patcher seul pour CFGGuider, +uncond_model_patcher pour
        Guider_DualModel, etc.)."""
        guider_lora = copy.copy(guider)
        for attr_name in model_attrs:
            base_mp = getattr(guider, attr_name)
            patched_mp, _ = comfy.sd.load_lora_for_models(base_mp, None, weights, sm, 1.0)
            setattr(guider_lora, attr_name, patched_mp)
        guider_lora.model_options = guider_lora.model_patcher.model_options
        return guider_lora

    # ── main ──────────────────────────────────────────────────────

    def generate_grid(self, vae, noise, guider, sampler, sigmas, latent_image,
                      loras, grid_cols, grid_padding, add_labels, label_height,
                      font_size, label_color, bg_color, footer_text):

        lora_entries = self._parse_loras_text(loras)

        print(f"[LoraGridAdvanced] {len(lora_entries)} LoRA au total")

        model_attrs = self._model_patcher_attrs(guider)
        print(f"[LoraGridAdvanced] modeles detectes sur le guider : {model_attrs}")

        base_model = guider.model_patcher
        fixed_samples = comfy.sample.fix_empty_latent_channels(base_model, latent_image["samples"])
        latent = latent_image.copy()
        latent["samples"] = fixed_samples
        noise_mask = latent.get("noise_mask")

        if not lora_entries:
            print("[LoraGridAdvanced] Aucune entree LoRA — sample sans LoRA.")
            try:
                latent_out = self._run_sample(guider, noise, latent, sampler, sigmas, noise_mask)
                decoded = self._vae_decode(vae, latent_out)
                images_batch = decoded
                grid = self._assemble_grid(
                    [decoded[0]], ["no lora"], grid_cols, grid_padding,
                    add_labels, label_height, font_size, label_color, bg_color, footer_text)
                return (grid, images_batch)
            except Exception as e:
                print(f"[LoraGridAdvanced] erreur sample sans LoRA : {e}")
                blank = torch.zeros(1, 64, 64, 3)
                return (blank, blank)

        cache_key = self._cache_key(guider, sampler, sigmas, noise, loras, latent_image)

        if cache_key in LoraGridAdvanced._cache:
            print(f"[LoraGridAdvanced] cache HIT ({cache_key[:8]}…)")
            cached = LoraGridAdvanced._cache[cache_key]
        else:
            print(f"[LoraGridAdvanced] cache MISS ({cache_key[:8]}…) — sampling")
            cached = []

            for i, entry in enumerate(lora_entries):
                path_raw = entry["path"]
                sm       = entry["strength_model"]
                is_null  = entry.get("is_null", False)
                dlabel   = entry.get("display_label")

                lbl = dlabel if dlabel is not None \
                      else os.path.splitext(os.path.basename(path_raw))[0]
                if entry.get("has_explicit_weight"):
                    lbl = f"{lbl}:{sm:g}"

                if is_null:
                    print(f"[LoraGridAdvanced] #{i} null slot → '{lbl}'")
                    try:
                        latent_out = self._run_sample(guider, noise, latent, sampler, sigmas, noise_mask)
                    except Exception as e:
                        import traceback
                        print(f"[LoraGridAdvanced] erreur sampling null #{i} : {e}")
                        traceback.print_exc()
                        continue
                    try:
                        decoded = self._vae_decode(vae, latent_out)
                    except Exception as e:
                        print(f"[LoraGridAdvanced] erreur VAE decode null #{i} : {e}")
                        continue
                    cached.append((decoded[0].clone(), lbl))
                    print(f"[LoraGridAdvanced] OK #{len(cached)} (null) {decoded.shape}")
                    continue

                lora_full = self._find_lora(path_raw)
                if not lora_full:
                    print(f"[LoraGridAdvanced] #{i} introuvable : {path_raw!r}")
                    continue

                print(f"[LoraGridAdvanced] #{i} {os.path.basename(lora_full)} sm={sm}")

                try:
                    weights = comfy.utils.load_torch_file(lora_full, safe_load=True)
                    guider_lora = self._build_lora_guider(guider, model_attrs, weights, sm)
                except Exception as e:
                    print(f"[LoraGridAdvanced] erreur chargement/patch #{i} : {e}")
                    continue

                try:
                    latent_out = self._run_sample(guider_lora, noise, latent, sampler, sigmas, noise_mask)
                except Exception as e:
                    import traceback
                    print(f"[LoraGridAdvanced] erreur sampling #{i} : {e}")
                    traceback.print_exc()
                    continue

                try:
                    decoded = self._vae_decode(vae, latent_out)
                except Exception as e:
                    import traceback
                    print(f"[LoraGridAdvanced] erreur VAE decode #{i} : {e}")
                    traceback.print_exc()
                    continue

                cached.append((decoded[0].clone(), lbl))
                print(f"[LoraGridAdvanced] OK #{len(cached)} {decoded.shape}")

            LoraGridAdvanced._cache[cache_key] = cached
            print(f"[LoraGridAdvanced] {len(cached)} images en cache ({cache_key[:8]}…)")

        if not cached:
            print("[LoraGridAdvanced] Aucune image produite.")
            blank = torch.zeros(1, 64, 64, 3)
            return (blank, blank)

        image_tensors = [t for t, _ in cached]
        labels        = [l for _, l in cached]
        images_batch  = torch.stack(image_tensors, dim=0)

        grid = self._assemble_grid(
            image_tensors, labels, grid_cols, grid_padding,
            add_labels, label_height, font_size, label_color, bg_color, footer_text)

        print(f"[LoraGridAdvanced] grille {grid.shape}, batch {images_batch.shape}")
        return (grid, images_batch)


NODE_CLASS_MAPPINGS = {
    "LoRA Grid Advanced": LoraGridAdvanced,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LoRA Grid Advanced": "\U0001f9ea TOO LoRA Grid (Advanced)",
}