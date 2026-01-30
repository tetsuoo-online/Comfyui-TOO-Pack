"""
TOO Preset Text Node
Provides a dropdown with text presets that can be managed via a dialog
"""
import os
import json
import folder_paths

class TOOPresetText:
    def __init__(self):
        self.type = "TOOPresetText"
        
    @classmethod
    def INPUT_TYPES(cls):
        # Get the presets directory
        presets_dir = cls.get_presets_dir()
        
        # Load presets
        presets = cls.load_presets(presets_dir)
        preset_names = list(presets.keys()) if presets else ["default"]
        
        return {
            "required": {
                "preset": (preset_names, {"default": preset_names[0] if preset_names else "default"}),
            },
        }
    
    @classmethod
    def get_presets_dir(cls):
        """Get the presets directory path"""
        # Get the custom nodes directory
        custom_nodes_dir = folder_paths.get_folder_paths("custom_nodes")[0]
        
        # Find the Comfyui-TOO-Pack directory
        too_pack_dir = None
        for root, dirs, files in os.walk(custom_nodes_dir):
            if "__init__.py" in files:
                with open(os.path.join(root, "__init__.py"), 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "Comfyui-TOO-Pack" in content:
                        too_pack_dir = root
                        break
        
        if too_pack_dir is None:
            # Fallback to current directory
            too_pack_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up to the pack root
            while not os.path.exists(os.path.join(too_pack_dir, "__init__.py")):
                parent = os.path.dirname(too_pack_dir)
                if parent == too_pack_dir:
                    break
                too_pack_dir = parent
        
        presets_dir = os.path.join(too_pack_dir, "presets")
        os.makedirs(presets_dir, exist_ok=True)
        
        return presets_dir
    
    @classmethod
    def load_presets(cls, presets_dir):
        """Load presets from the presets directory"""
        presets_file = os.path.join(presets_dir, "text_presets.json")
        
        if os.path.exists(presets_file):
            try:
                with open(presets_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading presets: {e}")
                return {"default": ""}
        else:
            # Create default presets
            default_presets = {
                "default negative": "worst quality, low quality, jpeg artifacts",
                "remove": "\\b",
                "regex : extract filename from": "([^\\\\\/]+)_safetensors$"
            }
            cls.save_presets(presets_dir, default_presets)
            return default_presets
    
    @classmethod
    def save_presets(cls, presets_dir, presets):
        """Save presets to the presets directory"""
        presets_file = os.path.join(presets_dir, "text_presets.json")
        try:
            with open(presets_file, 'w', encoding='utf-8') as f:
                json.dump(presets, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error saving presets: {e}")
            return False
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "get_preset_value"
    CATEGORY = "🔵TOO-Pack/utils"
    
    def get_preset_value(self, preset):
        """Return the value for the selected preset"""
        presets_dir = self.get_presets_dir()
        presets = self.load_presets(presets_dir)
        
        return (presets.get(preset, ""),)

# Web API endpoints for preset management
from server import PromptServer
from aiohttp import web

@PromptServer.instance.routes.get("/too/presets/list")
async def get_presets_list(request):
    """Get list of all presets"""
    presets_dir = TOOPresetText.get_presets_dir()
    presets = TOOPresetText.load_presets(presets_dir)
    return web.json_response(presets)

@PromptServer.instance.routes.post("/too/presets/save")
async def save_presets(request):
    """Save presets"""
    try:
        data = await request.json()
        presets = data.get("presets", {})
        presets_dir = TOOPresetText.get_presets_dir()
        success = TOOPresetText.save_presets(presets_dir, presets)
        return web.json_response({"success": success})
    except Exception as e:
        return web.json_response({"success": False, "error": str(e)})

# Node registration
NODE_CLASS_MAPPINGS = {
    "TOOPresetText": TOOPresetText
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TOOPresetText": "TOO Preset Text 📋"
}
