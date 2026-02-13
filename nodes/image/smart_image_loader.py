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
    Charge une image selon la priorité : txt_path > img_path > img_directory > image input
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
                "txt_path": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "tooltip": "Path to a text file containing image paths (one per line)"
                }),
                "img_path": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "vhs_path_extensions": ['png', 'jpg', 'jpeg', 'bmp', 'webp', 'tiff'],
                    "tooltip": "Direct path to an image file"
                }),
                "img_directory": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "vhs_path_extensions": [''],
                    "tooltip": "Path to a directory containing images"
                }),
                "image": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("IMAGE", "file_path", "metadata", "workflow")
    FUNCTION = "load_smart"
    CATEGORY = "🔵TOO-Pack/image"

    def load_smart(self, seed, img_dir_level=0, show_preview=True, txt_path="", img_path="", img_directory="", image=None):
        """Charge une image selon l'ordre de priorité"""
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
                        metadata = self._extract_metadata(file_path)
                        workflow = self._extract_workflow(file_path)
                        return (loaded_image, file_path, json.dumps(metadata, indent=2), json.dumps(workflow, indent=2))
            except Exception as e:
                print(f"SmartImageLoader: Error reading txt_path '{txt_path}': {e}")

        # Priorité 2 : img_path (chemin direct vers une image)
        if img_path and img_path.strip() and os.path.exists(img_path):
            try:
                loaded_image = self._load_image_from_path(img_path)
                if loaded_image is not None:
                    file_path = img_path
                    metadata = self._extract_metadata(file_path)
                    workflow = self._extract_workflow(file_path)
                    return (loaded_image, file_path, json.dumps(metadata, indent=2), json.dumps(workflow, indent=2))
            except Exception as e:
                print(f"SmartImageLoader: Error loading img_path '{img_path}': {e}")

        # Priorité 3 : img_directory (dossier avec images)
        if img_directory and img_directory.strip() and os.path.isdir(img_directory):
            try:
                valid_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.webp', '.tiff')
                image_files = []

                if img_dir_level == -1:
                    for root, dirs, files in os.walk(img_directory):
                        for f in files:
                            if f.lower().endswith(valid_extensions):
                                image_files.append(os.path.join(root, f))
                elif img_dir_level == 0:
                    image_files = [
                        os.path.join(img_directory, f)
                        for f in os.listdir(img_directory)
                        if f.lower().endswith(valid_extensions) and os.path.isfile(os.path.join(img_directory, f))
                    ]
                else:
                    image_files = self._get_images_at_depth(img_directory, img_dir_level, valid_extensions)

                if image_files:
                    random.seed(seed)
                    file_path = random.choice(image_files)
                    loaded_image = self._load_image_from_path(file_path)
                    if loaded_image is not None:
                        metadata = self._extract_metadata(file_path)
                        workflow = self._extract_workflow(file_path)
                        return (loaded_image, file_path, json.dumps(metadata, indent=2), json.dumps(workflow, indent=2))
            except Exception as e:
                print(f"SmartImageLoader: Error reading directory '{img_directory}': {e}")

        # Priorité 4 : image input directe
        if image is not None:
            file_path = "external_input"
            return (image, file_path, "{}", "{}")

        # Aucune source valide trouvée
        raise ValueError(
            "SmartImageLoader: No valid image source found. "
            "Please provide at least one of: txt_path, img_path, img_directory, or image input."
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
        """Extrait les métadonnées A1111/Civitai depuis l'image"""
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
        }

        try:
            ext = os.path.splitext(filepath)[1].lower()
            if ext == '.png':
                try:
                    img = Image.open(filepath)
                    if hasattr(img, 'info') and 'parameters' in img.info:
                        user_comment = img.info['parameters']
                        metadata = self._parse_a111_params(user_comment)
                except:
                    pass
            else:
                try:
                    exif_dict = piexif.load(filepath)
                    if "Exif" in exif_dict and piexif.ExifIFD.UserComment in exif_dict["Exif"]:
                        user_comment_raw = exif_dict["Exif"][piexif.ExifIFD.UserComment]
                        user_comment = piexif.helper.UserComment.load(user_comment_raw)
                        metadata = self._parse_a111_params(user_comment)
                except:
                    pass
        except:
            pass

        return metadata

    def _extract_workflow(self, filepath):
        """Extrait le workflow ComfyUI depuis l'image"""
        workflow = {}

        try:
            ext = os.path.splitext(filepath)[1].lower()
            if ext == '.png':
                try:
                    img = Image.open(filepath)
                    if hasattr(img, 'info'):
                        for key, value in img.info.items():
                            if key == "prompt":
                                try:
                                    workflow["prompt"] = json.loads(value)
                                except:
                                    pass
                            elif key != "parameters":
                                try:
                                    workflow[key] = json.loads(value)
                                except:
                                    workflow[key] = value
                except:
                    pass
        except:
            pass

        return workflow

    def _parse_a111_params(self, params_text):
        """Parse les paramètres au format A1111/Civitai"""
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
        }

        if not params_text:
            return metadata

        lines = params_text.split('\n')
        negative_idx = params_idx = -1

        for i, line in enumerate(lines):
            if line.startswith("Negative prompt:"):
                negative_idx = i
            elif "Steps:" in line:
                params_idx = i
                break

        # Positive prompt
        if negative_idx != -1:
            positive_lines = lines[:negative_idx]
        elif params_idx != -1:
            positive_lines = lines[:params_idx]
        else:
            positive_lines = lines
        metadata["positive"] = ' '.join(positive_lines).strip()

        # Negative prompt
        if negative_idx != -1:
            negative_lines = lines[negative_idx:params_idx] if params_idx != -1 else lines[negative_idx:]
            if negative_lines:
                first = negative_lines[0]
                if first.startswith("Negative prompt:"):
                    negative_lines[0] = first.replace("Negative prompt:", "", 1).strip()
            metadata["negative"] = ' '.join(negative_lines).strip()

        # Parameters
        if params_idx != -1:
            params_line = lines[params_idx]

            m = re.search(r"Steps:\s*(\d+)", params_line)
            if m: metadata["steps"] = m.group(1)

            m = re.search(r"Sampler:\s*([^\s,]+)(?:\s+([^\s,]+))?", params_line)
            if m:
                metadata["sampler_name"] = m.group(1)
                if m.group(2): metadata["scheduler"] = m.group(2)

            m = re.search(r"CFG scale:\s*([\d.]+)", params_line)
            if m: metadata["cfg"] = m.group(1)

            m = re.search(r"Seed:\s*(\d+)", params_line)
            if m: metadata["seed"] = m.group(1)

            m = re.search(r"Model hash:\s*([a-fA-F0-9]+)", params_line)
            if m: metadata["model_hash"] = m.group(1)

            m = re.search(r"Model:\s*([^,]+?)(?:,|$)", params_line)
            if m: metadata["model_name"] = m.group(1).strip()

            m = re.search(r'Lora hashes:\s*"([^"]+)"', params_line)
            if m:
                lora_str = m.group(1)
                for pair in lora_str.split(','):
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

NODE_CLASS_MAPPINGS = {
    "SmartImageLoader": SmartImageLoader
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SmartImageLoader": "TOO Smart Image Loader"
}
