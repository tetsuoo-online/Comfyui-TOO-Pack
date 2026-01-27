# String Output Logic Node - TOO-Pack

Ce node remplace le subgraph de logique de sortie string. Il permet de faire des remplacements conditionnels simples et efficaces.

## 📦 Installation

Placez les fichiers dans votre dossier `custom_nodes/TOO-Pack/` :

### Option 1 : Version Simple (RECOMMANDÉE)
- `string_output_logic_simple.py`

**Avantages :**
- ✅ Aucune dépendance JavaScript
- ✅ Fonctionne immédiatement après redémarrage
- ✅ 5 règles de remplacement (suffisant pour la plupart des cas)
- ✅ Interface claire et simple

**Inconvénient :**
- ❌ Nombre de règles fixe (5 paires input/output)

### Option 2 : Version avec JavaScript
- `string_output_logic.py` 
- `string_output_logic.js` (à placer dans le dossier `web/` de TOO-Pack)

**Avantages :**
- ✅ Nombre de règles dynamique (1-20)
- ✅ Interface s'adapte automatiquement

**Inconvénients :**
- ❌ Nécessite un fichier JavaScript supplémentaire
- ❌ Plus complexe à maintenir

## 🎯 Utilisation

### Exemple d'utilisation avec vos modèles Flux

**Input string :**
```
Flux2\flux-2-klein-base-9b-fp8.safetensors
```

**Règles de remplacement :**
- `input_1`: `Flux2\flux-2-klein-base-9b-fp8.safetensors`
- `output_1`: `Flux2-Klein-Base-9B`

- `input_2`: `Flux2\flux-2-klein-9b-fp8.safetensors`
- `output_2`: `Flux2-Klein-9B`

- `input_3`: `Flux2\flux-2-klein-4b-fp8.safetensors`
- `output_3`: `Flux2-Klein-4B`

- `input_4`: `=============================`
- `output_4`: ` ` (espace ou vide pour supprimer)

**Output string :**
```
Flux2-Klein-Base-9B
```

## 🔧 Fonctionnement

Le node applique les règles de remplacement dans l'ordre :
1. Vérifie si `input_1` existe dans le string
2. Si oui, remplace par `output_1`
3. Continue avec `input_2`, `input_3`, etc.
4. Retourne le string modifié

## 💡 Conseils

- Laissez les champs vides si vous n'avez pas besoin de toutes les règles
- Les remplacements sont appliqués séquentiellement (ordre important)
- Utilisez un `output` vide pour supprimer du texte
- Le node retourne toujours un STRING compatible avec d'autres nodes

## 🔗 Connexion avec Extract Widget From Node

```
[Extract Widget From Node] → STRING → [String Output Logic] → STRING → [Destination]
```

Parfait pour nettoyer les noms de modèles, loras, etc. extraits de vos workflows !

---

**Recommandation :** Utilisez la version Simple sauf si vous avez vraiment besoin de plus de 5 règles.
