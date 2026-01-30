import os
import json
import re
from datetime import datetime
from PIL import Image
import numpy as np
import folder_paths
from comfy.cli_args import args

class TOOSmartImageSaver:
    """
    Node de sauvegarde d'images intelligent qui remplace le subgraph SAVE_IMG.
    Permet d'activer/désactiver facilement chaque élément du nom de fichier.
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
                
                # Paramètres pour seed et model (si vides, non utilisés)
                "seed_node_name": ("STRING", {
                    "default": "KSampler",
                    "tooltip": "Nom de classe du node contenant le seed (ex: KSampler) ou #ID pour cibler par ID (ex: #10). Laisser vide pour ignorer."
                }),
                "seed_widget_name": ("STRING", {
                    "default": "seed",
                    "tooltip": "Nom du widget contenant le seed"
                }),
                
                "model_node_name": ("STRING", {
                    "default": "CheckpointLoaderSimple",
                    "tooltip": "Nom de classe du node contenant le modèle (ex: CheckpointLoaderSimple) ou #ID pour cibler par ID (ex: #5). Laisser vide pour ignorer."
                }),
                "model_widget_name": ("STRING", {
                    "default": "ckpt_name",
                    "tooltip": "Nom du widget contenant le modèle"
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

    def save_images(self, images, output_folder, prefix, suffix, 
                   seed_node_name, seed_widget_name, model_node_name, model_widget_name,
                   output_format, webp_lossless, quality, separator, prompt=None, extra_pnginfo=None):
        
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
        
        # 2. Seed (si seed_node_name n'est pas vide)
        if seed_node_name and prompt:
            seed_value = self._extract_widget(prompt, seed_node_name, seed_widget_name)
            if seed_value:
                filename_parts.append(str(seed_value))
        
        # 3. Model name (si model_node_name n'est pas vide)
        if model_node_name and prompt:
            model_name = self._extract_widget(prompt, model_node_name, model_widget_name)
            if model_name:
                model_name = self._clean_model_name(model_name)
                filename_parts.append(model_name)
        
        # 4. Suffix (peut contenir tokens date)
        if suffix:
            suffix = self._parse_date_tokens(suffix)
            filename_parts.append(suffix)
        
        # Construire le nom final
        if not filename_parts:
            filename_parts = ["output"]
        
        filename_base = separator.join(filename_parts)
        
        # Nettoyer le nom de fichier des caractères invalides
        filename_base = self._safe_path(filename_base) if filename_base else filename_base
        
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
            
            # Ajouter les métadonnées (prompt et workflow) dans EXIF
            if not args.disable_metadata:
                exif = img.getexif()
                if prompt is not None:
                    # Ajouter le prompt dans EXIF tag "Make"
                    exif[0x010f] = "Prompt:" + json.dumps(prompt)
                if extra_pnginfo is not None:
                    # Ajouter le workflow dans EXIF tag "ImageDescription"
                    exif[0x010e] = "Workflow:" + json.dumps(extra_pnginfo["workflow"])
            
            # Sauvegarder selon le format
            if output_format == "webp":
                if not args.disable_metadata:
                    img.save(filepath, lossless=webp_lossless, quality=quality, method=6, exif=exif.tobytes())
                else:
                    img.save(filepath, lossless=webp_lossless, quality=quality, method=6)
            elif output_format in ["jpg", "jpeg"]:
                if not args.disable_metadata:
                    img.save(filepath, quality=quality, exif=exif.tobytes())
                else:
                    img.save(filepath, quality=quality)
            else:  # PNG
                if not args.disable_metadata:
                    # PNG utilise pnginfo au lieu de exif
                    from PIL import PngImagePlugin
                    metadata = PngImagePlugin.PngInfo()
                    if prompt is not None:
                        metadata.add_text("prompt", json.dumps(prompt))
                    if extra_pnginfo is not None:
                        metadata.add_text("workflow", json.dumps(extra_pnginfo["workflow"]))
                    img.save(filepath, pnginfo=metadata)
                else:
                    img.save(filepath)
            
            saved_paths.append(filepath)
            print(f"💾 Image sauvegardée: {filepath}")
        
        # Retourner les images et le chemin du premier fichier
        return (images, saved_paths[0] if saved_paths else "")
    
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
    
    def _extract_widget(self, prompt, node_name, widget_name):
        """
        Extrait la valeur d'un widget depuis le prompt.
        Supporte deux modes:
        - Par class_type: node_name="KSampler" cherche tous les nodes de ce type
        - Par ID direct: node_name="#10" cible directement le node avec l'ID 10
        """
        if not prompt or not node_name or not widget_name:
            return None
        
        # Mode #ID : cibler directement un node par son ID
        if node_name.startswith("#"):
            try:
                target_id = node_name[1:]  # Enlever le #
                if target_id in prompt:
                    node_data = prompt[target_id]
                    inputs = node_data.get("inputs", {})
                    
                    # Chercher le widget
                    if widget_name in inputs:
                        value = inputs[widget_name]
                        return self._extract_value_from_input(value)
            except:
                pass
            return None
        
        # Mode class_type : chercher par nom de classe (comportement original)
        for node_id in prompt:
            node_data = prompt[node_id]
            class_type = node_data.get("class_type", "")
            
            # Vérifier si c'est le bon type de node
            if node_name.lower() in class_type.lower():
                inputs = node_data.get("inputs", {})
                
                # Chercher le widget
                if widget_name in inputs:
                    value = inputs[widget_name]
                    return self._extract_value_from_input(value)
        
        return None
    
    def _extract_value_from_input(self, value):
        """Extrait la valeur d'un input selon son type"""
        if isinstance(value, dict):
            if "on" in value and not value.get("on", True):
                return None
            # Extraire la première valeur non-"on"
            for key, val in value.items():
                if key != "on" and val:
                    return str(val)
        elif not isinstance(value, (list, dict)):
            return str(value)
        return None
    
    def _clean_model_name(self, model_name):
        """
        Nettoie le nom du modèle:
        - Retire l'extension .safetensors, .ckpt, .pt
        - Retire le chemin si présent
        """
        # Retirer le chemin (Windows et Unix)
        model_name = os.path.basename(model_name)
        
        # Retirer les extensions connues
        extensions = ['.safetensors', '.ckpt', '.pt', '.pth', '.bin']
        for ext in extensions:
            if model_name.lower().endswith(ext):
                model_name = model_name[:-len(ext)]
                break
        
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
