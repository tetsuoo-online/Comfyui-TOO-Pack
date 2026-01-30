# TOO Much Replace 🔄

Un node de remplacement de chaînes de caractères avec 5 règles successives.

**Catégorie:** `TOO-Pack/utils`

---

## 📋 Fonctionnalités

- **5 règles de remplacement** successives
- **Ordre de priorité** : les règles s'appliquent dans l'ordre 1→5
- **Connexion STRING** en entrée
- **Simple et stable** : aucune dépendance JavaScript

---

## ⚙️ Paramètres

### Paramètres obligatoires

| Paramètre | Type | Description | Défaut |
|-----------|------|-------------|--------|
| **string** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Chaîne de caractères à traiter | `""` |
| **input_1** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Motif à rechercher (règle 1) | `""` |
| **output_1** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Valeur de remplacement (règle 1) | `""` |
| **input_2** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Motif à rechercher (règle 2) | `""` |
| **output_2** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Valeur de remplacement (règle 2) | `""` |
| **input_3** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Motif à rechercher (règle 3) | `""` |
| **output_3** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Valeur de remplacement (règle 3) | `""` |
| **input_4** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Motif à rechercher (règle 4) | `""` |
| **output_4** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Valeur de remplacement (règle 4) | `""` |
| **input_5** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Motif à rechercher (règle 5) | `""` |
| **output_5** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Valeur de remplacement (règle 5) | `""` |

### Sorties

| Paramètre | Type | Description |
|-----------|------|-------------|
| **STRING** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Chaîne après application des remplacements |

---

## 🎯 Fonctionnement

Le node applique les règles de remplacement dans l'ordre :

1. Cherche `input_1` dans le string → remplace par `output_1`
2. Cherche `input_2` dans le résultat → remplace par `output_2`
3. Cherche `input_3` dans le résultat → remplace par `output_3`
4. Cherche `input_4` dans le résultat → remplace par `output_4`
5. Cherche `input_5` dans le résultat → remplace par `output_5`

⚠️ **Important** : Les remplacements sont successifs, chaque règle s'applique sur le résultat de la règle précédente.

---

## 💡 Exemples d'utilisation

### Cas 1 : Nettoyer des noms de modèles

**Input :**
```
Flux2\flux-2-klein-base-9b-fp8.safetensors
```

**Règles :**
- `input_1`: `Flux2\flux-2-klein-base-9b-fp8.safetensors`
- `output_1`: `Flux2-Klein-Base-9B`

**Output :**
```
Flux2-Klein-Base-9B
```

---

### Cas 2 : Remplacements multiples

**Input :**
```
Flux2\flux-2-klein-9b-fp8.safetensors
Flux2\flux-2-klein-base-9b-fp8.safetensors
=============================
```

**Règles :**
- `input_1`: `Flux2\flux-2-klein-base-9b-fp8.safetensors` → `output_1`: `Flux2-Klein-Base-9B`
- `input_2`: `Flux2\flux-2-klein-9b-fp8.safetensors` → `output_2`: `Flux2-Klein-9B`
- `input_3`: `Flux2\flux-2-klein-4b-fp8.safetensors` → `output_3`: `Flux2-Klein-4B`
- `input_4`: `=============================` → `output_4`: ` ` (espace)

**Output :**
```
Flux2-Klein-9B
Flux2-Klein-Base-9B
 
```

---

### Cas 3 : Supprimer du texte

**Input :**
```
Mon texte [A SUPPRIMER] important
```

**Règle :**
- `input_1`: `[A SUPPRIMER]` → `output_1`: `` (vide)

**Output :**
```
Mon texte  important
```

---

## 🔗 Combinaison typique

```
[Extract Widget From Node] → STRING → [TOO Much Replace] → STRING → [Show Text]
```

Exemple : Extraire des noms de widgets depuis des nodes et les nettoyer pour affichage.

---

## 📝 Notes

- Les règles avec `input_X` vide sont ignorées
- Laissez `output_X` vide pour supprimer le texte
- L'ordre des règles est important (elles s'appliquent séquentiellement)
- Pour plus de 5 règles, dupliquez le node et chaînez-les
- Le champ `string` accepte les connexions depuis d'autres nodes

---

## 🔧 Détails techniques

### Remplacement de texte

Le node utilise Python `str.replace()` :
- Sensible à la casse
- Remplace toutes les occurrences du motif
- Pas de regex (recherche exacte)

### Performance

- Très léger (pur Python)
- Pas de dépendance JavaScript
- Fonctionne de manière synchrone

---

## 📄 License

MIT

---

## 🙏 Crédits

Partie de **Comfyui-TOO-Pack**
