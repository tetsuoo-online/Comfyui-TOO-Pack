import os
import random
import torch
import numpy as np
from PIL import Image

class SmartImageLoader:
    """
    Charge une image selon la priorité : txt_path > img_path > img_directory > image input
    Retourne l'image + le chemin du fichier
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            },
            "optional": {
                "txt_path": ("STRING", {"default": "", "multiline": False}),
                "img_path": ("STRING", {"default": "", "multiline": False}),
                "img_directory": ("STRING", {"default": "", "multiline": False}),
                "image": ("IMAGE",),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("IMAGE", "FILE_PATH")
    FUNCTION = "load_smart"
    CATEGORY = "🔵TOO-Pack/image"

    def load_smart(self, seed, txt_path="", img_path="", img_directory="", image=None):
        """
        Charge une image selon l'ordre de priorité
        """
        file_path = "none"
        loaded_image = None
        
        # Priorité 1 : txt_path (fichier texte avec liste de chemins)
        if txt_path and txt_path.strip() and os.path.exists(txt_path):
            try:
                with open(txt_path, 'r', encoding='utf-8') as f:
                    lines = [line.strip() for line in f.readlines() if line.strip()]
                
                if lines:
                    random.seed(seed)
                    file_path = random.choice(lines)
                    loaded_image = self._load_image_from_path(file_path)
                    if loaded_image is not None:
                        return (loaded_image, file_path)
            except Exception as e:
                print(f"SmartImageLoader: Error reading txt_path '{txt_path}': {e}")
        
        # Priorité 2 : img_path (chemin direct vers une image)
        if img_path and img_path.strip() and os.path.exists(img_path):
            try:
                loaded_image = self._load_image_from_path(img_path)
                if loaded_image is not None:
                    file_path = img_path
                    return (loaded_image, file_path)
            except Exception as e:
                print(f"SmartImageLoader: Error loading img_path '{img_path}': {e}")
        
        # Priorité 3 : img_directory (dossier avec images)
        if img_directory and img_directory.strip() and os.path.isdir(img_directory):
            try:
                valid_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.webp', '.tiff')
                image_files = [
                    os.path.join(img_directory, f) 
                    for f in os.listdir(img_directory) 
                    if f.lower().endswith(valid_extensions)
                ]
                
                if image_files:
                    random.seed(seed)
                    file_path = random.choice(image_files)
                    loaded_image = self._load_image_from_path(file_path)
                    if loaded_image is not None:
                        return (loaded_image, file_path)
            except Exception as e:
                print(f"SmartImageLoader: Error reading directory '{img_directory}': {e}")
        
        # Priorité 4 : image input directe
        if image is not None:
            file_path = "external_input"
            return (image, file_path)
        
        # Aucune source valide trouvée
        raise ValueError(
            "SmartImageLoader: No valid image source found. "
            "Please provide at least one of: txt_path, img_path, img_directory, or image input."
        )
    
    def _load_image_from_path(self, path):
        """
        Charge une image depuis un chemin et la convertit en tensor ComfyUI
        """
        try:
            img = Image.open(path)
            img = img.convert("RGB")
            img_array = np.array(img).astype(np.float32) / 255.0
            img_tensor = torch.from_numpy(img_array)[None,]
            return img_tensor
        except Exception as e:
            print(f"SmartImageLoader: Error loading image '{path}': {e}")
            return None

# Enregistrement du node
NODE_CLASS_MAPPINGS = {
    "SmartImageLoader": SmartImageLoader
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SmartImageLoader": "TOO Smart Image Loader"
}
