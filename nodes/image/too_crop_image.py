import os
import torch
import numpy as np
from PIL import Image

class TOOCropImage:
    """
    Interactive crop node with visual handles.
    Loads image from path and displays interactive crop box BEFORE workflow execution.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "img_path": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "tooltip": "Path to image file for cropping"
                }),
            },
            "optional": {
                "image": ("IMAGE", {
                    "tooltip": "Optional image input (overrides img_path)"
                }),
                "left": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 8192,
                    "step": 1,
                    "tooltip": "Pixels to crop from left edge"
                }),
                "right": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 8192,
                    "step": 1,
                    "tooltip": "Pixels to crop from right edge"
                }),
                "top": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 8192,
                    "step": 1,
                    "tooltip": "Pixels to crop from top edge"
                }),
                "bottom": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 8192,
                    "step": 1,
                    "tooltip": "Pixels to crop from bottom edge"
                }),
                "h_offset": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 8192,
                    "step": 1,
                    "tooltip": "Shift crop window horizontally"
                }),
                "v_offset": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 8192,
                    "step": 1,
                    "tooltip": "Shift crop window vertically"
                }),
            },
            "hidden": {}
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("IMAGE",)
    FUNCTION = "crop_image"
    CATEGORY = "🔵TOO-Pack/image"

    def crop_image(self, img_path="", image=None, left=0, right=0, top=0, bottom=0, h_offset=0, v_offset=0, extra_pnginfo=None):
        # Load image
        if image is not None:
            img_tensor = image
        elif img_path and img_path.strip() and os.path.exists(img_path):
            img_tensor = self._load_image_from_path(img_path)
            if img_tensor is None:
                raise ValueError(f"Failed to load image from '{img_path}'")
        else:
            raise ValueError("No valid image source. Provide either 'image' input or 'img_path'.")

        batch_size, img_height, img_width, channels = img_tensor.shape

        left = max(0, min(left, img_width - 1))
        right = max(0, min(right, img_width - 1))
        top = max(0, min(top, img_height - 1))
        bottom = max(0, min(bottom, img_height - 1))

        if left + right >= img_width:
            right = img_width - left - 1
        if top + bottom >= img_height:
            bottom = img_height - top - 1

        x1, x2 = left, img_width - right
        y1, y2 = top, img_height - bottom

        return (img_tensor[:, y1:y2, x1:x2, :],)

    def _load_image_from_path(self, path):
        """Load image from path and convert to ComfyUI tensor"""
        try:
            img = Image.open(path)
            img = img.convert("RGB")
            img_array = np.array(img).astype(np.float32) / 255.0
            img_tensor = torch.from_numpy(img_array)[None,]
            return img_tensor
        except Exception as e:
            print(f"TOOCropImage: Error loading image '{path}': {e}")
            return None


NODE_CLASS_MAPPINGS = {
    "TOOCropImage": TOOCropImage
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TOOCropImage": "✂️ TOO Crop Image"
}
