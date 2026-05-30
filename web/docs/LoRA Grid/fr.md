# TOO LoRA Grid 🧪

Compare plusieurs LoRAs côte à côte en générant une grille d'images. Chaque cellule correspond à un LoRA différent, avec le même seed et les mêmes paramètres — idéal pour choisir rapidement le bon LoRA ou la bonne force.

**Catégorie :** `TOO-Pack/utils`

---

## 📋 Fonctionnalités

- **Grille comparative** : génère une image par LoRA, assemblées en grille
- **Slot "null"** : inclure une case sans LoRA comme référence
- **Labels automatiques** : nom du LoRA (+ weight si spécifié) affiché sous chaque image
- **Footer** : texte libre sous la grille (prompt, notes, etc.)
- **Cache interne** : les images déjà générées ne sont pas recalculées si rien n'a changé
- **Compatible** SD, SDXL, FLUX, Cosmos/Anima

---

## ⚙️ Entrées

### Connexions

| Entrée | Type | Description |
|--------|------|-------------|
| **model** | MODEL | Modèle de base |
| **clip** | CLIP | Encodeur CLIP |
| **vae** | VAE | VAE pour décoder les latents |
| **positive** | CONDITIONING | Prompt positif |
| **negative** | CONDITIONING | Prompt négatif |
| **latent_image** | LATENT | Latent de départ |

### Paramètres de sampling

| Paramètre | Défaut | Description |
|-----------|--------|-------------|
| **seed** | `0` | Seed de génération |
| **steps** | `20` | Nombre de steps |
| **cfg** | `7.0` | CFG scale |
| **sampler_name** | — | Sampler |
| **scheduler** | — | Scheduler |
| **denoise** | `1.0` | Force de débruitage |

### Liste des LoRAs

Le widget `loras` accepte une entrée par ligne :

```
# commentaire ignoré
chemin/vers/lora.safetensors
chemin/vers/lora.safetensors:0.75
chemin/vers/lora.safetensors:"sans LoRA"
```

| Syntaxe | Résultat |
|---------|----------|
| `nom.safetensors` | LoRA à weight `1.0`, label = nom du fichier |
| `nom.safetensors:0.75` | LoRA à weight `0.75`, label = `nom:0.75` |
| `nom.safetensors:"label"` | Slot null (génère sans LoRA), label personnalisé |

> Les chemins sont relatifs au dossier `loras` de ComfyUI.

### Paramètres de grille

| Paramètre | Défaut | Description |
|-----------|--------|-------------|
| **grid_cols** | `4` | Nombre de colonnes |
| **grid_padding** | `4` | Espacement entre cellules (px) |
| **add_labels** | `True` | Afficher les labels sous les images |
| **label_height** | `24` | Hauteur de la zone label (px) |
| **font_size** | `14` | Taille de police des labels |
| **label_color** | `#ffffff` | Couleur du texte |
| **bg_color** | `#111111` | Couleur de fond de la grille |
| **footer_text** | — | Texte affiché sous la grille (multiligne supporté) |

---

## 📤 Sorties

| Sortie | Type | Description |
|--------|------|-------------|
| **grid** | IMAGE | Grille complète assemblée |
| **images** | IMAGE | Batch de toutes les images individuelles |

---

## 💡 Exemples

### Tester 3 forces différentes pour un même LoRA

```
my_style.safetensors:0.5
my_style.safetensors:0.75
my_style.safetensors:1.0
my_style.safetensors:"référence"
```

La dernière ligne génère une image sans LoRA pour comparer.

### Comparer plusieurs LoRAs

```
styles/lora_A.safetensors
styles/lora_B.safetensors
styles/lora_C.safetensors
styles/lora_C.safetensors:0.5
```

---

## 📝 Notes

- Le cache est basé sur tous les paramètres d'entrée. Modifier uniquement `grid_cols`, `label_color`, etc. (paramètres visuels) ne régénère **pas** les images — seule la grille est reconstruite.
- Les lignes vides et les lignes commençant par `#` sont ignorées.
- Si aucune entrée valide n'est trouvée dans `loras`, le node génère quand même une image sans LoRA.
