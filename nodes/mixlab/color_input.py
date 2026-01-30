"""
ComfyUI Node: Color Input
Provides a color picker widget that outputs color values
"""

class ColorInput:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": { 
                "color": ("TOO_COLOR", {"default": {"hex": "#20A0B0", "r": 32, "g": 160, "b": 176, "a": 1.0}}), 
            },
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING",)
    RETURN_NAMES = ("hex", "r", "g", "b", "a",)
    FUNCTION = "run"
    CATEGORY = "🔵TOO-Pack/mixlab"
    INPUT_IS_LIST = False
    OUTPUT_IS_LIST = (False, False, False, False, False,)
    
    def run(self, color):
        # DEBUG: voir ce qu'on reçoit
        print(f"[ColorInput] Type reçu: {type(color)}")
        print(f"[ColorInput] Valeur reçue: {color}")
        
        # Handle if color is a string (shouldn't happen but just in case)
        if isinstance(color, str):
            # Parse hex string to RGB
            hex_color = color.lstrip('#')
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            return (color, r, g, b, 1.0)
        
        # Handle dictionary
        h = str(color.get('hex', '#000000'))
        r = str(int(color.get('r', 0)))
        g = str(int(color.get('g', 0)))
        b = str(int(color.get('b', 0)))
        a = str(float(color.get('a', 1.0)))
        return (h, r, g, b, a,)


# Node registration
NODE_CLASS_MAPPINGS = {
    "ColorInput": ColorInput
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ColorInput": "Color Input"
}