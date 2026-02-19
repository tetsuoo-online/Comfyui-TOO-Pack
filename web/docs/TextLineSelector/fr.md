# TExt Line Selector 📋

Un nœud ComfyUI pour diviser un texte multiligne en lignes individuelles avec pagination avancée et capacités de sélection.

## Fonctionnalités

- Division d'un texte multiligne en lignes individuelles
- Filtrage automatique des lignes vides
- Support de pagination avec `start_index` et `max_rows`
- Sélection avancée par plage avec syntaxe string
- Formats de sortie multiples (brut et numéroté)
- Comptage des lignes (entrée et sortie)

## Entrées

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `prompt` | STRING | "text" | Texte multiligne à traiter |
| `start_index` | <span style="background-color:#1e4d3e;color:#34d399;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">INT</span> | 0 | Index de ligne de départ (base 0) |
| `max_rows` | <span style="background-color:#1e4d3e;color:#34d399;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">INT</span> | 1000 | Nombre maximum de lignes à retourner |
| `range_str` | STRING | "" | Sélecteur de plage (prioritaire si renseigné) |

## Sorties

| Sortie | Type | Description |
|--------|------|-------------|
| `STRING` | LIST | Lignes de texte brutes |
| `COMBO` | LIST | Lignes de texte numérotées (format : `index: texte`) |
| `input_count` | <span style="background-color:#1e4d3e;color:#34d399;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">INT</span> | Nombre total de lignes non-vides en entrée |
| `output_count` | <span style="background-color:#1e4d3e;color:#34d399;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">INT</span> | Nombre de lignes retournées dans la sélection actuelle |

## Syntaxe Range

Le paramètre `range_str` prend la **priorité** sur `start_index` et `max_rows` lorsqu'il est renseigné. Il supporte plusieurs formats :

### Plage avec Tiret (séquence continue)
- **`0-2`** → Indices 0, 1, 2
- **`1-4`** → Indices 1, 2, 3, 4
- **`4-1`** → Indices 4, 3, 2, 1 (inversé)
- **`2--1`** → De l'index 2 au dernier élément
- **`-3--1`** → Les trois derniers éléments

### Indices Spécifiques avec Virgule (sélection précise)
- **`1,4`** → Uniquement les indices 1 et 4
- **`1,2,5`** → Uniquement les indices 1, 2 et 5
- **`0,3,-1`** → Indices 0, 3 et dernier élément
- **`-2,-1,1,2`** → Avant-dernier, dernier, 1 et 2

### Index Unique
- **`3`** → Uniquement l'index 3
- **`-1`** → Dernier élément
- **`-2`** → Avant-dernier élément

## Exemples d'Utilisation

### Exemple 1 : Pagination Basique

**Texte d'entrée :**
```
Pomme
Banane
Orange
Fraise
Kiwi
Mangue
Ananas
```

**Paramètres :**
- `start_index` : 2
- `max_rows` : 3
- `range` : (vide)

**Sortie STRING :** `["Orange", "Fraise", "Kiwi"]`  
**Sortie COMBO :** `["2: Orange", "3: Fraise", "4: Kiwi"]`  
**input_count :** `7`  
**output_count :** `3`

### Exemple 2 : Indices Spécifiques

**Texte d'entrée :** (identique ci-dessus)

**Paramètres :**
- `range_str` : "1,2,5"

**Sortie STRING :** `["Banane", "Orange", "Mangue"]`  
**Sortie COMBO :** `["1: Banane", "2: Orange", "5: Mangue"]`  
**input_count :** `7`  
**output_count :** `3`

### Exemple 3 : Plage Jusqu'au Dernier

**Texte d'entrée :** (identique ci-dessus)

**Paramètres :**
- `range_str` : "5--1"

**Sortie STRING :** `["Mangue", "Ananas"]`  
**Sortie COMBO :** `["5: Mangue", "6: Ananas"]`  
**input_count :** `7`  
**output_count :** `2`

### Exemple 4 : Mélange avec Indices Négatifs

**Texte d'entrée :** (identique ci-dessus)

**Paramètres :**
- `range_str` : "0,3,-1"

**Sortie STRING :** `["Pomme", "Fraise", "Ananas"]`  
**Sortie COMBO :** `["0: Pomme", "3: Fraise", "6: Ananas"]`  
**input_count :** `7`  
**output_count :** `3`

## Cas d'Usage Pratiques

### 1. Sélection de LoRAs
Extraire des LoRAs spécifiques d'une liste avec le nœud Extract Widget, puis utiliser View Combo pour les sélectionner et les numéroter pour un traitement ultérieur.

### 2. Traitement par Lots
Traiter des données textuelles par morceaux en utilisant la pagination (`start_index` + `max_rows`), utile pour les workflows qui doivent gérer de grands ensembles de données de manière incrémentale.

### 3. Sélection Dynamique
Connecter d'autres nœuds à l'entrée `range_str` pour sélectionner dynamiquement des lignes spécifiques en fonction de la logique du workflow.

### 4. Validation de Données
Utiliser `input_count` et `output_count` pour vérifier l'<span style="background-color:#1e4d3e;color:#34d399;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">INT</span>égrité des données et suivre la progression du traitement.

## Conseils

- Laissez `range_str` vide pour utiliser `start_index` et `max_rows` pour une pagination simple
- Utilisez le **tiret (`-`)** pour les plages continues : `0-5`, `10-15`, `3--1`
- Utilisez la **virgule (`,`)** pour des indices spécifiques uniquement : `0,5,10`, `1,3,-1`
- La sortie `COMBO` préserve les indices originaux pour une traçabilité facile
- Les lignes vides sont automatiquement filtrées
- Connectez des nœuds à `start_index` et `max_rows` pour un contrôle dynamique de la pagination

## Catégorie

**TOO-Pack/View**

## Nom d'Affichage du Nœud

**View Combo 📋**
