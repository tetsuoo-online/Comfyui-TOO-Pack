import hashlib
import os
import folder_paths

class TOOImageMetadata:
    """
    Node pour créer des métadonnées d'image au format Civitai (A1111).
    Ces métadonnées peuvent être utilisées avec TOO Smart Image Saver.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "positive": ("STRING", {
                    "multiline": True,
                    "default": ""
                }),
                "negative": ("STRING", {
                    "multiline": True,
                    "default": ""
                }),
                "seed": ("STRING", {
                    "default": "",
                }),
                "steps": ("STRING", {
                    "default": "",
                }),
                "cfg": ("STRING", {
                    "default": "",
                }),
                "sampler_name": ("STRING", {
                    "default": ""
                }),
                "scheduler": ("STRING", {
                    "default": ""
                }),
            },
            "optional": {
                "model": ("STRING", {
                    "default": ""
                }),
                "loras": ("STRING", {
                    "multiline": True,
                    "default": ""
                }),
                "custom": ("STRING", {
                    "default": "",
                    "multiline": False
                }),
                "metadata": ("METADATA", {
                    "tooltip": "Métadonnées existantes à éditer"
                }),
            }
        }

    RETURN_TYPES = ("METADATA",)
    RETURN_NAMES = ("metadata",)
    FUNCTION = "create_metadata"
    OUTPUT_NODE = False
    CATEGORY = "🔵TOO-Pack/image"

    def create_metadata(self, positive, negative, seed, steps, cfg, sampler_name, scheduler, model="", loras="", custom="", metadata=None):
        # Si metadata est fourni, partir de ces valeurs
        if metadata and isinstance(metadata, dict):
            model_name = metadata.get("model_name", "")
            model_hash = metadata.get("model_hash", "")
            lora_hashes = metadata.get("lora_hashes", {}).copy()
            base_positive = metadata.get("positive", "")
            base_negative = metadata.get("negative", "")
            base_seed = metadata.get("seed", "")
            base_steps = metadata.get("steps", "")
            base_cfg = metadata.get("cfg", "")
            base_sampler = metadata.get("sampler_name", "")
            base_scheduler = metadata.get("scheduler", "")
            base_custom = metadata.get("custom", "")
        else:
            model_name = ""
            model_hash = ""
            lora_hashes = {}
            base_positive = ""
            base_negative = ""
            base_seed = ""
            base_steps = ""
            base_cfg = ""
            base_sampler = ""
            base_scheduler = ""
            base_custom = ""

        # Appliquer les widgets (priorité sur metadata si non vides)
        # Un espace unique " " permet d'effacer une valeur
        def apply_widget(widget_value, base_value):
            if widget_value == " ":
                return ""
            elif widget_value:
                return widget_value.strip()
            else:
                return base_value

        final_positive = apply_widget(positive, base_positive)
        final_negative = apply_widget(negative, base_negative)
        final_seed = apply_widget(seed, base_seed)
        final_steps = apply_widget(steps, base_steps)
        final_cfg = apply_widget(cfg, base_cfg)
        final_sampler = apply_widget(sampler_name, base_sampler)
        final_scheduler = apply_widget(scheduler, base_scheduler)
        final_custom = apply_widget(custom, base_custom)

        # Traiter le model
        if model == " ":
            model_name = ""
            model_hash = ""
        elif model:
            model = model.strip()
            full_path = self._get_checkpoint_path(model)
            if full_path and os.path.exists(full_path):
                model_hash = self._calculate_sha256(full_path)[:10]
                model_name = os.path.splitext(os.path.basename(model))[0]
            else:
                model_name = os.path.splitext(os.path.basename(model))[0]

        # Traiter les loras
        if loras == " ":
            lora_hashes = {}
        elif loras:
            # Remplacer les retours à la ligne par des virgules, puis séparer
            loras_cleaned = loras.replace('\n', ',').replace('\r', ',')
            lora_list = [l.strip() for l in loras_cleaned.split(',') if l.strip()]
            
            # Réinitialiser lora_hashes si on fournit de nouvelles loras
            lora_hashes = {}
            
            for lora_path in lora_list:
                full_path = self._get_lora_path(lora_path)
                lora_name = os.path.splitext(os.path.basename(lora_path))[0]
                if full_path and os.path.exists(full_path):
                    lora_hash = self._calculate_lora_hash(full_path)
                    lora_hashes[lora_name] = lora_hash

        metadata_dict = {
            "model_name": model_name,
            "model_hash": model_hash,
            "lora_hashes": lora_hashes,
            "positive": final_positive,
            "negative": final_negative,
            "seed": final_seed,
            "steps": final_steps,
            "cfg": final_cfg,
            "sampler_name": final_sampler,
            "scheduler": final_scheduler,
            "custom": final_custom
        }

        return (metadata_dict,)

    def _get_checkpoint_path(self, ckpt_name):
        """Trouve le chemin absolu d'un checkpoint via folder_paths"""
        try:
            checkpoints = folder_paths.get_filename_list("checkpoints")
            if ckpt_name in checkpoints:
                return folder_paths.get_full_path("checkpoints", ckpt_name)
        except:
            pass
        return None

    def _get_lora_path(self, lora_name):
        """Trouve le chemin absolu d'un lora via folder_paths"""
        try:
            loras = folder_paths.get_filename_list("loras")
            if lora_name in loras:
                return folder_paths.get_full_path("loras", lora_name)
        except:
            pass
        return None

    def _calculate_sha256(self, filepath):
        """Calcule le hash SHA256 d'un fichier"""
        sha256_hash = hashlib.sha256()
        try:
            with open(filepath, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            print(f"⚠️ Erreur calcul hash pour {filepath}: {e}")
            return ""

    def _calculate_lora_hash(self, filepath):
        """Calcule le hash SHA256 d'un lora en excluant les métadonnées safetensors (compatible A1111/Civitai AutoV3)"""
        try:
            hash_sha256 = hashlib.sha256()
            blksize = 1024 * 1024

            with open(filepath, "rb") as f:
                header = f.read(8)
                n = int.from_bytes(header, "little")
                offset = n + 8
                f.seek(offset)

                for chunk in iter(lambda: f.read(blksize), b""):
                    hash_sha256.update(chunk)

            return hash_sha256.hexdigest()[:12]
        except Exception as e:
            print(f"⚠️ Erreur calcul hash lora pour {filepath}: {e}")
            return ""

NODE_CLASS_MAPPINGS = {
    "TOOImageMetadata": TOOImageMetadata
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TOOImageMetadata": "📝 TOO Image Metadata"
}