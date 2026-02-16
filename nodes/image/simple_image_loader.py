import os
import torch
import numpy as np
from PIL import Image
import piexif
import piexif.helper
import re
import json

class TOOSimpleImageLoader:
    """
    Simple image loader: loads from img_path or image input
    Returns image + file path + metadata + workflow
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "show_preview": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Show image preview in the node"
                }),
            },
            "optional": {
                "img_path": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "vhs_path_extensions": ['png', 'jpg', 'jpeg', 'bmp', 'webp', 'tiff'],
                    "tooltip": "Direct path to an image file"
                }),
                "image": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING", "METADATA", "WORKFLOW")
    RETURN_NAMES = ("IMAGE", "FILE_PATH", "metadata", "workflow")
    FUNCTION = "load_simple"
    CATEGORY = "🔵TOO-Pack/image"

    def load_simple(self, show_preview=True, img_path="", image=None):
        """
        Load an image from image input or img_path.
        - IMAGE output: from image input (priority) or img_path
        - metadata/workflow output: always from img_path (if provided)
        """
        file_path = "none"
        loaded_image = None
        metadata = {}
        workflow = {}

        # Extract metadata and workflow from img_path (if provided)
        if img_path and img_path.strip() and os.path.exists(img_path):
            file_path = img_path
            metadata = self._extract_metadata(file_path)
            workflow = self._extract_workflow(file_path)
            
            # If no image input, load the image from img_path
            if image is None:
                try:
                    loaded_image = self._load_image_from_path(img_path)
                    if loaded_image is not None:
                        return (loaded_image, file_path, metadata, workflow)
                except Exception as e:
                    print(f"TOOSimpleImageLoader: Error loading img_path '{img_path}': {e}")
                    raise ValueError(f"TOOSimpleImageLoader: Failed to load image from '{img_path}': {e}")

        # Use image input if provided
        if image is not None:
            # If img_path was provided, file_path is already set and metadata/workflow extracted
            # Otherwise, file_path remains "external_input" and metadata/workflow are empty
            if file_path == "none":
                file_path = "external_input"
            return (image, file_path, metadata, workflow)

        # No valid source found
        raise ValueError(
            "TOOSimpleImageLoader: No valid image source found. "
            "Please provide either image input or img_path."
        )

    def _extract_metadata(self, filepath):
        """
        Extract A1111/Civitai metadata from image
        PNG: from "parameters" chunk
        JPEG/WEBP: from EXIF UserComment
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
            # Detect format
            ext = os.path.splitext(filepath)[1].lower()
            
            if ext == '.png':
                # For PNG, read "parameters" chunk
                try:
                    img = Image.open(filepath)
                    if hasattr(img, 'info') and 'parameters' in img.info:
                        user_comment = img.info['parameters']
                        metadata = self._parse_a111_params(user_comment)
                except Exception as e:
                    print(f"TOOSimpleImageLoader: No PNG metadata found in '{filepath}': {e}")
            else:
                # For JPEG/WEBP, use EXIF
                try:
                    exif_dict = piexif.load(filepath)
                    
                    # Look in ExifIFD.UserComment
                    if "Exif" in exif_dict and piexif.ExifIFD.UserComment in exif_dict["Exif"]:
                        user_comment_raw = exif_dict["Exif"][piexif.ExifIFD.UserComment]
                        
                        try:
                            # Decode UserComment
                            user_comment = piexif.helper.UserComment.load(user_comment_raw)
                            metadata = self._parse_a111_params(user_comment)
                        except Exception as e:
                            print(f"TOOSimpleImageLoader: Error decoding UserComment: {e}")
                except Exception as e:
                    print(f"TOOSimpleImageLoader: No EXIF metadata found in '{filepath}': {e}")
                    
        except Exception as e:
            print(f"TOOSimpleImageLoader: Error reading metadata from '{filepath}': {e}")
        
        return metadata

    def _extract_workflow(self, filepath):
        """
        Extract ComfyUI workflow from image
        PNG: from PNG chunks (prompt, workflow, etc.)
        JPEG/WEBP: from EXIF Make/Model tags
        """
        workflow = {}

        try:
            # Detect format
            ext = os.path.splitext(filepath)[1].lower()
            
            if ext == '.png':
                # For PNG, read all chunks except "parameters"
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
                            elif key != "parameters":  # Ignore "parameters" which contains A1111 metadata
                                try:
                                    extra_pnginfo[key] = json.loads(value)
                                except:
                                    extra_pnginfo[key] = value
                        
                        if extra_pnginfo:
                            workflow["extra_pnginfo"] = extra_pnginfo
                        if prompt:
                            workflow["prompt"] = prompt
                except Exception as e:
                    print(f"TOOSimpleImageLoader: No PNG workflow found in '{filepath}': {e}")
            else:
                # For JPEG/WEBP, use EXIF
                try:
                    exif_dict = piexif.load(filepath)
                    
                    if "0th" in exif_dict:
                        # Reconstruct extra_pnginfo and prompt
                        extra_pnginfo = {}
                        prompt = None
                        
                        for tag, value in exif_dict["0th"].items():
                            if isinstance(value, bytes):
                                value = value.decode('utf-8', errors='ignore')
                            
                            # Parse tags in "key:json" format
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
                    print(f"TOOSimpleImageLoader: No EXIF workflow found in '{filepath}': {e}")
                    
        except Exception as e:
            print(f"TOOSimpleImageLoader: Error reading workflow from '{filepath}': {e}")
        
        return workflow

    def _parse_a111_params(self, params_text):
        """
        Parse A1111/Civitai format parameters.
        Expected format:
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
        
        # Find section indices
        negative_idx = -1
        params_idx = -1
        
        for i, line in enumerate(lines):
            if line.startswith("Negative prompt:"):
                negative_idx = i
            elif "Steps:" in line:
                params_idx = i
                break
        
        # Extract positive prompt (all lines before "Negative prompt:" or params)
        if negative_idx != -1:
            positive_lines = lines[:negative_idx]
        elif params_idx != -1:
            positive_lines = lines[:params_idx]
        else:
            positive_lines = lines
        
        # Join with spaces and clean
        metadata["positive"] = ' '.join(positive_lines).strip()
        
        # Extract negative prompt (between "Negative prompt:" and params)
        if negative_idx != -1:
            if params_idx != -1:
                negative_lines = lines[negative_idx:params_idx]
            else:
                negative_lines = lines[negative_idx:]
            
            # Remove "Negative prompt:" prefix from first line
            if negative_lines:
                first_line = negative_lines[0]
                if first_line.startswith("Negative prompt:"):
                    negative_lines[0] = first_line.replace("Negative prompt:", "", 1).strip()
                
                # Join with spaces
                metadata["negative"] = ' '.join(negative_lines).strip()
        
        # Parse parameters line
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
        """Load an image from path and convert to ComfyUI tensor"""
        try:
            img = Image.open(path)
            img = img.convert("RGB")
            img_array = np.array(img).astype(np.float32) / 255.0
            img_tensor = torch.from_numpy(img_array)[None,]
            return img_tensor
        except Exception as e:
            print(f"TOOSimpleImageLoader: Error loading image '{path}': {e}")
            return None

NODE_CLASS_MAPPINGS = {
    "TOOSimpleImageLoader": TOOSimpleImageLoader
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TOOSimpleImageLoader": "TOO Simple Image Loader 🖼️"
}
