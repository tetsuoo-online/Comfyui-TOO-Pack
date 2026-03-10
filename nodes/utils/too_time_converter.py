import math

class TOOTimeConverter:
    """
    Convertit une durée (float) en format HHhMMmSSs.
    L'affichage temps réel est géré côté JS.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "value": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 999999.0,
                    "step": 0.1,
                }),
                "unit": (["Secondes", "Minutes", "Heures"], {
                    "default": "Secondes"
                }),
            }
        }

    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("formatted", "total_seconds")
    FUNCTION = "convert"
    CATEGORY = "🔵TOO-Pack/utils"

    def convert(self, value, unit):
        if unit == "Minutes":
            total_seconds = value * 60
        elif unit == "Heures":
            total_seconds = value * 3600
        else:
            total_seconds = value

        total_seconds_rounded = round(total_seconds)

        hours = total_seconds_rounded // 3600
        remainder = total_seconds_rounded % 3600
        minutes = remainder // 60
        seconds = remainder % 60

        if hours > 0:
            formatted = f"{hours:02d}h{minutes:02d}m{seconds:02d}s"
        elif minutes > 0:
            formatted = f"{minutes:02d}m{seconds:02d}s"
        else:
            formatted = f"{seconds:02d}s"

        return (formatted, total_seconds_rounded)


NODE_CLASS_MAPPINGS = {
    "TOOTimeConverter": TOOTimeConverter
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TOOTimeConverter": "⏱️ TOO Time Converter"
}
