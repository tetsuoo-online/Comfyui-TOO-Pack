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
    Returns image + mask (alpha if available, else white) + metadata + workflow
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

    RETURN_TYPES = ("IMAGE", "MASK", "METADATA", "WORKFLOW")
    RETURN_NAMES = ("IMAGE", "MASK", "metadata", "workflow")
    FUNCTION = "load_simple"
    CATEGORY = "🔵TOO-Pack/image"

    def load_simple(self, show_preview=True, img_path="", image=None):
        """
        Load an image from image input or img_path.
        - IMAGE output: from image input (priority) or img_path
        - MASK output: alpha channel if available, else white mask
        - metadata/workflow output: always from img_path (if provided)
        """
        loaded_image = None
        metadata = {}
        workflow = {}

        # Extract metadata and workflow from img_path (if provided)
        if img_path and img_path.strip() and os.path.exists(img_path):
            metadata = self._extract_metadata(img_path)
            workflow = self._extract_workflow(img_path)

            # If no image input, load the image from img_path
            if image is None:
                try:
                    loaded_image, mask = self._load_image_from_path(img_path)
                    if loaded_image is not None:
                        return (loaded_image, mask, metadata, workflow)
                except Exception as e:
                    raise ValueError(f"TOOSimpleImageLoader: Failed to load image from '{img_path}': {e}")

        # Use image input if provided
        if image is not None:
            mask = self._white_mask(image)
            return (image, mask, metadata, workflow)

        # No valid source found
        raise ValueError(
            "TOOSimpleImageLoader: No valid image source found. "
            "Please provide either image input or img_path."
        )

    def _white_mask(self, image_tensor):
        """Returns a white mask (all ones) matching image dimensions — shape [B, H, W]"""
        return torch.ones(image_tensor.shape[0], image_tensor.shape[1], image_tensor.shape[2])

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
            ext = os.path.splitext(filepath)[1].lower()

            if ext == '.png':
                try:
                    img = Image.open(filepath)
                    if hasattr(img, 'info') and 'parameters' in img.info:
                        metadata = self._parse_a111_params(img.info['parameters'])
                except Exception as e:
                    print(f"TOOSimpleImageLoader: No PNG metadata found in '{filepath}': {e}")
            else:
                try:
                    exif_dict = piexif.load(filepath)
                    if "Exif" in exif_dict and piexif.ExifIFD.UserComment in exif_dict["Exif"]:
                        user_comment_raw = exif_dict["Exif"][piexif.ExifIFD.UserComment]
                        try:
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
            ext = os.path.splitext(filepath)[1].lower()

            if ext == '.png':
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
                            elif key != "parameters":
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
                try:
                    exif_dict = piexif.load(filepath)
                    if "0th" in exif_dict:
                        extra_pnginfo = {}
                        prompt = None

                        for tag, value in exif_dict["0th"].items():
                            if isinstance(value, bytes):
                                value = value.decode('utf-8', errors='ignore')
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

        negative_idx = -1
        params_idx = -1

        for i, line in enumerate(lines):
            if line.startswith("Negative prompt:"):
                negative_idx = i
            elif "Steps:" in line:
                params_idx = i
                break

        if negative_idx != -1:
            positive_lines = lines[:negative_idx]
        elif params_idx != -1:
            positive_lines = lines[:params_idx]
        else:
            positive_lines = lines

        metadata["positive"] = ' '.join(positive_lines).strip()

        if negative_idx != -1:
            if params_idx != -1:
                negative_lines = lines[negative_idx:params_idx]
            else:
                negative_lines = lines[negative_idx:]

            if negative_lines:
                first_line = negative_lines[0]
                if first_line.startswith("Negative prompt:"):
                    negative_lines[0] = first_line.replace("Negative prompt:", "", 1).strip()
                metadata["negative"] = ' '.join(negative_lines).strip()

        if params_idx != -1:
            params_line = lines[params_idx]

            match = re.search(r"Steps:\s*(\d+)", params_line)
            if match:
                metadata["steps"] = match.group(1)

            match = re.search(r"Sampler:\s*([^\s,]+)(?:\s+([^\s,]+))?", params_line)
            if match:
                metadata["sampler_name"] = match.group(1)
                if match.group(2):
                    metadata["scheduler"] = match.group(2)

            match = re.search(r"CFG scale:\s*([\d.]+)", params_line)
            if match:
                metadata["cfg"] = match.group(1)

            match = re.search(r"Seed:\s*(\d+)", params_line)
            if match:
                metadata["seed"] = match.group(1)

            match = re.search(r"Model hash:\s*([a-fA-F0-9]+)", params_line)
            if match:
                metadata["model_hash"] = match.group(1)

            match = re.search(r"Model:\s*([^,]+?)(?:,|$)", params_line)
            if match:
                metadata["model_name"] = match.group(1).strip()

            match = re.search(r'Lora hashes:\s*"([^"]+)"', params_line)
            if match:
                lora_str = match.group(1)
                for pair in lora_str.split(','):
                    if ':' in pair:
                        name, hash_val = pair.split(':', 1)
                        metadata["lora_hashes"][name.strip()] = hash_val.strip()

        return metadata

    def _load_image_from_path(self, path):
        """Load image from path, return (image_tensor, mask_tensor).
        Extracts alpha channel if present, otherwise returns white mask.
        mask convention: 1.0 = masked (transparent), 0.0 = visible (opaque)
        """
        try:
            img = Image.open(path)

            if img.mode == "RGBA":
                img_array = np.array(img).astype(np.float32) / 255.0
                img_tensor = torch.from_numpy(img_array[:, :, :3])[None,]
                # Alpha: 0=transparent → 1.0 masked, 1=opaque → 0.0 masked
                mask_tensor = torch.from_numpy(1.0 - img_array[:, :, 3])[None,]
            else:
                img = img.convert("RGB")
                img_array = np.array(img).astype(np.float32) / 255.0
                img_tensor = torch.from_numpy(img_array)[None,]
                mask_tensor = torch.zeros(1, img_array.shape[0], img_array.shape[1])

            return img_tensor, mask_tensor

        except Exception as e:
            print(f"TOOSimpleImageLoader: Error loading image '{path}': {e}")
            return None, None


NODE_CLASS_MAPPINGS = {
    "TOOSimpleImageLoader": TOOSimpleImageLoader
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TOOSimpleImageLoader": "TOO Simple Image Loader 🖼️"
}
