import os
import json
import re
from datetime import datetime
from PIL import Image
import numpy as np
import folder_paths
from comfy.cli_args import args

import piexif
import piexif.helper

class TOOSmartImageSaver:
    """
    Node de sauvegarde d'images intelligent qui remplace le subgraph SAVE_IMG.
    Permet d'activer/désactiver facilement chaque élément du nom de fichier.
    Supporte les métadonnées au format Civitai (A1111) via ExifIFD.UserComment.
    """
    
    def _safe_path(self, path):
        """
        Nettoie un chemin de fichier en retirant les caractères invalides.
        """
        if not path:
            return path
        
        # Séparer le chemin en répertoire et nom de fichier
        directory = os.path.dirname(path)
        filename = os.path.basename(path)
        
        # Caractères invalides dans les noms de fichiers (Windows/Linux/Mac)
        invalid = '<>:"|?*\n\r\t'
        # Pour le nom de fichier, nettoyer tous les caractères invalides
        clean_filename = "".join(c for c in filename if c not in invalid).strip()
        
        # Pour le répertoire, on garde les séparateurs de chemin
        # On nettoie juste les \n, \r, \t
        clean_directory = directory.replace('\n', '').replace('\r', '').replace('\t', '').strip()
        
        # Reconstruire le chemin
        if clean_directory:
            return os.path.join(clean_directory, clean_filename)
        return clean_filename
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "Images à sauvegarder"}),
                
                # Champs de base pour construire le nom (dans l'ordre d'affichage)
                "output_folder": ("STRING", {
                    "default": "YYYY-MM-DD",
                    "multiline": False,
                    "tooltip": "Dossier de destination. Supporte YYYY, YY, MM, DD, HH, mm, ss, timestamp. Ex: YYYY-MM-DD ou projects/test"
                }),
                "prefix": ("STRING", {
                    "default": "ComfyUI_YYYY-MM-DD_HHmmss",
                    "multiline": False,
                    "tooltip": "Préfixe du nom. Supporte YYYY, YY, MM, DD, HH, mm, ss, timestamp. Ex: render_YYYYMMDD"
                }),
                
                "extra1": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "tooltip": "Extra data. Supporte YYYY, YY, MM, DD, HH, mm, ss, timestamp. Ex: seed_YYYYMMDD"
                }),
                "extra2": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "tooltip": "Extra data. Supporte YYYY, YY, MM, DD, HH, mm, ss, timestamp. Ex: denoise_YYYYMMDD"
                }),
                "model": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "tooltip": "Model name with relative path. Clean name will be extracted without the extension"
                }),
                
                "suffix": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "tooltip": "Suffixe du nom. Supporte YYYY, YY, MM, DD, HH, mm, ss, timestamp. Ex: _final ou _HHmmss"
                }),
                
                # Format de sortie
                "output_format": (["webp", "png", "jpg", "jpeg"], {
                    "default": "webp",
                    "tooltip": "Format de l'image sauvegardée"
                }),
                "webp_lossless": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "WEBP sans perte (lossless, fichiers plus lourds). Uniquement pour WEBP. Si activé, ignore quality."
                }),
                "quality": ("INT", {
                    "default": 97,
                    "min": 1,
                    "max": 100,
                    "step": 1,
                    "tooltip": "Qualité de compression (1-100). Pour WEBP et JPG. Ignoré si webp_lossless est activé."
                }),
                
                # Séparateur
                "separator": ("STRING", {
                    "default": "_",
                    "multiline": False,
                    "tooltip": "Séparateur entre les éléments du nom"
                }),
                
                # Métadonnées
                "embed_workflow": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Embarquer le workflow ComfyUI dans l'image"
                }),
                "save_metadata": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Sauvegarder les métadonnées A1111/Civitai"
                }),
            },
            "optional": {
                "metadata": ("METADATA", {
                    "tooltip": "Métadonnées provenant de TOO Image Metadata"
                }),
                "workflow": ("WORKFLOW", {
                    "tooltip": "Workflow ComfyUI à embarquer (écrase le workflow courant si embed_workflow activé)"
                }),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
            },
        }
    
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("images", "filepath")
    FUNCTION = "save_images"
    OUTPUT_NODE = True
    CATEGORY = "🔵TOO-Pack/image"

    def save_images(self, images, output_folder, prefix, extra1, extra2, model, suffix,
                   output_format, webp_lossless, quality, separator, embed_workflow, save_metadata,
                   metadata=None, workflow=None, prompt=None, extra_pnginfo=None):
        
        # Traiter output_folder avec syntaxe date
        output_folder = self._parse_date_tokens(output_folder)
        
        # Nettoyer output_folder des caractères invalides
        output_folder = self._safe_path(output_folder) if output_folder else output_folder
        
        # Créer le dossier de sortie
        output_dir = folder_paths.get_output_directory()
        if output_folder:
            output_dir = os.path.join(output_dir, output_folder)
        os.makedirs(output_dir, exist_ok=True)
        
        # Construction du nom de fichier
        filename_parts = []
        
        # 1. Prefix (peut contenir tokens date)
        if prefix:
            prefix = self._parse_date_tokens(prefix)
            filename_parts.append(prefix)
        
        # 2. Extra1
        if extra1:
            extra1 = self._parse_date_tokens(extra1)
            filename_parts.append(extra1)
        
        # 3. Extra2
        if extra2:
            extra2 = self._parse_date_tokens(extra2)
            filename_parts.append(extra2)
        
        # 4. Model
        if model:
            model = self._clean_model_name(model)
            filename_parts.append(model)
        
        # 5. Suffix (peut contenir tokens date)
        if suffix:
            suffix = self._parse_date_tokens(suffix)
            filename_parts.append(suffix)
        
        # Construire le nom final
        if not filename_parts:
            filename_parts = ["output"]
        
        filename_base = separator.join(filename_parts)
        
        # Nettoyer le nom de fichier des caractères invalides
        filename_base = self._safe_path(filename_base) if filename_base else filename_base
        
        # Préparer les métadonnées A1111 si fournies et si save_metadata activé
        a111_params = None
        if save_metadata and metadata and isinstance(metadata, dict):
            width, height = self._get_image_dimensions(images[0])
            a111_params = self._build_a111_params(metadata, width, height)
        
        # Sauvegarder toutes les images
        saved_paths = []
        for i, image in enumerate(images):
            # Ajouter un compteur si plusieurs images
            if len(images) > 1:
                filename = f"{filename_base}_{i:04d}.{output_format}"
            else:
                filename = f"{filename_base}.{output_format}"
            
            filepath = os.path.join(output_dir, filename)
            
            # S'assurer que le fichier n'existe pas déjà (ajouter un compteur)
            counter = 1
            while os.path.exists(filepath):
                if len(images) > 1:
                    filename = f"{filename_base}_{i:04d}_{counter:03d}.{output_format}"
                else:
                    filename = f"{filename_base}_{counter:03d}.{output_format}"
                filepath = os.path.join(output_dir, filename)
                counter += 1
            
            # Convertir tensor en image PIL
            img = self._tensor_to_pil(image)
            
            # Sauvegarder selon le format
            if output_format == "png":
                self._save_png(img, filepath, a111_params, prompt, extra_pnginfo, embed_workflow, workflow)
            elif output_format in ["webp", "jpg", "jpeg"]:
                self._save_webp_jpeg(img, filepath, output_format, webp_lossless, quality, 
                                    a111_params, prompt, extra_pnginfo, embed_workflow, workflow)
            
            saved_paths.append(filepath)
            print(f"💾 Image sauvegardée: {filepath}")
        
        # Retourner les images et le chemin du premier fichier
        return (images, saved_paths[0] if saved_paths else "")
    
    def _save_png(self, img, filepath, a111_params, prompt, extra_pnginfo, embed_workflow, workflow):
        """Sauvegarde une image PNG avec métadonnées"""
        from PIL import PngImagePlugin
        
        if args.disable_metadata:
            img.save(filepath)
            return
        
        metadata = PngImagePlugin.PngInfo()
        
        # Ajouter les paramètres A1111 dans "parameters"
        if a111_params:
            metadata.add_text("parameters", a111_params)
        
        # Ajouter le workflow ComfyUI si demandé
        if embed_workflow:
            # Si workflow est fourni en entrée, l'utiliser en priorité
            if workflow and isinstance(workflow, dict):
                wf_extra_pnginfo = workflow.get("extra_pnginfo")
                wf_prompt = workflow.get("prompt")
                
                if wf_extra_pnginfo is not None:
                    for k, v in wf_extra_pnginfo.items():
                        metadata.add_text(k, json.dumps(v))
                
                if wf_prompt is not None:
                    metadata.add_text("prompt", json.dumps(wf_prompt))
            else:
                # Sinon, utiliser le workflow courant
                if extra_pnginfo is not None:
                    for k, v in extra_pnginfo.items():
                        metadata.add_text(k, json.dumps(v))
                
                if prompt is not None:
                    metadata.add_text("prompt", json.dumps(prompt))
        
        img.save(filepath, pnginfo=metadata)
    
    def _save_webp_jpeg(self, img, filepath, output_format, webp_lossless, quality, 
                       a111_params, prompt, extra_pnginfo, embed_workflow, workflow):
        """Sauvegarde une image WEBP ou JPEG avec métadonnées EXIF"""
        # Sauvegarder l'image d'abord
        if output_format == "webp":
            img.save(filepath, lossless=webp_lossless, quality=quality, method=6)
        else:  # jpg/jpeg
            img.save(filepath, quality=quality)
        
        # Ajouter les métadonnées EXIF si non désactivé
        if args.disable_metadata:
            return
        
        # Construire le dictionnaire EXIF
        pnginfo_json = {}
        prompt_json = {}
        
        # Workflow ComfyUI dans Make/Model tags si demandé
        if embed_workflow:
            # Si workflow est fourni en entrée, l'utiliser en priorité
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
                # Sinon, utiliser le workflow courant
                if extra_pnginfo is not None:
                    pnginfo_json = {
                        piexif.ImageIFD.Make - i: f"{k}:{json.dumps(v, separators=(',', ':'))}" 
                        for i, (k, v) in enumerate(extra_pnginfo.items())
                    }
                
                if prompt is not None:
                    prompt_json = {
                        piexif.ImageIFD.Model: f"prompt:{json.dumps(prompt, separators=(',', ':'))}"
                    }
        
        # Construire le dictionnaire EXIF complet
        exif_dict = {}
        
        # Section "0th" pour workflow
        if pnginfo_json or prompt_json:
            exif_dict["0th"] = pnginfo_json | prompt_json
        
        # Section "Exif" pour les paramètres A1111
        if a111_params:
            exif_dict["Exif"] = {
                piexif.ExifIFD.UserComment: piexif.helper.UserComment.dump(
                    a111_params, 
                    encoding="unicode"
                )
            }
        
        # Générer et insérer les données EXIF
        if exif_dict:
            exif_bytes = piexif.dump(exif_dict)
            
            # Vérifier la taille pour JPEG
            if output_format in ["jpg", "jpeg"]:
                MAX_EXIF_SIZE = 65535
                if len(exif_bytes) > MAX_EXIF_SIZE:
                    print(f"⚠️ TOO Smart Image Saver: Métadonnées trop volumineuses ({len(exif_bytes)} bytes) pour JPEG (max {MAX_EXIF_SIZE})")
                    # Essayer sans le workflow
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
    
    def _build_a111_params(self, metadata, width, height):
        """
        Construit la chaîne de paramètres au format A1111/Civitai.
        Format: 
        {positive}
        Negative prompt: {negative}
        Steps: {steps}, Sampler: {sampler} {scheduler}, CFG scale: {cfg}, Seed: {seed}, 
        Size: {width}x{height}, Model hash: {hash}, Model: {model}, Lora hashes: "name1: hash1, name2: hash2"
        """
        positive = metadata.get("positive", "").strip()
        negative = metadata.get("negative", "").strip()
        seed = metadata.get("seed")
        steps = metadata.get("steps", 20)
        cfg = metadata.get("cfg", 7.0)
        sampler_name = metadata.get("sampler_name", "euler")
        scheduler = metadata.get("scheduler", "normal")
        model_name = metadata.get("model_name", "").strip()
        model_hash = metadata.get("model_hash", "").strip()
        lora_hashes = metadata.get("lora_hashes", {})
        custom = metadata.get("custom", "").strip()
        
        # Construction de la chaîne
        parts = [positive]
        
        if negative:
            parts.append(f"Negative prompt: {negative}")
        
        # Ligne des paramètres
        params_line = f"Steps: {steps}, Sampler: {sampler_name} {scheduler}, CFG scale: {cfg}"
        
        if seed is not None:
            params_line += f", Seed: {seed}"
        
        if width and height:
            params_line += f", Size: {width}x{height}"
        
        if custom:
            params_line += f", {custom}"
        
        if model_hash:
            params_line += f", Model hash: {model_hash}"
        
        if model_name:
            params_line += f", Model: {model_name}"
        
        if lora_hashes:
            lora_str = ", ".join([f"{name}: {hash_val}" for name, hash_val in lora_hashes.items()])
            params_line += f', Lora hashes: "{lora_str}"'
        
        params_line += ", Version: ComfyUI"
        
        parts.append(params_line)
        
        return "\n".join(parts)
    
    def _get_image_dimensions(self, tensor):
        """Récupère les dimensions d'un tensor d'image"""
        # tensor shape: [H, W, C]
        if len(tensor.shape) >= 2:
            height, width = tensor.shape[0], tensor.shape[1]
            return int(width), int(height)
        return None, None
    
    def _parse_date_tokens(self, text):
        """
        Remplace les tokens date directement dans le texte.
        Tokens supportés: YYYY, YY, MM, DD, HH, mm, ss, timestamp
        Ex: YYYY-MM-DD -> 2024-12-19
            HH-mm-ss -> 14-30-25
            timestamp -> 1734618625
        """
        if not text:
            return text
        
        now = datetime.now()
        
        # Cas spécial: timestamp (doit être fait en premier)
        if 'timestamp' in text:
            text = text.replace('timestamp', str(int(now.timestamp())))
        
        # Remplacements simples
        replacements = {
            'YYYY': now.strftime('%Y'),  # Année 4 chiffres
            'YY': now.strftime('%y'),    # Année 2 chiffres
            'MM': now.strftime('%m'),    # Mois 2 chiffres
            'DD': now.strftime('%d'),    # Jour 2 chiffres
            'HH': now.strftime('%H'),    # Heure 24h 2 chiffres
            'mm': now.strftime('%M'),    # Minute 2 chiffres
            'ss': now.strftime('%S'),    # Seconde 2 chiffres
        }
        
        for token, value in replacements.items():
            text = text.replace(token, value)
        
        return text
    def _clean_model_name(self, model_name):
        """
        Nettoie le nom du modèle:
        - Retire l'extension .safetensors, .ckpt, .pt
        - Retire le chemin si présent (Windows et Unix)
        - Nettoie les espaces et retours à la ligne
        """
        if not model_name:
            return model_name
            
        # Retirer tous les espaces, retours à la ligne, et caractères invisibles
        model_name = model_name.strip()
        
        # Normaliser les séparateurs de chemin (remplacer \ par /)
        # pour que os.path.basename fonctionne sur tous les systèmes
        model_name = model_name.replace('\\', '/')
        
        # Retirer le chemin
        model_name = os.path.basename(model_name)
        
        # Re-strip après basename au cas où
        model_name = model_name.strip()
        
        # Utiliser splitext pour retirer l'extension, puis vérifier si c'est une extension connue
        name_without_ext, ext = os.path.splitext(model_name)
        
        # Liste des extensions connues (en minuscules)
        known_extensions = ['.safetensors', '.ckpt', '.pt', '.pth', '.bin']
        
        # Si l'extension est dans la liste, on retourne le nom sans extension
        if ext.lower() in known_extensions:
            return name_without_ext.strip()  # Strip final pour être sûr
        
        # Sinon, on retourne le nom complet (peut-être que ce n'était pas vraiment une extension de modèle)
        return model_name
    
    def _tensor_to_pil(self, tensor):
        """Convertit un tensor ComfyUI en image PIL"""
        # tensor shape: [H, W, C] avec valeurs 0-1
        img_array = (tensor.cpu().numpy() * 255).astype(np.uint8)
        return Image.fromarray(img_array)


NODE_CLASS_MAPPINGS = {
    "TOOSmartImageSaver": TOOSmartImageSaver
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TOOSmartImageSaver": "💾 TOO Smart Image Saver"
}
