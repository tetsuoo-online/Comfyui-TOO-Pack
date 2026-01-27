class ExtractWidgetFromNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "node_name": ("STRING", {
                    "default": "Power Lora Loader",
                    "tooltip": "The class type of the node to extract from (e.g., 'Power Lora Loader', 'LoraLoader', 'KSampler')"
                }),
                "widget_names": ("STRING", {
                    "default": "lora, strength",
                    "multiline": False,
                    "tooltip": "Comma-separated list of widgets to extract. Examples: 'lora, strength' for Power Lora Loader (rgthree), 'lora_name, strength_model' for LoraLoader, 'seed, steps, cfg' for KSampler. Leave empty to extract all widgets."
                }),
            },
            "hidden": {
                "extra_pnginfo": "EXTRA_PNGINFO",
                "prompt": "PROMPT",
                "unique_id": "UNIQUE_ID",
            },
        }
    
    RETURN_TYPES = ("STRING",)
    FUNCTION = "extract"
    CATEGORY = "TOO-Pack/utils"
    OUTPUT_NODE = False

    @classmethod
    def IS_CHANGED(cls, node_name, widget_names, **kwargs):
        return float("nan")

    def extract(self, node_name, widget_names, extra_pnginfo=None, prompt=None, unique_id=None):
        if prompt is None:
            return ("",)
        
        widget_list = [w.strip() for w in widget_names.split(",")] if widget_names else []
        result_lines = []
        
        for node_id in prompt:
            node_data = prompt[node_id]
            class_type = node_data.get("class_type", "")
            
            if node_name.lower() in class_type.lower():
                inputs = node_data.get("inputs", {})
                node_results = []
                processed_dicts = set()
                
                for key, value in inputs.items():
                    # Si key est dans la liste des widgets demandés
                    if widget_list and key in widget_list:
                        if isinstance(value, dict):
                            if "on" in value and not value.get("on", True):
                                continue
                            for dict_key, dict_value in value.items():
                                if dict_key != "on" and dict_value:
                                    node_results.append(str(dict_value))
                        elif not isinstance(value, (list, dict)):
                            node_results.append(str(value))
                    # Si value est un dict contenant les widgets demandés
                    elif isinstance(value, dict):
                        dict_id = id(value)
                        if dict_id not in processed_dicts:
                            if widget_list:
                                # Extraire seulement les widgets demandés du dict
                                matching_widgets = [w for w in widget_list if w in value]
                                if matching_widgets:
                                    processed_dicts.add(dict_id)
                                    if value.get("on", True):
                                        for widget_name in matching_widgets:
                                            widget_value = value.get(widget_name, "")
                                            if widget_value:
                                                node_results.append(str(widget_value))
                            else:
                                # Extraire tout si aucun widget spécifié
                                processed_dicts.add(dict_id)
                                for dict_key, dict_value in value.items():
                                    if dict_key != "on" and dict_value:
                                        node_results.append(str(dict_value))
                    # Extraire tout si aucun widget spécifié
                    elif not widget_list:
                        if not isinstance(value, (list, dict)):
                            node_results.append(str(value))
                
                if node_results:
                    result_lines.append("\n".join(node_results))
        
        output_string = "\n".join(result_lines)
        if output_string:
            output_string += "\n"
        
        return (output_string,)

NODE_CLASS_MAPPINGS = {
    "ExtractWidgetFromNode": ExtractWidgetFromNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ExtractWidgetFromNode": "Extract Widget From Node"
}