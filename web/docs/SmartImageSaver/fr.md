# Smart Image Saver 💾

Un sauvegarder d'images intelligent qui remplace le subgraph SAVE_IMG avec personnalisation flexible du nom de fichier.

**Catégorie:** `TOO-Pack/image`

---

## 📋 Fonctionnalités

- **Nommage flexible** : Préfixe, suffixe et séparateur personnalisables
- **Tokens de date** : Support de YYYY, MM, DD, HH, mm, ss, timestamp
- **Extraction intelligente** : Extrait automatiquement seed et nom du modèle
- **Ciblage de nodes** : Cible par nom de classe ou ID direct (#10)
- **Formats multiples** : WEBP (lossy/lossless), PNG, JPG/JPEG
- **Préservation métadonnées** : Sauvegarde prompt et workflow en EXIF/PNG info
- **Auto-incrément** : Évite l'écrasement des fichiers existants

---

## ⚙️ Paramètres

### Paramètres obligatoires

| Paramètre | Type | Description | Défaut |
|-----------|------|-------------|--------|
| **images** | <span style="background-color:#7c2d12;color:#fb923c;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">IMAGE</span> | Images à sauvegarder | - |
| **output_folder** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Dossier de sortie (supporte tokens date) | `YYYY-MM-DD` |
| **prefix** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Préfixe du nom (supporte tokens date) | `ComfyUI_YYYY-MM-DD_HHmmss` |
| **seed_node_name** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Node contenant le seed (classe ou #ID) | `KSampler` |
| **seed_widget_name** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Nom du widget pour le seed | `seed` |
| **model_node_name** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Node contenant le modèle (classe ou #ID) | `CheckpointLoaderSimple` |
| **model_widget_name** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Nom du widget pour le modèle | `ckpt_name` |
| **suffix** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Suffixe du nom (supporte tokens date) | `""` |
| **output_format** | <span style="background-color:#4a5568;color:#a0aec0;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">COMBO</span> | Format de l'image | `webp` |
| **webp_lossless** | <span style="background-color:#7c3aed;color:#a78bfa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">BOOLEAN</span> | Mode WEBP sans perte (fichiers plus lourds) | `False` |
| **quality** | <span style="background-color:#1e4d3e;color:#34d399;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">INT</span> | Qualité de compression (1-100) | `97` |
| **separator** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Séparateur entre les éléments du nom | `_` |

### Sorties

| Paramètre | Type | Description |
|-----------|------|-------------|
| **images** | <span style="background-color:#7c2d12;color:#fb923c;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">IMAGE</span> | Retour des images en entrée |
| **filepath** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Chemin du premier fichier sauvegardé |

---

## 🎯 Structure du nom de fichier

Le node construit le nom dans cet ordre :

```
[prefix]_[seed]_[nom_modèle]_[suffix].[format]
```

Les éléments sont joints par le séparateur. Les éléments vides sont ignorés.

**Exemples de sortie :**
- `render_2024-01-30_123456_mymodel_final.webp`
- `ComfyUI_2024-01-30_143025_987654_sd15.png`
- `test_500_juggernaut_v9.jpg`

---

## 💡 Exemples d'utilisation

### Cas 1 : Usage basique avec dossier daté
```python
output_folder = "YYYY-MM-DD"           # → 2024-01-30/
prefix = "render_YYYYMMDD"              # → render_20240130
seed_node_name = "KSampler"
model_node_name = "CheckpointLoaderSimple"
```
**Sortie :** `2024-01-30/render_20240130_123456_mymodel.webp`

### Cas 2 : Cibler un node par ID
```python
seed_node_name = "#10"                  # Cible le node ID 10
model_node_name = "#5"                  # Cible le node ID 5
```

### Cas 3 : Désactiver seed ou modèle
```python
seed_node_name = ""                     # N'inclut pas le seed
model_node_name = ""                    # N'inclut pas le modèle
prefix = "my_render"
suffix = "HHmmss"                       # Ajoute timestamp
```
**Sortie :** `my_render_143025.webp`

### Cas 4 : Organisation par projet
```python
output_folder = "projects/character_design/YYYY-MM-DD"
prefix = "char"
suffix = "v1"
```
**Sortie :** `projects/character_design/2024-01-30/char_123456_model_v1.webp`

### Cas 5 : PNG haute qualité
```python
output_format = "png"
# PNG ignore les réglages quality et webp_lossless
```

### Cas 6 : WEBP sans perte
```python
output_format = "webp"
webp_lossless = True                    # Plus lourd mais sans perte
# quality est ignoré quand lossless=True
```

---

## 📅 Tokens de date

Tous les tokens sont remplacés par les valeurs date/heure actuelles :

| Token | Description | Exemple |
|-------|-------------|---------|
| `YYYY` | Année (4 chiffres) | 2024 |
| `YY` | Année (2 chiffres) | 24 |
| `MM` | Mois (2 chiffres) | 01 |
| `DD` | Jour (2 chiffres) | 30 |
| `HH` | Heure 24h (2 chiffres) | 14 |
| `mm` | Minute (2 chiffres) | 30 |
| `ss` | Seconde (2 chiffres) | 25 |
| `timestamp` | Timestamp Unix | 1706623825 |

**Exemples :**
- `YYYY-MM-DD` → `2024-01-30`
- `YYYYMMDD_HHmmss` → `20240130_143025`
- `backup_timestamp` → `backup_1706623825`

---

## 🎯 Ciblage de nodes

Deux méthodes pour cibler les nodes :

### Par nom de classe (défaut)
```python
seed_node_name = "KSampler"              # Trouve n'importe quel KSampler
model_node_name = "CheckpointLoaderSimple"
```
- Recherche insensible à la casse
- Trouve le premier node correspondant

### Par ID de node (précis)
```python
seed_node_name = "#10"                   # Cible le node ID 10
model_node_name = "#5"                   # Cible le node ID 5
```
- Ciblage direct par ID
- Utile avec plusieurs nodes du même type
- IDs visibles dans le workflow ComfyUI

---

## 🔧 Détails techniques

### Nettoyage du nom de modèle

Le node nettoie automatiquement les noms :
- Retire le chemin : `/models/checkpoints/model.safetensors` → `model`
- Retire les extensions : `.safetensors`, `.ckpt`, `.pt`, `.pth`, `.bin`

### Sécurité des fichiers

- Caractères invalides retirés automatiquement
- Fichiers existants jamais écrasés (auto-incrément : `_001`, `_002`, etc.)
- Noms de dossiers vides gérés correctement

### Stockage des métadonnées

**WEBP/JPG :** Métadonnées en tags EXIF
- Tag 0x010f (Make) : Prompt JSON
- Tag 0x010e (ImageDescription) : Workflow JSON

**PNG :** Métadonnées en chunks PNG info
- `prompt` : Prompt JSON
- `workflow` : Workflow JSON

Métadonnées désactivables avec `--disable-metadata` de ComfyUI.

### Lots d'images multiples

Lors de la sauvegarde de plusieurs images :
```
render_0000.webp
render_0001.webp
render_0002.webp
```

---

## 📂 Formats de sortie

| Format | Description | Qualité | Cas d'usage |
|--------|-------------|---------|-------------|
| **WEBP** | Format moderne, bonne compression | Lossy/Lossless | Recommandé pour la plupart des cas |
| **PNG** | Sans perte, fichiers lourds | Toujours lossless | Exports finaux, transparence |
| **JPG/JPEG** | Avec perte, fichiers légers | Lossy | Partage web, stockage limité |

---

## 🔧 Dépannage

### ❌ Seed/Modèle n'apparaît pas dans le nom
- Vérifiez que les noms de nodes correspondent à votre workflow
- Essayez le format `#ID` pour cibler des nodes spécifiques
- Vérifiez les noms de widgets (`seed`, `ckpt_name`, etc.)
- Laissez vide pour désactiver cet élément

### ❌ Caractères invalides dans le nom
- Le node retire automatiquement les caractères invalides
- Si problème persiste, évitez les caractères spéciaux

### ⚠️ Fichiers écrasés
- Le node empêche l'écrasement avec auto-incrément
- Si échec, vérifiez les permissions du dossier

---

## 📝 Notes

- Tous les tokens date fonctionnent dans `output_folder`, `prefix` et `suffix`
- `seed_node_name` ou `model_node_name` vide désactive cet élément
- Recherches de nodes insensibles à la casse
- WEBP lossless ignore le réglage quality
- Format PNG ignore quality et lossless

---

## 📄 License

MIT

---

## 🙏 Crédits

- **ComfyUI** - Framework node-based
- **PIL/Pillow** - Manipulation d'images
- **PyTorch** - Opérations tensorielles
