import os
import json
import subprocess
from pathlib import Path
import folder_paths

class CollectionCategorizer:
    """
    Scanne un dossier et catégorise le contenu avec un LLM local (Ollama)
    Compatible avec le format JSON du Collection Manager
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "ollama_model": (["qwen2.5:7b", "gemma3:12b", "llama3.1:8b", "gemma3:4b", "llama3:8b", "custom"], {"default": "qwen2.5:7b"}),
                "custom_ollama_model": ("STRING", {"default": "", "multiline": False, "placeholder": "Ex: mistral:7b, llama3:8b..."}),
                "folder_path": ("STRING", {"default": "", "multiline": False}),
                "scan_subfolders": ("BOOLEAN", {"default": False}),
                "save_json": ("BOOLEAN", {"default": True}),
                "collection_title": ("STRING", {"default": "Ma Collection", "multiline": False}),
                "content_type": (["films", "mangas", "anime", "series", "books", "games", "custom"], {"default": "films"}),
            },
            "optional": {
                "custom_type_name": ("STRING", {"default": "", "multiline": False, "placeholder": "Ex: Documentaires, Podcasts..."}),
                "custom_categories": ("STRING", {"default": "", "multiline": True, "placeholder": "Ex: Genre, Année, Studio, Thème...\nLaisse vide = LLM décide"}),
				"seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff, "tooltip": "Seed pour résultats reproductibles (0 = aléatoire)"}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING",)
    RETURN_NAMES = ("json_output", "summary",)
    FUNCTION = "categorize_collection"
    CATEGORY = "🔵TOO-Pack/utils"
    OUTPUT_NODE = True

    def scan_folder(self, folder_path: str, scan_subfolders: bool = False):
        """Scanne le dossier et liste tous les items."""
        items = []
        video_extensions = {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv'}
        archive_extensions = {'.cbz', '.cbr', '.zip', '.rar'}
        doc_extensions = {'.epub', '.pdf', '.mobi'}
        
        folder = Path(folder_path)
        if not folder.exists():
            return []
        
        def scan_directory(directory: Path, relative_path: str = ""):
            """Fonction récursive pour scanner un répertoire."""
            for item in sorted(directory.iterdir()):
                if item.is_file():
                    stem = item.stem
                    ext = item.suffix.lower()
                    
                    # Fichiers vidéo, archives, docs
                    if ext in video_extensions or ext in archive_extensions or ext in doc_extensions:
                        # Avec sous-dossiers : préfixer par le chemin relatif
                        if relative_path:
                            items.append(f"{relative_path}/{stem}")
                        else:
                            items.append(stem)
                        
                elif item.is_dir():
                    if scan_subfolders:
                        # Scanner récursivement
                        new_relative = f"{relative_path}/{item.name}" if relative_path else item.name
                        scan_directory(item, new_relative)
                    else:
                        # Chaque sous-dossier = un item (comportement par défaut)
                        items.append(item.name)
        
        scan_directory(folder)
        return items

    def build_prompt(self, items: list, content_type: str, custom_categories: str = ""):
        """Construit le prompt pour le LLM."""
        
        categories_hint = custom_categories if custom_categories else "genres principaux, époques"
        
        items_count = len(items)
        
        prompt = f"""Tu es un expert en classification de {content_type}.

LISTE COMPLÈTE ({items_count} titres) à catégoriser :
{json.dumps(items, ensure_ascii=False, indent=2)}

TÂCHE : Classe TOUS ces {items_count} titres par {categories_hint}.

RÈGLES STRICTES :
1. CHAQUE titre doit apparaître dans EXACTEMENT UNE catégorie
2. Utilise les titres EXACTEMENT comme fournis (copie-colle)
3. Crée entre 3 et 8 catégories génériques (ex: "Science Fiction", "Comédie", "Action")
4. NE crée PAS de catégories avec le nom d'une série spécifique
5. Les catégories doivent être des GENRES/THÈMES larges, pas des titres individuels
6. Vérifie que le total des titres = {items_count}

FORMAT JSON (sans texte avant/après) :
{{
  "categories": {{
    "Nom Catégorie Générique 1": ["Titre exact A", "Titre exact B"],
    "Nom Catégorie Générique 2": ["Titre exact C", "Titre exact D"]
  }}
}}

IMPORTANT : 
- Pas de catégorie avec un seul titre
- Regroupe intelligemment
- Total titres dans categories = {items_count}

JSON uniquement :"""
        
        return prompt

    def call_ollama(self, prompt: str, model: str = "qwen2.5:7b", seed: int = 0):
        """Appelle Ollama via API HTTP et retourne la réponse JSON."""
        import requests
        
        try:
            # Configuration de la requête
            url = "http://localhost:11434/api/generate"
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "format": "json"
            }
            
            # Ajouter le seed si spécifié
            if seed > 0:
                payload["options"] = {"seed": seed}
            
            response = requests.post(url, json=payload, timeout=120)
            
            if response.status_code != 200:
                return None, f"Erreur API Ollama: {response.status_code}"
            
            result = response.json()
            llm_response = result.get("response", "")
            
            # Extraction du JSON
            start = llm_response.find('{')
            end = llm_response.rfind('}') + 1
            
            if start == -1 or end == 0:
                return None, f"Pas de JSON trouvé dans la réponse"
            
            json_str = llm_response[start:end]
            parsed = json.loads(json_str)
            
            return parsed, None
            
        except requests.exceptions.Timeout:
            return None, "Timeout Ollama (>120s)"
        except requests.exceptions.ConnectionError:
            return None, "Impossible de se connecter à Ollama (localhost:11434)"
        except json.JSONDecodeError as e:
            return None, f"JSON invalide : {str(e)}"
        except Exception as e:
            return None, f"Erreur Ollama : {str(e)}"

    def build_collection_json(self, title: str, items: list, llm_result: dict, 
                            folder_path: str, content_type: str):
        """Construit le JSON final compatible Collection Manager."""
        
        llm_categories = llm_result.get("categories", {})
        
        # Construction du format Collection Manager
        categories = []
        cat_id = 1
        
        for cat_name, cat_items in llm_categories.items():
            categories.append({
                "id": cat_id,
                "name": cat_name,
                "subcategories": [],
                "games": cat_items  # Oui "games" même pour films/anime
            })
            cat_id += 1
        
        # Icône selon le type
        icons = {
            "films": "🎬",
            "mangas": "📚", 
            "anime": "🎬",
            "series": "📺",
            "books": "📖",
            "games": "🎮",
            "custom": "📁"
        }
        
        return {
            "title": title,
            "icon": icons.get(content_type, "📁"),
            "type": content_type.capitalize(),
            "filename": f"{content_type}.json",
            "categories": categories
        }

    def categorize_collection(self, folder_path: str, collection_title: str, 
                             content_type: str, ollama_model: str,
                             custom_ollama_model: str = "",
                             save_json: bool = True,
                             scan_subfolders: bool = False,
                             custom_type_name: str = "",
                             custom_categories: str = "",
                             seed: int = 0):
        
        # Gestion du modèle custom
        if ollama_model == "custom":
            if not custom_ollama_model:
                return (json.dumps({"error": "Modèle custom nécessite custom_ollama_model"}, indent=2), 
                       "❌ Erreur : spécifie un nom de modèle Ollama")
            ollama_model = custom_ollama_model
        
        # Gestion du type custom
        if content_type == "custom":
            if not custom_type_name:
                return (json.dumps({"error": "Type custom nécessite custom_type_name"}, indent=2), 
                       "❌ Erreur : spécifie un nom pour le type custom")
            content_type = custom_type_name.lower()
        
        # 1. Scan du dossier
        items = self.scan_folder(folder_path, scan_subfolders)
        
        if not items:
            summary = f"❌ Aucun item trouvé dans {folder_path}"
            return (json.dumps({"error": "Empty folder"}, indent=2), summary)
        
        summary = f"📁 {len(items)} items trouvés"
        if scan_subfolders:
            summary += " (incluant sous-dossiers)\n"
        else:
            summary += "\n"
        
        # 2. Appel au LLM
        prompt = self.build_prompt(items, content_type, custom_categories)
        llm_result, error = self.call_ollama(prompt, ollama_model, seed)
        
        if error:
            summary += f"❌ Erreur LLM : {error}"
            return (json.dumps({"error": error}, indent=2), summary)
        
        # 3. Validation : vérifier que tous les items sont catégorisés
        llm_categories = llm_result.get("categories", {})
        categorized_items = []
        for cat_items in llm_categories.values():
            categorized_items.extend(cat_items)
        
        missing_items = set(items) - set(categorized_items)
        if missing_items:
            summary += f"⚠️ {len(missing_items)} items non catégorisés: {list(missing_items)[:3]}\n"
        
        # 4. Construction du JSON final
        collection_json = self.build_collection_json(
            collection_title, items, llm_result, folder_path, content_type
        )
        
        summary += f"✓ {len(collection_json.get('categories', []))} catégories créées\n"
        summary += f"✓ {len(categorized_items)}/{len(items)} items catégorisés\n"
        summary += f"✓ Modèle : {ollama_model}\n"
        if seed > 0:
            summary += f"✓ Seed : {seed} (reproductible)\n"
        
        json_output = json.dumps(collection_json, ensure_ascii=False, indent=2)
        
        # 5. Sauvegarde auto
        if save_json:
            output_path = Path(folder_path) / f"{content_type}.json"
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(json_output)
                summary += f"✓ Sauvegardé : {output_path}"
            except Exception as e:
                summary += f"\n❌ Erreur sauvegarde : {str(e)}"
        else:
            summary += "✓ JSON prêt (pas de sauvegarde auto)"
        
        return (json_output, summary)


NODE_CLASS_MAPPINGS = {
    "CollectionCategorizer": CollectionCategorizer
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CollectionCategorizer": "🗂️ Collection Categorizer (LLM)"
}