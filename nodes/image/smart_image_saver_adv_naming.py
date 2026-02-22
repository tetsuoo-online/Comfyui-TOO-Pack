import os
import json
import numpy as np
from PIL import Image
from PIL.PngImagePlugin import PngInfo
import folder_paths
from datetime import datetime
import piexif
import piexif.helper
from comfy.cli_args import args
import hashlib

class FileNaming:
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
            },
            "optional": {
                "metadata": ("METADATA",),
                "workflow": ("WORKFLOW",),
                "any1": ("*", {"forceInput": True}),
                "any2": ("*", {"forceInput": True}),
                "any3": ("*", {"forceInput": True}),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
                "unique_id": "UNIQUE_ID",
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("images", "filepath")
    FUNCTION = "save_images"
    OUTPUT_NODE = True
    CATEGORY = "🔵TOO-Pack/image"

    def _parse_date_tokens(self, text):
        if not text:
            return text
        now = datetime.now()
        if 'timestamp' in text:
            text = text.replace('timestamp', str(int(now.timestamp())))

        replacements = {
            "YYYY": now.strftime("%Y"),
            "YY": now.strftime("%y"),
            "MM": now.strftime("%m"),
            "DD": now.strftime("%d"),
            "HH": now.strftime("%H"),
            "mm": now.strftime("%M"),
            "ss": now.strftime("%S")
        }

        for token, value in replacements.items():
            text = text.replace(token, value)
        return text

    def _safe_path(self, path):
        if not path:
            return path
        directory = os.path.dirname(path)
        filename = os.path.basename(path)
        invalid = '<>:"|?*\n\r\t'
        clean_filename = "".join(c for c in filename if c not in invalid).strip()
        clean_directory = directory.replace('\n', '').replace('\r', '').replace('\t', '').strip()
        if clean_directory:
            return os.path.join(clean_directory, clean_filename)
        return clean_filename
    
    def _calculate_file_hash(self, filepath, hash_length=12):
        try:
            possible_paths = []
            if os.path.isfile(filepath):
                possible_paths.append(filepath)
            else:
                checkpoints_dir = folder_paths.get_folder_paths("checkpoints")
                for cp_dir in checkpoints_dir:
                    full_path = os.path.join(cp_dir, filepath)
                    if os.path.isfile(full_path):
                        possible_paths.append(full_path)
                loras_dir = folder_paths.get_folder_paths("loras")
                for lora_dir in loras_dir:
                    full_path = os.path.join(lora_dir, filepath)
                    if os.path.isfile(full_path):
                        possible_paths.append(full_path)
            if not possible_paths:
                return ""
            actual_path = possible_paths[0]
            sha256_hash = hashlib.sha256()
            with open(actual_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()[:hash_length]
        except Exception as e:
            print(f"Warning: Could not calculate hash for {filepath}: {e}")
            return ""

    def _calculate_lora_hash(self, filepath):
        """
        Calculate SHA256 hash of a lora file excluding safetensors metadata (compatible A1111/Civitai AutoV3).
        Returns first 12 characters of the hash.
        """
        try:
            possible_paths = []
            if os.path.isfile(filepath):
                possible_paths.append(filepath)
            else:
                checkpoints_dir = folder_paths.get_folder_paths("checkpoints")
                for cp_dir in checkpoints_dir:
                    full_path = os.path.join(cp_dir, filepath)
                    if os.path.isfile(full_path):
                        possible_paths.append(full_path)
                loras_dir = folder_paths.get_folder_paths("loras")
                for lora_dir in loras_dir:
                    full_path = os.path.join(lora_dir, filepath)
                    if os.path.isfile(full_path):
                        possible_paths.append(full_path)
            if not possible_paths:
                return ""
            actual_path = possible_paths[0]
            hash_sha256 = hashlib.sha256()
            blksize = 1024 * 1024
            with open(actual_path, "rb") as f:
                header = f.read(8)
                n = int.from_bytes(header, "little")
                offset = n + 8
                f.seek(offset)
                for chunk in iter(lambda: f.read(blksize), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()[:12]
        except Exception as e:
            print(f"Warning: Could not calculate lora hash for {filepath}: {e}")
            return ""

    def _build_a111_params(self, metadata, width, height):
        """Build A1111/Civitai format metadata string"""
        positive = metadata.get("positive", "").strip()
        positive = " ".join(positive.split())
        negative = metadata.get("negative", "").strip()
        negative = " ".join(negative.split())
        seed = metadata.get("seed")
        steps = metadata.get("steps")
        cfg = metadata.get("cfg")
        sampler_name = metadata.get("sampler_name", "").strip()
        scheduler = metadata.get("scheduler", "").strip()
        model_name = metadata.get("model_name", "").strip()
        model_hash = metadata.get("model_hash", "").strip()
        lora_hashes = metadata.get("lora_hashes", {})
        custom = metadata.get("custom", "").strip()

        parts = []
        if positive:
            parts.append(positive)
        if negative:
            parts.append(f"Negative prompt: {negative}")

        params_parts = []
        if steps:
            params_parts.append(f"Steps: {steps}")
        if sampler_name:
            sampler_str = f"Sampler: {sampler_name}"
            if scheduler:
                sampler_str += f" {scheduler}"
            params_parts.append(sampler_str)
        if cfg:
            params_parts.append(f"CFG scale: {cfg}")
        if seed is not None:
            params_parts.append(f"Seed: {seed}")
        if width and height:
            params_parts.append(f"Size: {width}x{height}")
        if custom:
            params_parts.append(custom)
        if model_hash:
            params_parts.append(f"Model hash: {model_hash}")
        if model_name:
            params_parts.append(f"Model: {model_name}")
        if lora_hashes:
            if isinstance(lora_hashes, dict):
                lora_str = ", ".join([f"{name}: {h}" for name, h in lora_hashes.items()])
                params_parts.append(f'Lora hashes: "{lora_str}"')
            elif isinstance(lora_hashes, str):
                params_parts.append(f'Lora hashes: "{lora_hashes}"')

        params_parts.append("Version: ComfyUI")

        if params_parts:
            parts.append(", ".join(params_parts))

        return "\n".join(parts) if parts else ""

    def _get_image_dimensions(self, tensor):
        if len(tensor.shape) >= 2:
            height, width = tensor.shape[0], tensor.shape[1]
            return int(width), int(height)
        return None, None

    def _extract_from_prompt(self, extraction_pattern, prompt):
        """
        Extract widget value from prompt.
        Supports:
        - #123:widget_name (simple node ID)
        - #270:268:widget_name (subgraph node ID with : separator)
        - ClassName:widget_name (class type search)
        Returns list of values for multiline strings, or single value as string.
        """
        if not prompt or not extraction_pattern:
            return ""

        extraction_pattern = extraction_pattern.strip()

        if ":" not in extraction_pattern:
            return ""

        if extraction_pattern.startswith("#"):
            pattern_without_hash = extraction_pattern[1:]
            last_colon_idx = pattern_without_hash.rfind(":")
            if last_colon_idx == -1:
                return ""

            node_id = pattern_without_hash[:last_colon_idx]
            widget_name = pattern_without_hash[last_colon_idx + 1:]

            if node_id in prompt:
                node_data = prompt[node_id]
                inputs = node_data.get("inputs", {})
                value = inputs.get(widget_name, "")
                if isinstance(value, str) and '\n' in value:
                    lines = [line.strip() for line in value.split('\n') if line.strip()]
                    return lines if lines else ""
                return str(value) if value else ""
            return ""

        else:
            parts = extraction_pattern.split(":", 1)
            if len(parts) != 2:
                return ""

            class_search = parts[0].lower()
            widget_name = parts[1]

            for node_id in prompt:
                node_data = prompt[node_id]
                class_type = node_data.get("class_type", "")

                if class_search in class_type.lower():
                    inputs = node_data.get("inputs", {})
                    value = inputs.get(widget_name, "")
                    if isinstance(value, str) and '\n' in value:
                        lines = [line.strip() for line in value.split('\n') if line.strip()]
                        return lines if lines else ""
                    return str(value) if value else ""
            return ""

    def resolve_template_value(self, value, prompt, meta_dict, date_vars, any_values):
        if not value or "{" not in value:
            return self._resolve_simple(value, prompt, meta_dict, date_vars, any_values)
        
        import re
        return re.sub(r'\{([^}]+)\}', 
                      lambda m: self._resolve_token(m.group(1).strip(), prompt, meta_dict, date_vars, any_values) or m.group(0), 
                      value)

    def _resolve_simple(self, value, prompt, meta_dict, date_vars, any_values):
        if not value:
            return ""
        v = value.strip()
        result = self._resolve_token(v, prompt, meta_dict, date_vars, any_values)
        return result if result is not None else value

    def _resolve_token(self, token, prompt, meta_dict, date_vars, any_values):
        if token in any_values and any_values[token]:
            result = self._convert_to_str(any_values[token])
            if result and ('\\' in result or '/' in result or result.endswith(('.safetensors', '.ckpt', '.pt', '.pth', '.bin'))):
                result = os.path.splitext(os.path.basename(result))[0]
            return result if result else None
        if token in date_vars and date_vars[token]:
            return self._convert_to_str(date_vars[token])
        if ":" in token and (token.startswith("#") or not token.startswith("%")):
            extracted = self._extract_from_prompt(token, prompt)
            if extracted:
                result = self._convert_to_str(extracted)
                if result and ('\\' in result or '/' in result or result.endswith(('.safetensors', '.ckpt', '.pt', '.pth', '.bin'))):
                    result = os.path.splitext(os.path.basename(result))[0]
                return result if result else None
        if token in meta_dict and meta_dict[token]:
            return self._convert_to_str(meta_dict[token])
        return None
    
    def _resolve_token_raw(self, token, prompt, meta_dict, date_vars, any_values):
        if token in any_values and any_values[token]:
            return any_values[token]
        if token in date_vars and date_vars[token]:
            return date_vars[token]
        if ":" in token and (token.startswith("#") or not token.startswith("%")):
            return self._extract_from_prompt(token, prompt)
        if token in meta_dict and meta_dict[token]:
            return meta_dict[token]
        return None

    def _convert_to_str(self, val):
        if isinstance(val, list):
            return " ".join(" ".join(str(v).split()) for v in val)
        result = str(val) if val else ""
        return " ".join(result.split())
    
    def resolve_for_metadata(self, value, prompt, meta_dict, date_vars, any_values):
        if not value:
            return ""
        import re
        match = re.search(r'\{([^}]+)\}', value)
        if match:
            return self._resolve_token(match.group(1).strip(), prompt, meta_dict, date_vars, any_values) or ""
        return self._resolve_simple(value, prompt, meta_dict, date_vars, any_values)
    
    def resolve_for_metadata_raw(self, value, prompt, meta_dict, date_vars, any_values):
        if not value:
            return None
        import re
        match = re.search(r'\{([^}]+)\}', value)
        if match:
            return self._resolve_token_raw(match.group(1).strip(), prompt, meta_dict, date_vars, any_values)
        v = value.strip()
        return self._resolve_token_raw(v, prompt, meta_dict, date_vars, any_values)

    def save_images(self, images, metadata=None, workflow=None, any1=None, any2=None, any3=None, prompt=None, extra_pnginfo=None, unique_id=None):
        config = self._get_config(extra_pnginfo, unique_id)

        any1_value = str(any1).strip() if any1 is not None else ""
        any2_value = str(any2).strip() if any2 is not None else ""
        any3_value = str(any3).strip() if any3 is not None else ""
        
        any_values = {
            "[any1]": any1_value,
            "[any2]": any2_value,
            "[any3]": any3_value
        }

        date_vars = {
            "%date1": self._parse_date_tokens(config.get("date1", "")),
            "%date2": self._parse_date_tokens(config.get("date2", "")),
            "%date3": self._parse_date_tokens(config.get("date3", ""))
        }

        meta_dict = {}
        naming_dict = {}
        if metadata and isinstance(metadata, dict):
            meta_dict = metadata.copy()
            naming_dict = metadata.copy()

        data_fields = config.get("data_fields", [])
        for field in data_fields:
            name = field.get("name", "")
            value = field.get("value", "")

            if not name:
                continue

            resolved_meta = self.resolve_for_metadata(value, prompt, meta_dict, date_vars, any_values)
            if resolved_meta:
                meta_dict[name] = resolved_meta
            
            resolved_naming = self.resolve_template_value(value, prompt, meta_dict, date_vars, any_values)
            if resolved_naming:
                naming_dict[name] = resolved_naming

        model_extract = config.get("model_extract", "")
        if model_extract:
            model_value = self.resolve_for_metadata_raw(model_extract, prompt, meta_dict, date_vars, any_values)
            
            if model_value:
                if isinstance(model_value, list):
                    model_value = model_value[0] if model_value else None
                
                if model_value:
                    model_name = os.path.splitext(os.path.basename(str(model_value)))[0]
                    meta_dict["model"] = model_name
                    naming_dict["model"] = self.resolve_template_value(model_extract, prompt, meta_dict, date_vars, any_values)
                    if "model_name" not in meta_dict:
                        meta_dict["model_name"] = model_name
                        naming_dict["model_name"] = model_name
                    
                    if "model_hash" not in meta_dict:
                        model_hash = self._calculate_file_hash(str(model_value), 10)
                        if model_hash:
                            meta_dict["model_hash"] = model_hash
                            naming_dict["model_hash"] = model_hash

        loras_extracts = config.get("loras_extracts", [])
        lora_names = []
        lora_hashes_dict = {}
        for lora_extract in loras_extracts:
            if lora_extract:
                lora_value = self.resolve_for_metadata_raw(lora_extract, prompt, meta_dict, date_vars, any_values)
                
                if isinstance(lora_value, str):
                    lora_value = [line.strip() for line in lora_value.split('\n') if line.strip()]
                
                lora_values = lora_value if isinstance(lora_value, list) else [lora_value] if lora_value else []
                
                for lora_val in lora_values:
                    if lora_val:
                        lora_name = os.path.splitext(os.path.basename(str(lora_val)))[0]
                        lora_names.append(lora_name)
                        lora_hash = self._calculate_lora_hash(str(lora_val))
                        if lora_hash:
                            lora_hashes_dict[lora_name] = lora_hash

        if lora_names:
            meta_dict["loras"] = ", ".join(lora_names)
            if loras_extracts and loras_extracts[0]:
                naming_dict["loras"] = self.resolve_template_value(loras_extracts[0], prompt, meta_dict, date_vars, any_values)
            else:
                naming_dict["loras"] = ", ".join(lora_names)
        
        if lora_hashes_dict and "lora_hashes" not in meta_dict:
            meta_dict["lora_hashes"] = lora_hashes_dict
            naming_dict["lora_hashes"] = lora_hashes_dict

        replacements = config.get("text_replace_pairs", [])
        for pair in replacements:
            target = pair.get("target", "")
            input_str = pair.get("input", "")
            output_str = pair.get("output", "")

            if not input_str:
                continue

            if target in any_values:
                target = ""
            
            if target and target in meta_dict:
                value = str(meta_dict[target])
                meta_dict[target] = value.replace(input_str, output_str)
            elif not target:
                for key in meta_dict:
                    value = str(meta_dict[key])
                    meta_dict[key] = value.replace(input_str, output_str)
            
            if target and target in naming_dict:
                value = str(naming_dict[target])
                naming_dict[target] = value.replace(input_str, output_str)
            elif not target:
                for key in naming_dict:
                    value = str(naming_dict[key])
                    naming_dict[key] = value.replace(input_str, output_str)

        filename_parts = []
        separator = config.get("separator", "_")

        output_folder = ""
        for field in ["output_folder", "prefix", "extra1", "extra2", "extra3", "extra4", "suffix"]:
            value = config.get(field, "")
            if not value:
                continue

            resolved = self.resolve_template_value(value, prompt, naming_dict, date_vars, any_values)
            if not resolved:
                continue

            if field == "output_folder":
                output_folder = resolved
            else:
                filename_parts.append(resolved)

        output_dir = self.output_dir
        if output_folder:
            output_folder = self._safe_path(output_folder)
            output_dir = os.path.join(output_dir, output_folder)
            os.makedirs(output_dir, exist_ok=True)

        filename_base = separator.join(filename_parts) if filename_parts else "output"
        filename_base = self._safe_path(filename_base)

        output_format = config.get("output_format", "webp")
        quality = config.get("quality", 95)
        embed_workflow = config.get("embed_workflow", True)
        save_metadata = config.get("save_metadata", True)

        saved_paths = []
        for i, image in enumerate(images):
            if len(images) > 1:
                filename = f"{filename_base}_{i:04d}.{output_format}"
            else:
                filename = f"{filename_base}.{output_format}"

            filepath = os.path.join(output_dir, filename)

            counter = 1
            while os.path.exists(filepath):
                filename = f"{filename_base}_{counter:03d}.{output_format}"
                filepath = os.path.join(output_dir, filename)
                counter += 1

            i_np = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i_np, 0, 255).astype(np.uint8))

            a111_params = None
            if save_metadata and meta_dict:
                width, height = self._get_image_dimensions(image)
                a111_params = self._build_a111_params(meta_dict, width, height)

            if output_format == "png":
                self._save_png(img, filepath, a111_params, workflow, prompt, extra_pnginfo, embed_workflow)
            else:
                self._save_webp_jpeg(img, filepath, output_format, quality, a111_params, workflow, prompt, extra_pnginfo, embed_workflow)

            saved_paths.append(filepath)

        return (images, saved_paths[0] if saved_paths else "")

    def _get_config(self, extra_pnginfo, unique_id=None):
        config = {
            "separator": "_",
            "output_format": "webp",
            "quality": 95,
            "embed_workflow": True,
            "save_metadata": True,
            "date1": "YYYY-MM-DD",
            "date2": "YYYY-MM-DD_HHmmss",
            "date3": "HHmmss",
            "text_replace_pairs": [],
            "data_fields": [],
            "model_extract": "",
            "loras_extracts": []
        }

        if extra_pnginfo and "workflow" in extra_pnginfo:
            try:
                wf = json.loads(extra_pnginfo["workflow"]) if isinstance(extra_pnginfo["workflow"], str) else extra_pnginfo["workflow"]
                nodes = wf.get("nodes", [])
                target_node = None

                # Chercher d'abord par unique_id
                if unique_id is not None:
                    uid = str(unique_id)
                    for node in nodes:
                        if str(node.get("id", "")) == uid:
                            target_node = node
                            break

                if target_node:
                    config.update(target_node.get("properties", {}))
                    config["text_replace_pairs"] = target_node.get("text_replace_pairs", [])
                    config["data_fields"] = target_node.get("data_fields", [])
            except:
                pass

        return config

    def _save_png(self, img, filepath, a111_params, workflow, prompt, extra_pnginfo, embed_workflow):
        if args.disable_metadata:
            img.save(filepath)
            return

        pnginfo = PngInfo()

        if a111_params:
            pnginfo.add_text("parameters", a111_params)

        if embed_workflow:
            if workflow and isinstance(workflow, dict):
                wf_extra = workflow.get("extra_pnginfo")
                wf_prompt = workflow.get("prompt")
                if wf_extra:
                    for k, v in wf_extra.items():
                        pnginfo.add_text(k, json.dumps(v) if not isinstance(v, str) else v)
                if wf_prompt:
                    pnginfo.add_text("prompt", json.dumps(wf_prompt))
            else:
                if extra_pnginfo:
                    for k, v in extra_pnginfo.items():
                        pnginfo.add_text(k, json.dumps(v) if not isinstance(v, str) else v)
                if prompt:
                    pnginfo.add_text("prompt", json.dumps(prompt))

        img.save(filepath, pnginfo=pnginfo)

    def _save_webp_jpeg(self, img, filepath, output_format, quality, a111_params, workflow, prompt, extra_pnginfo, embed_workflow):
        if output_format == "webp":
            img.save(filepath, quality=quality, method=6)
        else:
            img.save(filepath, quality=quality)

        if args.disable_metadata:
            return

        pnginfo_json = {}
        prompt_json = {}

        if embed_workflow:
            if workflow and isinstance(workflow, dict):
                wf_extra_pnginfo = workflow.get("extra_pnginfo")
                wf_prompt = workflow.get("prompt")

                if wf_extra_pnginfo is not None:
                    pnginfo_json = {
                        piexif.ImageIFD.Make - i: f"{k}:{json.dumps(v, separators=(',', ':'))}"
                        for i, (k, v) in enumerate(wf_extra_pnginfo.items())
                    }

                if wf_prompt is not None:
                    prompt_json = {
                        piexif.ImageIFD.Model: f"prompt:{json.dumps(wf_prompt, separators=(',', ':'))}"
                    }
            else:
                if extra_pnginfo is not None:
                    pnginfo_json = {
                        piexif.ImageIFD.Make - i: f"{k}:{json.dumps(v, separators=(',', ':'))}"
                        for i, (k, v) in enumerate(extra_pnginfo.items())
                    }

                if prompt is not None:
                    prompt_json = {
                        piexif.ImageIFD.Model: f"prompt:{json.dumps(prompt, separators=(',', ':'))}"
                    }

        exif_dict = {}

        if pnginfo_json or prompt_json:
            exif_dict["0th"] = pnginfo_json | prompt_json

        if a111_params:
            exif_dict["Exif"] = {
                piexif.ExifIFD.UserComment: piexif.helper.UserComment.dump(
                    a111_params,
                    encoding="unicode"
                )
            }

        if exif_dict:
            try:
                exif_bytes = piexif.dump(exif_dict)

                if output_format in ["jpg", "jpeg"]:
                    MAX_EXIF_SIZE = 65535
                    if len(exif_bytes) > MAX_EXIF_SIZE:
                        print(f"⚠️ Métadonnées trop volumineuses ({len(exif_bytes)} bytes) pour JPEG (max {MAX_EXIF_SIZE})")
                        exif_dict_minimal = {}
                        if a111_params:
                            exif_dict_minimal["Exif"] = {
                                piexif.ExifIFD.UserComment: piexif.helper.UserComment.dump(
                                    a111_params,
                                    encoding="unicode"
                                )
                            }
                        if exif_dict_minimal:
                            exif_bytes = piexif.dump(exif_dict_minimal)
                            if len(exif_bytes) <= MAX_EXIF_SIZE:
                                piexif.insert(exif_bytes, filepath)
                                print("   → Métadonnées A1111 sauvegardées (workflow omis)")
                            else:
                                print("   → Impossible de sauvegarder les métadonnées")
                        return

                piexif.insert(exif_bytes, filepath)
            except Exception as e:
                print(f"Could not save EXIF metadata: {e}")


NODE_CLASS_MAPPINGS = {
    "FileNaming (LiteGraph)": FileNaming,
    "FileNaming (DOM)": FileNaming
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "FileNaming (LiteGraph)": "💾 TOO Smart Image Saver (Advanced)",
    "FileNaming (DOM)": "💾 TOO Smart Image Saver (Advanced)(DOM)"
}
