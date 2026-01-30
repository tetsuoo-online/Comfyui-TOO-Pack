"""
ComfyUI Node: Load Images from URL
Loads images and their alpha masks from URLs
"""

import requests
from PIL import Image
from io import BytesIO
import torch
import numpy as np


def pil2tensor(image):
    """Convert PIL Image to tensor"""
    return torch.from_numpy(np.array(image).astype(np.float32) / 255.0).unsqueeze(0)


def load_image_and_mask_from_url(url, timeout=10):
    """Load image and extract alpha mask from URL"""
    response = requests.get(url, timeout=timeout)
    content_type = response.headers.get('Content-Type')
    
    image = Image.open(BytesIO(response.content))
    # Create a mask from the image's alpha channel
    mask = image.convert('RGBA').split()[-1]
    # Convert the mask to a black and white image
    mask = mask.convert('L')
    image = image.convert('RGB')
    return (image, mask)


class LoadImagesFromURL:
    """Load multiple images from URLs with caching"""
    
    # Global cache for loaded images
    _cache = {}
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": { 
                "url": ("STRING", {
                    "multiline": True,
                    "default": "https://",
                    "dynamicPrompts": False
                }),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "MASK",)
    RETURN_NAMES = ("images", "masks",)
    FUNCTION = "load_images"
    CATEGORY = "🔵TOO-Pack/mixlab"
    INPUT_IS_LIST = False
    OUTPUT_IS_LIST = (True, True,)
    
    def load_images(self, url):
        """Load images from newline-separated URLs"""
        
        def filter_http_urls(urls):
            """Extract valid HTTP/HTTPS URLs"""
            filtered_urls = []
            for u in urls.split('\n'):
                u = u.strip()
                if u.startswith('http'):
                    filtered_urls.append(u)
            return filtered_urls
        
        filtered_urls = filter_http_urls(url)
        images = []
        masks = []
        
        for img_url in filtered_urls:
            try:
                # Check cache first
                if img_url in self._cache:
                    img, mask = self._cache[img_url]
                else:
                    # Load from URL and cache
                    img, mask = load_image_and_mask_from_url(img_url)
                    self._cache[img_url] = (img, mask)
                
                # Convert to tensors
                img_tensor = pil2tensor(img)
                mask_tensor = pil2tensor(mask)
                
                images.append(img_tensor)
                masks.append(mask_tensor)
                
            except Exception as e:
                print(f"Error loading image from {img_url}: {str(e)}")
        
        return (images, masks,)


# Node registration
NODE_CLASS_MAPPINGS = {
    "LoadImagesFromURL": LoadImagesFromURL
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LoadImagesFromURL": "Load Images from URL"
}