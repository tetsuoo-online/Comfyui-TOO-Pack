"""
Krita Bridge Node for ComfyUI
Auto-loads the latest image from input/krita/ folder
"""

import os
import folder_paths
from PIL import Image
import numpy as np
import torch
import time


class KritaBridgeNode:
    """
    Node that automatically loads the latest image from input/krita/ folder.
    Checks for new files and updates automatically during generation.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
        }
    
    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("image", "mask")
    FUNCTION = "load_krita_image"
    CATEGORY = "🔵TOO-Pack/image"
    
    def __init__(self):
        self.last_file = None
        self.last_mtime = 0
        self.krita_folder = os.path.join(folder_paths.get_input_directory(), "krita")
        
        # Create krita folder if it doesn't exist
        if not os.path.exists(self.krita_folder):
            os.makedirs(self.krita_folder)
            print(f"KritaBridge: Created folder {self.krita_folder}")
    
    def load_krita_image(self):
        """Load the most recent image from input/krita/ folder"""
        
        # Get all PNG files in the krita folder
        png_files = [f for f in os.listdir(self.krita_folder) if f.endswith('.png')]
        
        if not png_files:
            # Return placeholder if no files
            print("KritaBridge: Waiting for images in input/krita/")
            empty = torch.zeros((1, 512, 512, 3))
            mask = torch.ones((1, 512, 512))
            return (empty, mask)
        
        # Get the most recent file
        latest_file = max(
            [os.path.join(self.krita_folder, f) for f in png_files],
            key=os.path.getmtime
        )
        
        latest_mtime = os.path.getmtime(latest_file)
        
        # Check if file has changed
        if self.last_file != latest_file or self.last_mtime != latest_mtime:
            self.last_file = latest_file
            self.last_mtime = latest_mtime
            print(f"KritaBridge: Loading {os.path.basename(latest_file)}")
        
        # Load the image
        img = Image.open(latest_file)
        
        # Extract alpha if present
        if img.mode == 'RGBA':
            alpha = np.array(img.split()[-1]).astype(np.float32) / 255.0
            img = img.convert('RGB')
        else:
            if img.mode != 'RGB':
                img = img.convert('RGB')
            alpha = np.ones((img.height, img.width), dtype=np.float32)
        
        # Convert to tensor
        img_array = np.array(img).astype(np.float32) / 255.0
        img_tensor = torch.from_numpy(img_array)[None,]
        
        # Convert mask to tensor
        mask_tensor = torch.from_numpy(alpha)[None,]
        
        return (img_tensor, mask_tensor)
    
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        """Force ComfyUI to check this node on every execution"""
        # Return current timestamp to force re-evaluation
        return float(time.time())


# Node registration
NODE_CLASS_MAPPINGS = {
    "KritaBridgeNode": KritaBridgeNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "KritaBridgeNode": "🎨 Krita Bridge"
}
