import os
import json
import re
import folder_paths
import comfy.sd


class LoraQueueHelper:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": ("MODEL",),
                "clip": ("CLIP",),
                "lora_list": ("STRING", {"multiline": True, "default": ""}),
                "range_str": ("STRING", {"default": "0-9"}),
                "strength": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
            },
        }
    
    RETURN_TYPES = ("MODEL", "CLIP", "STRING",)
    RETURN_NAMES = ("MODEL", "CLIP", "lora_info",)
    FUNCTION = "apply"
    CATEGORY = "🔵TOO-Pack/utils"
    OUTPUT_IS_LIST = (True, True, True,)

    def parse_range(self, range_str, total):
        """Parse range string like ViewCombo: '0-2', '1,3,5', '-1' etc."""
        if not range_str.strip():
            return list(range(total))
        
        if ',' in range_str:
            indices = [int(p.strip()) for p in range_str.split(',')]
            indices = [i if i >= 0 else total + i for i in indices]
            return [i for i in indices if 0 <= i < total]
        
        if '-' in range_str:
            match = re.match(r'^(-?\d+)-(-?\d+)$', range_str)
            if match:
                start = int(match.group(1))
                end = int(match.group(2))
                
                if start < 0:
                    start = total + start
                if end < 0:
                    end = total + end
                
                start = max(0, min(start, total - 1))
                end = max(0, min(end, total - 1))
                
                if start <= end:
                    return list(range(start, end + 1))
                else:
                    return list(range(start, end - 1, -1))
        
        try:
            idx = int(range_str)
            if idx < 0:
                idx = total + idx
            if 0 <= idx < total:
                return [idx]
        except:
            pass
        
        return list(range(total))

    def apply(self, model, clip, lora_list, range_str, strength):
        lines = [line.strip() for line in lora_list.split('\n') if line.strip()]
        
        if not lines:
            return ([model], [clip], ["No LoRAs specified"])
        
        indices = self.parse_range(range_str, len(lines))
        selected_loras = [lines[i] for i in indices if i < len(lines)]
        
        if not selected_loras:
            return ([model], [clip], ["No LoRAs in range"])
        
        models, clips, infos = [], [], []
        
        for lora_name in selected_loras:
            try:
                lora_path = folder_paths.get_full_path("loras", lora_name)
                lora = comfy.utils.load_torch_file(lora_path, safe_load=True)
                model_lora, clip_lora = comfy.sd.load_lora_for_models(model, clip, lora, strength, strength)
                models.append(model_lora)
                clips.append(clip_lora)
                infos.append(f"{lora_name} @ {strength}")
            except Exception as e:
                print(f"Error loading {lora_name}: {e}")
        
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
        except:
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
            filtered = [l for l in all_loras if l.startswith(folder_filter + os.sep) or l.startswith(folder_filter + "/")]
        
        return ("\n".join(filtered),)


NODE_CLASS_MAPPINGS = {
    "LoraQueueHelper": LoraQueueHelper,
    "LoraListHelper": LoraListHelper,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LoraQueueHelper": "Lora Queue Helper",
    "LoraListHelper": "Lora List Helper",
}
