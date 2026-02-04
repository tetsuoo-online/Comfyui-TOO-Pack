# Smart Image Loader 🖼️

Un chargeur d'images flexible qui supporte plusieurs sources d'entrée avec ordre de priorité.

**Catégorie:** `TOO-Pack/image`

---

## 📋 Fonctionnalités

- **Sources multiples** : txt, chemin direct, dossier, ou image directe
- **Ordre de priorité** intelligent et configurable
- **Sélection aléatoire** avec seed reproductible
- **Formats multiples** supportés (PNG, JPG, JPEG, BMP, WEBP, TIFF)
- **Gestion d'erreurs** robuste
- **Retour du chemin** du fichier chargé

---

## ⚙️ Paramètres

### Paramètres obligatoires

| Paramètre | Type | Description | Défaut |
|-----------|------|-------------|--------|
| **seed** | <span style="background-color:#1e4d3e;color:#34d399;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">INT</span> | Seed pour sélection aléatoire reproductible | `0` |
| **img_dir_level** | <span style="background-color:#1e4d3e;color:#34d399;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">INT</span> | Profondeur de sous-dossiers : -1=tous, 0=courant, 1-10=niveaux | `0` |

### Paramètres optionnels

| Paramètre | Type | Description | Défaut |
|-----------|------|-------------|--------|
| **txt_path** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Chemin vers fichier texte contenant des chemins d'images | - |
| **img_path** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Chemin direct vers un fichier image | - |
| **img_directory** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Chemin vers un dossier contenant des images | - |
| **image** | <span style="background-color:#7c2d12;color:#fb923c;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">IMAGE</span> | Image directe en entrée | - |

### Sorties

| Paramètre | Type | Description |
|-----------|------|-------------|
| **IMAGE** | <span style="background-color:#7c2d12;color:#fb923c;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">IMAGE</span> | L'image chargée sous forme de tenseur |
| **FILE_PATH** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Chemin du fichier chargé ("external_input" ou "none") |

---

## 🎯 Ordre de priorité

Le node charge l'image selon cet ordre (du plus prioritaire au moins prioritaire) :

1. **txt_path** 📄 : Sélectionne aléatoirement un chemin depuis le fichier texte
2. **img_path** 🖼️ : Charge le fichier image spécifique
3. **img_directory** 📁 : Sélectionne aléatoirement une image du dossier
4. **image** ⚡ : Utilise l'image fournie en entrée

---

## 💡 Exemples d'utilisation

### Cas 1 : Fichier texte avec liste d'images
```python
# Contenu de image_list.txt :
# /path/to/image1.png
# /path/to/image2.jpg
# /path/to/image3.webp

txt_path = "/path/to/image_list.txt"
seed = 42  # Reproductible
```
➜ Sélectionne aléatoirement une image de la liste

### Cas 2 : Chemin direct vers une image
```python
img_path = "/path/to/specific/image.png"
```
➜ Charge directement cette image

### Cas 3 : Dossier d'images
```python
img_directory = "/path/to/images/"
seed = 123
```
➜ Sélectionne aléatoirement une image du dossier

### Cas 4 : Image en entrée directe
```python
# Connecter une IMAGE depuis un autre node
image = <IMAGE depuis autre node>
```
➜ Utilise l'image fournie

### Cas 5 : Combinaison avec priorité
```python
txt_path = "/path/to/list.txt"       # Priorité 1
img_path = "/path/to/fallback.png"   # Priorité 2 (si txt_path échoue)
img_directory = "/path/to/backup/"   # Priorité 3 (si img_path échoue)
```
➜ Utilise la première source valide trouvée

---

## 📂 Formats supportés

| Extension | Description |
|-----------|-------------|
| `.png` | Portable Network Graphics |
| `.jpg`, `.jpeg` | JPEG |
| `.bmp` | Bitmap |
| `.webp` | WebP |
| `.tiff` | Tagged Image File Format |

---

## 🔧 Détails techniques

### Format de fichier texte (txt_path)

Le fichier texte doit contenir un chemin d'image par ligne :

```
/home/user/images/photo1.png
/home/user/images/photo2.jpg
/home/user/images/photo3.webp
```

- Les lignes vides sont ignorées
- Encodage UTF-8 supporté
- Un chemin aléatoire est sélectionné via le seed

### Gestion du seed

- **seed = 0** : Sélection aléatoire différente à chaque exécution
- **seed > 0** : Sélection identique avec les mêmes paramètres (reproductible)

### Valeurs de FILE_PATH

| Valeur | Description |
|--------|-------------|
| Chemin complet | Image chargée depuis txt_path, img_path ou img_directory |
| `"external_input"` | Image fournie via le paramètre image |
| `"none"` | Aucune source valide trouvée (erreur) |

---

## 🔧 Dépannage

### ❌ "No valid image source found"
- Vérifiez qu'au moins un paramètre optionnel est fourni
- Vérifiez que les chemins existent et sont accessibles
- Vérifiez les permissions de lecture

### ❌ "Error loading image"
- Vérifiez que le fichier est bien une image valide
- Vérifiez le format (doit être dans la liste supportée)
- Vérifiez que le fichier n'est pas corrompu

### ❌ "Error reading txt_path"
- Vérifiez que le fichier texte existe
- Vérifiez l'encodage (UTF-8 recommandé)
- Vérifiez que les chemins dans le fichier sont valides

### ⚠️ Image toujours identique
- Augmentez la valeur du seed pour varier la sélection
- Vérifiez que vous avez plusieurs images dans votre source

---

## 📝 Notes

- Le node convertit automatiquement toutes les images en RGB
- Les images sont normalisées (valeurs 0-1) pour ComfyUI
- Le seed affecte uniquement txt_path et img_directory (sélection aléatoire)
- img_path et image input ne sont pas affectés par le seed

---

## 📄 License

MIT

---

## 🙏 Crédits

- **ComfyUI** - Framework node-based
- **PIL/Pillow** - Manipulation d'images
- **PyTorch** - Tenseurs pour ComfyUI

---

## 📧 Contact

Pour signaler un bug ou suggérer une amélioration :
- Créez une issue
- Proposez une PR
