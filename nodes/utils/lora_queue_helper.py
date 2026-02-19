import os
import folder_paths
import comfy.sd
import comfy.utils


class LoraQueueHelper:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": ("MODEL",),
                "clip": ("CLIP",),
                "lora_list": ("STRING", {"multiline": True, "default": ""}),
                "strength": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
            },
        }

    RETURN_TYPES = ("MODEL", "CLIP", "STRING")
    RETURN_NAMES = ("MODEL", "CLIP", "lora_info")
    FUNCTION = "apply"
    CATEGORY = "🔵TOO-Pack/utils"
    OUTPUT_IS_LIST = (True, True, True)

    def apply(self, model, clip, lora_list, strength):
        lines = [line.strip() for line in lora_list.split("\n") if line.strip()]
        if not lines:
            return ([model], [clip], ["No LoRAs specified"])

        models, clips, infos = [], [], []

        for lora_name in lines:
            try:
                lora_path = folder_paths.get_full_path("loras", lora_name)
                if lora_path is None or not os.path.isfile(lora_path):
                    print(f"[LoraQueueHelper] LoRA not found: {lora_name}")
                    infos.append(f"{lora_name} @ {strength} [NOT FOUND]")
                    models.append(model)
                    clips.append(clip)
                    continue
                lora = comfy.utils.load_torch_file(lora_path, safe_load=True)
                model_lora, clip_lora = comfy.sd.load_lora_for_models(model, clip, lora, strength, strength)
                models.append(model_lora)
                clips.append(clip_lora)
                infos.append(f"{lora_name} @ {strength}")
                del lora
            except Exception as e:
                print(f"[LoraQueueHelper] Error loading {lora_name}: {e}")
                infos.append(f"{lora_name} @ {strength} [ERROR: {e}]")
                models.append(model)
                clips.append(clip)

        return (models, clips, infos)


class LoraListHelper:
    """Lists all LoRAs, optionally filtered by folder. Compatible with ViewCombo."""

    @classmethod
    def INPUT_TYPES(cls):
        lora_folder = folder_paths.get_folder_paths("loras")[0]
        folders = ["All"]
        try:
            for root, dirs, files in os.walk(lora_folder):
                for d in dirs:
                    rel_path = os.path.relpath(os.path.join(root, d), lora_folder)
                    folders.append(rel_path)
        except Exception:
            pass
        return {
            "required": {
                "folder_filter": (folders,),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("lora_list",)
    FUNCTION = "list_loras"
    CATEGORY = "🔵TOO-Pack/utils"

    def list_loras(self, folder_filter):
        all_loras = folder_paths.get_filename_list("loras")
        if folder_filter == "All":
            filtered = all_loras
        else:
            filtered = [
                l for l in all_loras
                if l.startswith(folder_filter + os.sep) or l.startswith(folder_filter + "/")
            ]
        return ("\n".join(filtered),)


NODE_CLASS_MAPPINGS = {
    "LoraQueueHelper": LoraQueueHelper,
    "LoraListHelper": LoraListHelper,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LoraQueueHelper": "Lora Queue Helper",
    "LoraListHelper": "Lora List Helper",
}
