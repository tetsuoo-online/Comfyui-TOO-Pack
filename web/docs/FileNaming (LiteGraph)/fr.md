# 💾 TOO Smart Image Saver (Advanced)(LiteGraph)

Nœud permettant la sauvegarde d'image avec système de nommage avancé et des métadonnées compatibles A1111/Civitai Auto V3.

**Catégorie :** TOO-Pack/image

## Fonctionnalités

- Nommage de fichiers dynamique avec extraction depuis le workflow
- Injection/édition de métadonnées
- Support de 3 entrées universelles (`any1`, `any2`, `any3`)
- Extraction automatique du modèle et des LoRAs avec calcul de hash
- Remplacement de texte ciblé
- Formatage de dates personnalisable
- Métadonnées A1111/Civitai compatibles
- Formats de sortie: PNG, JPG, WebP

## Entrées

| Paramètre | Type | Description |
|-----------|------|-------------|
| `images` | IMAGE | Images à sauvegarder (requis) |
| `metadata` | METADATA | Métadonnées optionnelles |
| `workflow` | WORKFLOW | Workflow à embarquer |
| `any1` | * | Entrée universelle 1 |
| `any2` | * | Entrée universelle 2 |
| `any3` | * | Entrée universelle 3 |

## Sorties

| Sortie | Type | Description |
|--------|------|-------------|
| `images` | IMAGE | Images passthrough |
| `filepath` | STRING | Chemin du fichier sauvegardé |

## Configuration (Interface JS)

### DATA
Créez des champs de données personnalisés pour les métadonnées et le nommage.

**Formats de valeur:**
- **Texte statique:** `"mon_texte"`
- **Extraction widget:** `#123:widget_name` (node ID) ou `ClassName:widget_name`
- **Entrée any:** `[any1]`, `[any2]`, `[any3]`

**Exemple:**
```
name: positive
value: #45:text

name: model_used
value: [any1]
```

### DATE FORMAT
Formatez les dates pour le nommage.

- **date1:** Format de date (ex: `YYYY-MM-DD`)
- **date2:** Format d'heure (ex: `HHmmss`)
- **date3:** Format personnalisé

**Tokens disponibles:** `YYYY`, `YY`, `MM`, `DD`, `HH`, `mm`, `ss`, `timestamp`

### MODEL
Extraction automatique du modèle.

**Valeur:** `#123:ckpt_name` ou `[any1]`

Le node calcule automatiquement:
- Nom du modèle (basename sans extension)
- Hash du modèle (10 premiers caractères SHA256)

### LORAS
Extraction automatique des LoRAs avec hash compatible Civitai.

**Ajoutez plusieurs loras:**
- Lora 1: `#45:lora_name` ou `[any1]`
- Lora 2: `#67:lora_name` ou `[any2]`

**Support multiline:** Si `[any1]` contient:
```
lora1.safetensors
lora2.safetensors
```
→ Les deux sont parsés automatiquement

### TEXT REPLACE
Remplacez du texte dans les champs avant le nommage.

**Target:**
- Vide ou `[any1]`/`[any2]`/`[any3]` → Applique à tous les champs
- `positive` → Applique uniquement au champ "positive"
- `model` → Applique uniquement au modèle

**Exemple:**
```
target: positive
in: (masterpiece)
out: 
```
→ Retire "(masterpiece)" du prompt positif

### NAMING
Construisez le nom de fichier avec les éléments disponibles.

**Champs disponibles:**
- `output_folder` : Sous-dossier de sortie
- `prefix` : Préfixe du fichier
- `extra1`, `extra2`, `extra3` : Champs supplémentaires
- `model` : Nom du modèle
- `suffix` : Suffixe du fichier
- `separator` : Caractère de séparation (défaut: `_`)

**Sources disponibles:**
- Vide (ignoré)
- `[any1]`, `[any2]`, `[any3]` : Entrées universelles
- Nom de data field : `positive`, `seed`, `steps`, etc.
- `model`, `loras` : Valeurs extraites
- `%date1`, `%date2`, `%date3` : Dates formatées

**Exemple de naming:**
```
prefix: %date1
extra1: positive
model: model
suffix: seed
separator: _
```
→ `2025-02-12_beautiful_landscape_MyModel_12345.webp`

### OUTPUT
Configuration de sortie.

- **format:** `png`, `jpg`, `webp`
- **quality:** 1-100 (pour jpg/webp)
- **save metadata:** Inclure les métadonnées A1111
- **embed workflow:** Embarquer le workflow ComfyUI (sauf JPG)

## Exemples d'Utilisation

### Exemple 1 : Nommage avec modèle et seed

**Configuration:**
```
DATA:
  - name: seed, value: #10:seed

MODEL:
  - extract: KSampler:ckpt_name

NAMING:
  - prefix: %date1
  - model: model
  - suffix: seed
  - separator: _
```

**Résultat:** `2025-02-12_MyCheckpoint_8675309.webp`

### Exemple 2 : Extraction de LoRAs depuis any1

**Workflow:**
```
ExtractWidgetFromNode → any1 (TOO Smart Image Saver)
```

**Configuration:**
```
LORAS:
  - lora 1: [any1]

NAMING:
  - prefix: %date1
  - extra1: loras
```

**Si any1 contient:**
```
style_lora_v2.safetensors
quality_lora_v1.safetensors
```

**Métadonnées générées:**
```
Lora hashes: "style_lora_v2: a1b2c3d4e5f6, quality_lora_v1: f6e5d4c3b2a1"
```

### Exemple 3 : Nettoyage du prompt avec Text Replace

**Configuration:**
```
TEXT REPLACE:
  - target: positive
  - in: (masterpiece, best quality)
  - out: 

NAMING:
  - prefix: positive
```

**Si positive = "beautiful landscape, (masterpiece, best quality)"**  
**→ Filename:** `beautiful_landscape.webp`

## Cas d'Usage Pratiques

### 1. Workflow avec Multiple LoRAs
Utilisez `ExtractWidgetFromNode` pour récupérer tous les LoRAs utilisés → connectez à `any1` → Le node calcule automatiquement tous les hashes pour compatibilité Civitai.

### 2. Organisation par Modèle
Configurez `output_folder: model` pour trier automatiquement les images par modèle utilisé.

### 3. Métadonnées Complètes
Créez des data fields pour tous les paramètres importants (seed, steps, cfg, sampler, scheduler) → Le node génère des métadonnées A1111 complètes lisibles par Civitai et Automatic1111.

### 4. Nommage Intelligent
Utilisez les entrées `any` pour injecter des informations dynamiques depuis d'autres nodes (tags, descriptions, scores, etc.).

## Conseils

- Les **data fields** sont flexibles : créez autant de champs que nécessaire
- **[any1]**, **[any2]**, **[any3]** acceptent n'importe quel type de données (converties en string)
- Le **multiline** est supporté pour les loras : une ligne = un lora
- Les **hashes** des loras excluent les métadonnées safetensors (compatible Civitai AutoV3)
- Le **text replace** s'applique sur les valeurs extraites avant la construction du nom de fichier
- Les **lignes vides** dans les data fields sont automatiquement ignorées
- L'entrée **metadata** a la priorité sur les data fields du node, sauf si les data fields sont explicitement renseignés (permet l'injection/édition de métadonnées)
