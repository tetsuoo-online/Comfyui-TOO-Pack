# Extract Widget From Node 🔧

Extrait les valeurs de widgets spécifiques depuis n'importe quel node dans le workflow ComfyUI.

**Catégorie:** `TOO-Pack/utils`

---

## 📋 Fonctionnalités

- **Extraction ciblée** de widgets spécifiques par nom
- **Compatible** avec tous les nodes ComfyUI
- **Extraction multiple** : plusieurs widgets en une fois
- **Mode auto** : extrait tous les widgets si aucun n'est spécifié
- **Gestion intelligente** des dictionnaires et valeurs imbriquées
- **Filtre "on"** : ignore les widgets désactivés

---

## ⚙️ Paramètres

### Paramètres obligatoires

| Paramètre | Type | Description | Défaut |
|-----------|------|-------------|--------|
| **node_name** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Nom du type de node (ex: "Power Lora Loader") OU ID du node (ex: "#180" ou "#45:180" pour subgraph) | `Power Lora Loader` |
| **widget_names** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Noms des widgets à extraire (séparés par virgules) | `lora, strength` |

### Paramètres cachés

| Paramètre | Type | Description |
|-----------|------|-------------|
| **extra_pnginfo** | <span style="background-color:#2d3748;color:#a0aec0;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">EXTRA_PNGINFO</span> | Métadonnées PNG du workflow |
| **prompt** | <span style="background-color:#2d3748;color:#a0aec0;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">PROMPT</span> | Données du workflow actuel |
| **unique_id** | <span style="background-color:#2d3748;color:#a0aec0;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">UNIQUE_ID</span> | ID unique du node |

### Sorties

| Paramètre | Type | Description |
|-----------|------|-------------|
| **STRING** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Valeurs extraites (une par ligne, séparées par `\n`) |

---

## 💡 Exemples d'utilisation

### Cas 1 : Extraire des widgets spécifiques d'un Power Lora Loader (rgthree)
```python
node_name = "Power Lora Loader"
widget_names = "lora, strength"
```
**Sortie :**
```
my_lora_v1.safetensors
0.85
```

### Cas 1b : Extraire des widgets d'un LoraLoader standard
```python
node_name = "LoraLoader"
widget_names = "lora_name, strength_model"
```
**Sortie :**
```
my_lora_v1.safetensors
0.85
```

### Cas 2 : Extraire plusieurs paramètres d'un KSampler
```python
node_name = "KSampler"
widget_names = "seed, steps, cfg"
```
**Sortie :**
```
123456789
20
7.5
```

### Cas 3 : Extraire tous les widgets (mode auto)
```python
node_name = "CheckpointLoaderSimple"
widget_names = ""  # Vide = tout extraire
```
**Sortie :**
```
model_name.safetensors
```

### Cas 4 : Extraire depuis plusieurs nodes du même type
```python
node_name = "Power Lora Loader"
widget_names = "lora_name"
```
**Sortie (si 3 Lora Loaders dans le workflow) :**
```
lora1.safetensors
lora2.safetensors
lora3.safetensors
```

### Cas 5 : Utiliser la sortie dans un autre node
```python
# Connecter la sortie STRING à un node de texte
# Exemple : Save Text, String Literal, etc.
```

### Cas 6 : Cibler un node spécifique par ID
```python
node_name = "#180"  # Node unique
# ou
node_name = "#45:180"  # Node 180 dans le subgraph 45
widget_names = "lora, strength"
```

---

## 🎯 Détails techniques

### Recherche de node

Le node effectue une recherche **insensible à la casse** sur `node_name` :
- `"power lora"` trouvera `"Power Lora Loader"`
- `"ksampler"` trouvera `"KSampler"` et `"KSamplerAdvanced"`

### Format de widget_names

Les noms de widgets doivent être **séparés par des virgules** :
```python
"widget1, widget2, widget3"
```

Les espaces sont automatiquement supprimés :
```python
"lora_name,strength_model,strength_clip"  # OK
"lora_name, strength_model, strength_clip"  # OK aussi
```

### Gestion des valeurs imbriquées

Le node gère intelligemment les dictionnaires imbriqués :

**Structure simple :**
```json
{
  "lora_name": "my_lora.safetensors",
  "strength_model": 0.85
}
```

**Structure imbriquée (Power Lora Loader) :**
```json
{
  "loras": {
    "on": true,
    "lora_name": "my_lora.safetensors",
    "strength_model": 0.85
  }
}
```

Le node extrait automatiquement les valeurs des deux structures.

### Filtre "on"

Si un dictionnaire contient `"on": false`, ses valeurs sont **ignorées** :
```json
{
  "loras": {
    "on": false,  // Ce lora sera ignoré
    "lora_name": "disabled_lora.safetensors"
  }
}
```

---

## 🔧 Cas d'usage avancés

### 1. Extraire les prompts d'un workflow
```python
node_name = "CLIPTextEncode"
widget_names = "text"
```

### 2. Récupérer les seeds utilisés
```python
node_name = "KSampler"
widget_names = "seed"
```

### 3. Lister tous les modèles chargés
```python
node_name = "CheckpointLoader"
widget_names = "ckpt_name"
```

### 4. Extraire les paramètres de contrôle
```python
node_name = "ControlNetLoader"
widget_names = "control_net_name, strength"
```

---

## 🔧 Dépannage

### ❌ Sortie vide
- Vérifiez que `node_name` correspond à un node présent dans le workflow
- Vérifiez l'orthographe de `widget_names`
- Vérifiez que les widgets ne sont pas désactivés (`"on": false`)

### ❌ Certains widgets ne sont pas extraits
- Vérifiez que les noms correspondent exactement aux noms internes du node
- Certains widgets peuvent avoir des noms différents de leur label affiché
- Utilisez le mode auto (widget_names vide) pour voir tous les widgets disponibles

### ⚠️ Valeurs dupliquées
- Si plusieurs nodes du même type existent, toutes leurs valeurs seront extraites
- C'est le comportement normal : utilisez un node_name plus spécifique si nécessaire

### ⚠️ Ordre des valeurs
- L'ordre dépend de l'ordre des nodes dans le workflow
- L'ordre des widgets suit l'ordre de `widget_names`

---

## 📝 Notes

- Le node se met à jour automatiquement à chaque exécution (`IS_CHANGED`)
- Compatible avec tous les nodes ComfyUI (natifs et custom)
- Les valeurs sont retournées ligne par ligne avec `\n` comme séparateur
- Une ligne vide est ajoutée à la fin pour faciliter la concaténation

---

## 📄 License

MIT

---

## 🙏 Crédits

- **ComfyUI** - Framework node-based

---

## 📧 Contact

Pour signaler un bug ou suggérer une amélioration :
- Créez une issue
- Proposez une PR
