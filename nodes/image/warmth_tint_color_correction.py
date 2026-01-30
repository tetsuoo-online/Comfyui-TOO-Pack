"""
Custom Color Tint Node for ComfyUI
Applies a color tint using hex color input
"""

import torch
import numpy as np

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    print("⚠️ OpenCV not available. Install with: pip install opencv-python")


def hex_to_rgb(hex_color):
    """Convert hex color (#FF0013) to RGB tuple (0-1 range)"""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])
    try:
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        return (r, g, b)
    except:
        return None


class CustomColorTint:
    """
    Apply a custom color tint to images using hex color input.
    Blends the target color with the image based on intensity.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "color_hex": ("STRING", {
                    "default": "#FF6B35",
                    "description": "Hex color code (e.g., #FF0013, #3B82F6)"
                }),
                "intensity": ("FLOAT", {
                    "default": 0.3,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "description": "Tint intensity: 0=no effect, 1=full color"
                }),
                "blend_mode": (["overlay", "multiply", "screen", "soft_light", "color"],),
                "preserve_luminosity": ("BOOLEAN", {
                    "default": True,
                    "description": "Preserve original image brightness"
                }),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_tint"
    CATEGORY = "🔵TOO-Pack/image"
    
    def apply_tint(self, image, color_hex, intensity, blend_mode, preserve_luminosity):
        """
        Apply color tint to image using hex color.
        
        Args:
            image: Input image tensor (B, H, W, C) in RGB format, values [0, 1]
            color_hex: Hex color string (e.g., "#FF0013")
            intensity: Tint strength (0.0 to 1.0)
            blend_mode: How to blend the tint color
            preserve_luminosity: Keep original brightness
            
        Returns:
            Tinted image tensor
        """
        # Parse hex color
        rgb_color = hex_to_rgb(color_hex)
        if rgb_color is None:
            print(f"⚠️ Invalid hex color: {color_hex}. Using default.")
            rgb_color = (1.0, 0.42, 0.21)  # Default orange
        
        if intensity == 0.0:
            return (image,)
        
        # Process each image in batch
        batch_size = image.shape[0]
        height = image.shape[1]
        width = image.shape[2]
        
        processed_images = []
        
        for i in range(batch_size):
            single_image = image[i]
            
            # Create color layer
            color_layer = torch.ones_like(single_image)
            color_layer[:, :, 0] = rgb_color[0]
            color_layer[:, :, 1] = rgb_color[1]
            color_layer[:, :, 2] = rgb_color[2]
            
            # Apply blend mode
            if blend_mode == "multiply":
                result = single_image * color_layer
            elif blend_mode == "screen":
                result = 1 - (1 - single_image) * (1 - color_layer)
            elif blend_mode == "overlay":
                result = self._blend_overlay(single_image, color_layer)
            elif blend_mode == "soft_light":
                result = self._blend_soft_light(single_image, color_layer)
            elif blend_mode == "color":
                result = self._blend_color(single_image, color_layer)
            else:
                result = single_image * (1 - intensity) + color_layer * intensity
            
            # Blend with original based on intensity
            result = single_image * (1 - intensity) + result * intensity
            
            # Preserve luminosity if requested
            if preserve_luminosity and OPENCV_AVAILABLE:
                result = self._preserve_luminosity(single_image, result)
            
            result = torch.clamp(result, 0.0, 1.0)
            processed_images.append(result)
        
        result_batch = torch.stack(processed_images, dim=0)
        
        print(f"🎨 Applied color tint: {color_hex} (intensity: {intensity:.2f}, mode: {blend_mode})")
        
        return (result_batch,)
    
    def _blend_overlay(self, base, blend):
        """Overlay blend mode"""
        mask = base < 0.5
        result = torch.where(
            mask,
            2 * base * blend,
            1 - 2 * (1 - base) * (1 - blend)
        )
        return result
    
    def _blend_soft_light(self, base, blend):
        """Soft light blend mode"""
        result = (1 - 2 * blend) * base**2 + 2 * blend * base
        return result
    
    def _blend_color(self, base, blend):
        """Color blend mode (replaces hue and saturation)"""
        if not OPENCV_AVAILABLE:
            return blend
        
        # Convert to numpy for HSV processing
        base_np = (base.cpu().numpy() * 255).astype(np.uint8)
        blend_np = (blend.cpu().numpy() * 255).astype(np.uint8)
        
        base_hsv = cv2.cvtColor(base_np, cv2.COLOR_RGB2HSV)
        blend_hsv = cv2.cvtColor(blend_np, cv2.COLOR_RGB2HSV)
        
        # Keep base luminosity (V), use blend's hue and saturation
        result_hsv = blend_hsv.copy()
        result_hsv[:, :, 2] = base_hsv[:, :, 2]
        
        result_rgb = cv2.cvtColor(result_hsv, cv2.COLOR_HSV2RGB)
        result = torch.from_numpy(result_rgb.astype(np.float32) / 255.0).to(base.device)
        
        return result
    
    def _preserve_luminosity(self, original, tinted):
        """Preserve original image luminosity"""
        # Convert to numpy
        orig_np = (original.cpu().numpy() * 255).astype(np.uint8)
        tint_np = (tinted.cpu().numpy() * 255).astype(np.uint8)
        
        # Convert to LAB
        orig_lab = cv2.cvtColor(orig_np, cv2.COLOR_RGB2LAB)
        tint_lab = cv2.cvtColor(tint_np, cv2.COLOR_RGB2LAB)
        
        # Replace L channel with original
        tint_lab[:, :, 0] = orig_lab[:, :, 0]
        
        # Convert back
        result_rgb = cv2.cvtColor(tint_lab, cv2.COLOR_LAB2RGB)
        result = torch.from_numpy(result_rgb.astype(np.float32) / 255.0).to(original.device)
        
        return result


class WarmthTintColorCorrection:
    """
    Professional color temperature (warmth) and tint adjustment node.
    Uses LAB color space for accurate color corrections similar to Lightroom/Photoshop.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "warmth": ("FLOAT", {
                    "default": 0.0,
                    "min": -1.0,
                    "max": 1.0,
                    "step": 0.01,
                    "description": "Temperature: negative=cooler (blue), positive=warmer (yellow)"
                }),
                "tint": ("FLOAT", {
                    "default": 0.0,
                    "min": -1.0,
                    "max": 1.0,
                    "step": 0.01,
                    "description": "Tint: negative=green, positive=magenta"
                }),
                "temperature": ("FLOAT", {
                    "default": 0.0,
                    "min": -100.0,
                    "max": 100.0,
                    "step": 1.0,
                    "description": "Color temperature adjustment (Kelvin-style): negative=cooler, positive=warmer"
                }),
                "temperature_rgb": ("FLOAT", {
                    "default": 0.0,
                    "min": -100.0,
                    "max": 100.0,
                    "step": 1.0,
                    "description": "RGB temperature (for comparison): negative=cooler, positive=warmer"
                }),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "adjust_color"
    CATEGORY = "color/correction"
    
    def adjust_color(self, image, warmth, tint, temperature, temperature_rgb):
        """
        Apply warmth, tint and temperature adjustments using LAB color space.
        
        Args:
            image: Input image tensor (B, H, W, C) in RGB format, values [0, 1]
            warmth: Temperature adjustment (-1.0 to 1.0) - subtle control
            tint: Tint adjustment (-1.0 to 1.0) - green/magenta
            temperature: Color temperature (-100 to 100) - strong Kelvin-style control (LAB)
            temperature_rgb: Color temperature (-100 to 100) - RGB method
            
        Returns:
            Adjusted image tensor
        """
        if not OPENCV_AVAILABLE and (warmth != 0.0 or tint != 0.0 or temperature != 0.0):
            print("⚠️ OpenCV not available for LAB adjustments.")
            print("   Install with: pip install opencv-python")
            if temperature_rgb == 0.0:
                return (image,)
        
        # If no adjustment needed, return original
        if warmth == 0.0 and tint == 0.0 and temperature == 0.0 and temperature_rgb == 0.0:
            return (image,)
        
        # First apply RGB temperature if specified
        processed_image = image
        if temperature_rgb != 0.0:
            processed_image = self._apply_temperature_rgb(processed_image, temperature_rgb)
        
        # Then apply LAB adjustments if OpenCV is available
        if not OPENCV_AVAILABLE or (warmth == 0.0 and tint == 0.0 and temperature == 0.0):
            return (processed_image,)
        
        # Process each image in the batch
        batch_size = processed_image.shape[0]
        processed_images = []
        
        for i in range(batch_size):
            # Get single image and convert to numpy
            single_image = processed_image[i]
            image_np = (single_image.cpu().numpy() * 255).astype(np.uint8)
            
            try:
                # Convert RGB to LAB color space
                lab = cv2.cvtColor(image_np, cv2.COLOR_RGB2LAB).astype(np.float32)
                
                # Apply warmth adjustment to 'b' channel (blue-yellow axis)
                if warmth != 0.0:
                    # 'b' channel: 128 is neutral, <128 is blue, >128 is yellow
                    temperature_shift = warmth * 35  # Scale factor for visible effect
                    lab[:, :, 2] = np.clip(lab[:, :, 2] + temperature_shift, 0, 255)
                
                # Apply tint adjustment to 'a' channel (green-magenta axis)
                if tint != 0.0:
                    # 'a' channel: 128 is neutral, <128 is green, >128 is magenta
                    tint_shift = tint * 30  # Scale factor for visible effect
                    lab[:, :, 1] = np.clip(lab[:, :, 1] + tint_shift, 0, 255)
                
                # Apply temperature adjustment (Kelvin-style, stronger effect)
                if temperature != 0.0:
                    # Temperature affects both 'b' channel (primary) and 'a' channel (secondary)
                    temp_factor = temperature / 100.0  # Normalize to -1.0 to 1.0
                    
                    # Primary effect on b channel (blue-yellow)
                    b_shift = temp_factor * 50
                    lab[:, :, 2] = np.clip(lab[:, :, 2] + b_shift, 0, 255)
                    
                    # Secondary effect on a channel for more realistic color temperature
                    a_shift = temp_factor * 8
                    lab[:, :, 1] = np.clip(lab[:, :, 1] + a_shift, 0, 255)
                
                # Convert back to uint8 and then to RGB
                lab = lab.astype(np.uint8)
                color_corrected_rgb = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
                
                # Convert back to torch tensor
                processed_tensor = torch.from_numpy(
                    color_corrected_rgb.astype(np.float32) / 255.0
                ).to(processed_image.device)
                
                processed_images.append(processed_tensor)
                
            except Exception as e:
                print(f"⚠️ Color correction failed for image {i}: {e}")
                processed_images.append(single_image)
        
        # Stack batch back together
        result = torch.stack(processed_images, dim=0)
        result = torch.clamp(result, 0.0, 1.0)
        
        # Log adjustments
        adjustments = []
        if temperature_rgb != 0.0:
            adjustments.append(f"temperature_rgb: {temperature_rgb:.1f} ({'warmer' if temperature_rgb > 0 else 'cooler'})")
        if warmth != 0.0:
            adjustments.append(f"warmth: {warmth:.2f} ({'warmer' if warmth > 0 else 'cooler'})")
        if tint != 0.0:
            adjustments.append(f"tint: {tint:.2f} ({'magenta' if tint > 0 else 'green'})")
        if temperature != 0.0:
            adjustments.append(f"temperature: {temperature:.1f}K ({'warmer' if temperature > 0 else 'cooler'})")
        
        print(f"🌡️ Applied color adjustments: {', '.join(adjustments)}")
        
        return (result,)
    
    def _apply_temperature_rgb(self, image, temperature):
        """
        Apply temperature adjustment using RGB method.
        
        Args:
            image: Input image tensor (B, H, W, C) in RGB format, values [0, 1]
            temperature: Temperature adjustment (-100 to 100)
            
        Returns:
            Adjusted image tensor
        """
        result = image.clone()
        
        # Convert temperature to shift factor
        shift = (temperature / 100.0) * 0.5
        r_factor = 1.0 + shift
        b_factor = 1.0 - shift
        
        # Apply to R and B channels
        result[:, :, :, 0] = torch.clamp(result[:, :, :, 0] * r_factor, 0.0, 1.0)  # Red
        result[:, :, :, 2] = torch.clamp(result[:, :, :, 2] * b_factor, 0.0, 1.0)  # Blue
        
        return result


# Node registration
NODE_CLASS_MAPPINGS = {
    "CustomColorTint": CustomColorTint,
    "WarmthTintColorCorrection": WarmthTintColorCorrection
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CustomColorTint": "Custom Color Tint (Hex)",
    "WarmthTintColorCorrection": "Warmth & Tint Color Correction"
}
