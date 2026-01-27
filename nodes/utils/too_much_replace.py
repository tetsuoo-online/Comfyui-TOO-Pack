class TooMuchReplace:
    """
    Simple string replacement node with 5 rules.
    Replace input patterns with output values.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "string": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "tooltip": "Input string to process"
                }),
                "input_1": ("STRING", {
                    "default": "",
                    "tooltip": "Pattern to search for (rule 1)"
                }),
                "output_1": ("STRING", {
                    "default": "",
                    "tooltip": "Replacement value (rule 1)"
                }),
                "input_2": ("STRING", {
                    "default": "",
                    "tooltip": "Pattern to search for (rule 2)"
                }),
                "output_2": ("STRING", {
                    "default": "",
                    "tooltip": "Replacement value (rule 2)"
                }),
                "input_3": ("STRING", {
                    "default": "",
                    "tooltip": "Pattern to search for (rule 3)"
                }),
                "output_3": ("STRING", {
                    "default": "",
                    "tooltip": "Replacement value (rule 3)"
                }),
                "input_4": ("STRING", {
                    "default": "",
                    "tooltip": "Pattern to search for (rule 4)"
                }),
                "output_4": ("STRING", {
                    "default": "",
                    "tooltip": "Replacement value (rule 4)"
                }),
                "input_5": ("STRING", {
                    "default": "",
                    "tooltip": "Pattern to search for (rule 5)"
                }),
                "output_5": ("STRING", {
                    "default": "",
                    "tooltip": "Replacement value (rule 5)"
                }),
            },
        }
    
    RETURN_TYPES = ("STRING",)
    FUNCTION = "process"
    CATEGORY = "TOO-Pack/utils"
    OUTPUT_NODE = False

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("nan")

    def process(self, string, input_1, output_1, input_2, output_2, 
                input_3, output_3, input_4, output_4, input_5, output_5):
        if not string:
            return ("",)
        
        result = string
        
        # Apply rules in order
        rules = [
            (input_1, output_1),
            (input_2, output_2),
            (input_3, output_3),
            (input_4, output_4),
            (input_5, output_5),
        ]
        
        for search_value, replace_value in rules:
            if search_value and search_value in result:
                result = result.replace(search_value, replace_value)
        
        return (result,)


NODE_CLASS_MAPPINGS = {
    "TooMuchReplace": TooMuchReplace
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TooMuchReplace": "TOO Much Replace"
}
