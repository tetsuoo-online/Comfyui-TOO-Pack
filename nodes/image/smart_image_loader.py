import os
import random
import torch
import numpy as np
from PIL import Image
import piexif
import piexif.helper
import re
import json

class SmartImageLoader:
    """
    Charge une image selon la priorité : image input > txt_path > img_path > img_directory
    - IMAGE output: priorité à l'entrée image, sinon chargée depuis les widgets
    - metadata/workflow: toujours extraits des fichiers (widgets)
    Retourne l'image + le chemin du fichier + metadata + workflow
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "img_dir_level": ("INT", {
                    "default": 0, 
                    "min": -1, 
                    "max": 10,
                    "tooltip": "Directory depth: -1=all subdirs, 0=current only, 1-10=levels deep"
                }),
                "show_preview": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Show image preview in the node"
                }),
            },
            "optional": {
                "txt_path": ("STRING", {"default": "", "multiline": False,
                "tooltip": "Path to a text file containing image paths (one per line)"
                }),
                "img_path": ("STRING", {"default": "", "multiline": False,
                "tooltip": "Direct path to an image file"
                }),
                "img_directory": ("STRING", {"default": "", "multiline": False,
                "tooltip": "Path to a directory containing images"
                }),
                "image": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING", "METADATA", "WORKFLOW")
    RETURN_NAMES = ("IMAGE", "FILE_PATH", "metadata", "workflow")
    FUNCTION = "load_smart"
    CATEGORY = "🔵TOO-Pack/image"

    def load_smart(self, seed, img_dir_level=0, show_preview=True, txt_path="", img_path="", img_directory="", image=None):
        """
        Charge une image selon l'ordre de priorité et extrait ses métadonnées et workflow.
        - IMAGE output: from image input (priority) or from widgets (txt_path/img_path/img_directory)
        - metadata/workflow output: always from widgets (if provided)
        """
        file_path = "none"
        loaded_image = None
        metadata = {}
        workflow = {}

        # Priorité 1 : txt_path (fichier texte avec liste de chemins)
        if txt_path and txt_path.strip() and os.path.exists(txt_path):
            try:
                with open(txt_path, 'r', encoding='utf-8') as f:
                    lines = [line.strip() for line in f.readlines() if line.strip()]
                if lines:
                    random.seed(seed)
                    file_path = random.choice(lines)
                    metadata = self._extract_metadata(file_path)
                    workflow = self._extract_workflow(file_path)
                    
                    # Load image from file only if no image input
                    if image is None:
                        loaded_image = self._load_image_from_path(file_path)
                        if loaded_image is not None:
                            return (loaded_image, file_path, metadata, workflow)
                    else:
                        # Use image input for IMAGE output
                        return (image, file_path, metadata, workflow)
            except Exception as e:
                print(f"SmartImageLoader: Error reading txt_path '{txt_path}': {e}")

        # Priorité 2 : img_path (chemin direct vers une image)
        if img_path and img_path.strip() and os.path.exists(img_path):
            try:
                file_path = img_path
                metadata = self._extract_metadata(file_path)
                workflow = self._extract_workflow(file_path)
                
                # Load image from file only if no image input
                if image is None:
                    loaded_image = self._load_image_from_path(img_path)
                    if loaded_image is not None:
                        return (loaded_image, file_path, metadata, workflow)
                else:
                    # Use image input for IMAGE output
                    return (image, file_path, metadata, workflow)
            except Exception as e:
                print(f"SmartImageLoader: Error loading img_path '{img_path}': {e}")

        # Priorité 3 : img_directory (dossier avec images)
        if img_directory and img_directory.strip() and os.path.isdir(img_directory):
            try:
                valid_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.webp', '.tiff')
                image_files = []

                if img_dir_level == -1:
                    # Tous les sous-dossiers
                    for root, dirs, files in os.walk(img_directory):
                        for f in files:
                            if f.lower().endswith(valid_extensions):
                                image_files.append(os.path.join(root, f))
                elif img_dir_level == 0:
                    # Dossier courant uniquement
                    image_files = [
                        os.path.join(img_directory, f)
                        for f in os.listdir(img_directory)
                        if f.lower().endswith(valid_extensions) and os.path.isfile(os.path.join(img_directory, f))
                    ]
                else:
                    # Profondeur spécifique
                    image_files = self._get_images_at_depth(img_directory, img_dir_level, valid_extensions)

                if image_files:
                    random.seed(seed)
                    file_path = random.choice(image_files)
                    metadata = self._extract_metadata(file_path)
                    workflow = self._extract_workflow(file_path)
                    
                    # Load image from file only if no image input
                    if image is None:
                        loaded_image = self._load_image_from_path(file_path)
                        if loaded_image is not None:
                            return (loaded_image, file_path, metadata, workflow)
                    else:
                        # Use image input for IMAGE output
                        return (image, file_path, metadata, workflow)
            except Exception as e:
                print(f"SmartImageLoader: Error reading directory '{img_directory}': {e}")

        # Priorité 4 : image input directe (si aucun widget n'a fourni de métadonnées)
        if image is not None:
            file_path = "external_input"
            return (image, file_path, metadata, workflow)

        # Aucune source valide trouvée
        raise ValueError(
            "SmartImageLoader: No valid image source found. "
            "Please provide at least one of: image input, txt_path, img_path or img_directory."
        )

    def _get_images_at_depth(self, directory, max_depth, valid_extensions):
        """Récupère les images jusqu'à une profondeur spécifique"""
        image_files = []

        def scan_directory(current_dir, current_depth):
            if current_depth > max_depth:
                return

            try:
                for item in os.listdir(current_dir):
                    item_path = os.path.join(current_dir, item)
                    if os.path.isfile(item_path) and item.lower().endswith(valid_extensions):
                        image_files.append(item_path)
                    elif os.path.isdir(item_path) and current_depth < max_depth:
                        scan_directory(item_path, current_depth + 1)
            except Exception as e:
                print(f"SmartImageLoader: Error scanning '{current_dir}': {e}")

        scan_directory(directory, 0)
        return image_files

    def _extract_metadata(self, filepath):
        """
        Extrait les métadonnées A1111/Civitai depuis l'image
        PNG: depuis le chunk "parameters"
        JPEG/WEBP: depuis l'EXIF UserComment
        """
        metadata = {
            "model_name": "",
            "model_hash": "",
            "lora_hashes": {},
            "positive": "",
            "negative": "",
            "seed": "",
            "steps": "",
            "cfg": "",
            "sampler_name": "",
            "scheduler": "",
            "custom": ""
        }

        try:
            # Détecter le format
            ext = os.path.splitext(filepath)[1].lower()
            
            if ext == '.png':
                # Pour PNG, lire le chunk "parameters"
                try:
                    img = Image.open(filepath)
                    if hasattr(img, 'info') and 'parameters' in img.info:
                        user_comment = img.info['parameters']
                        metadata = self._parse_a111_params(user_comment)
                except Exception as e:
                    print(f"SmartImageLoader: No PNG metadata found in '{filepath}': {e}")
            else:
                # Pour JPEG/WEBP, utiliser EXIF
                try:
                    exif_dict = piexif.load(filepath)
                    
                    # Chercher dans ExifIFD.UserComment
                    if "Exif" in exif_dict and piexif.ExifIFD.UserComment in exif_dict["Exif"]:
                        user_comment_raw = exif_dict["Exif"][piexif.ExifIFD.UserComment]
                        
                        try:
                            # Décoder UserComment
                            user_comment = piexif.helper.UserComment.load(user_comment_raw)
                            metadata = self._parse_a111_params(user_comment)
                        except Exception as e:
                            print(f"SmartImageLoader: Error decoding UserComment: {e}")
                except Exception as e:
                    print(f"SmartImageLoader: No EXIF metadata found in '{filepath}': {e}")
            
        except Exception as e:
            print(f"SmartImageLoader: Error reading metadata from '{filepath}': {e}")
        
        return metadata

    def _extract_workflow(self, filepath):
        """
        Extrait le workflow ComfyUI depuis l'image
        PNG: depuis les chunks "workflow" et "prompt"
        JPEG/WEBP: depuis les tags EXIF Make/Model
        """
        workflow = {}

        try:
            # Détecter le format
            ext = os.path.splitext(filepath)[1].lower()
            
            if ext == '.png':
                # Pour PNG, lire les chunks
                try:
                    img = Image.open(filepath)
                    if hasattr(img, 'info'):
                        extra_pnginfo = {}
                        prompt = None
                        
                        for key, value in img.info.items():
                            if key == "prompt":
                                try:
                                    prompt = json.loads(value)
                                except:
                                    pass
                            elif key != "parameters":  # Ignorer "parameters" qui contient les métadonnées A1111
                                try:
                                    extra_pnginfo[key] = json.loads(value)
                                except:
                                    extra_pnginfo[key] = value
                        
                        if extra_pnginfo:
                            workflow["extra_pnginfo"] = extra_pnginfo
                        if prompt:
                            workflow["prompt"] = prompt
                except Exception as e:
                    print(f"SmartImageLoader: No PNG workflow found in '{filepath}': {e}")
            else:
                # Pour JPEG/WEBP, utiliser EXIF
                try:
                    exif_dict = piexif.load(filepath)
                    
                    if "0th" in exif_dict:
                        # Reconstituer extra_pnginfo et prompt
                        extra_pnginfo = {}
                        prompt = None
                        
                        for tag, value in exif_dict["0th"].items():
                            if isinstance(value, bytes):
                                value = value.decode('utf-8', errors='ignore')
                            
                            # Parser les tags au format "key:json"
                            if isinstance(value, str) and ':' in value:
                                key, json_str = value.split(':', 1)
                                try:
                                    parsed = json.loads(json_str)
                                    if key == "prompt":
                                        prompt = parsed
                                    else:
                                        extra_pnginfo[key] = parsed
                                except:
                                    pass
                        
                        if extra_pnginfo:
                            workflow["extra_pnginfo"] = extra_pnginfo
                        if prompt:
                            workflow["prompt"] = prompt
                except Exception as e:
                    print(f"SmartImageLoader: No EXIF workflow found in '{filepath}': {e}")
                    
        except Exception as e:
            print(f"SmartImageLoader: Error reading workflow from '{filepath}': {e}")
        
        return workflow

    def _parse_a111_params(self, params_text):
        """
        Parse les paramètres au format A1111/Civitai.
        Format attendu:
        {positive}
        Negative prompt: {negative}
        Steps: X, Sampler: Y Z, CFG scale: X, Seed: X, Size: WxH, Model hash: X, Model: X, Lora hashes: "name: hash"
        """
        metadata = {
            "model_name": "",
            "model_hash": "",
            "lora_hashes": {},
            "positive": "",
            "negative": "",
            "seed": "",
            "steps": "",
            "cfg": "",
            "sampler_name": "",
            "scheduler": "",
            "custom": ""
        }

        if not params_text:
            return metadata

        lines = params_text.split('\n')
        
        # Trouver les indices des sections
        negative_idx = -1
        params_idx = -1
        
        for i, line in enumerate(lines):
            if line.startswith("Negative prompt:"):
                negative_idx = i
            elif "Steps:" in line:
                params_idx = i
                break
        
        # Extraire positive prompt (toutes les lignes avant "Negative prompt:" ou params)
        if negative_idx != -1:
            positive_lines = lines[:negative_idx]
        elif params_idx != -1:
            positive_lines = lines[:params_idx]
        else:
            positive_lines = lines
        
        # Joindre avec des espaces et nettoyer
        metadata["positive"] = ' '.join(positive_lines).strip()
        
        # Extraire negative prompt (entre "Negative prompt:" et params)
        if negative_idx != -1:
            if params_idx != -1:
                negative_lines = lines[negative_idx:params_idx]
            else:
                negative_lines = lines[negative_idx:]
            
            # Retirer le préfixe "Negative prompt:" de la première ligne
            if negative_lines:
                first_line = negative_lines[0]
                if first_line.startswith("Negative prompt:"):
                    negative_lines[0] = first_line.replace("Negative prompt:", "", 1).strip()
                
                # Joindre avec des espaces
                metadata["negative"] = ' '.join(negative_lines).strip()
        
        # Parser la ligne de paramètres
        if params_idx != -1:
            params_line = lines[params_idx]
            
            # Steps
            match = re.search(r"Steps:\s*(\d+)", params_line)
            if match:
                metadata["steps"] = match.group(1)
            
            # Sampler (format: "Sampler: name scheduler")
            match = re.search(r"Sampler:\s*([^\s,]+)(?:\s+([^\s,]+))?", params_line)
            if match:
                metadata["sampler_name"] = match.group(1)
                if match.group(2):
                    metadata["scheduler"] = match.group(2)
            
            # CFG scale
            match = re.search(r"CFG scale:\s*([\d.]+)", params_line)
            if match:
                metadata["cfg"] = match.group(1)
            
            # Seed
            match = re.search(r"Seed:\s*(\d+)", params_line)
            if match:
                metadata["seed"] = match.group(1)
            
            # Model hash
            match = re.search(r"Model hash:\s*([a-fA-F0-9]+)", params_line)
            if match:
                metadata["model_hash"] = match.group(1)
            
            # Model name
            match = re.search(r"Model:\s*([^,]+?)(?:,|$)", params_line)
            if match:
                metadata["model_name"] = match.group(1).strip()
            
            # Lora hashes (format: Lora hashes: "name1: hash1, name2: hash2")
            match = re.search(r'Lora hashes:\s*"([^"]+)"', params_line)
            if match:
                lora_str = match.group(1)
                lora_pairs = lora_str.split(',')
                for pair in lora_pairs:
                    if ':' in pair:
                        name, hash_val = pair.split(':', 1)
                        metadata["lora_hashes"][name.strip()] = hash_val.strip()

        return metadata

    def _load_image_from_path(self, path):
        """Charge une image depuis un chemin et la convertit en tensor ComfyUI"""
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
    "SmartImageLoader": "TOO Smart Image Loader 🖼️"
}