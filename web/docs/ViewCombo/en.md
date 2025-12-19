# View Combo 📋

A ComfyUI node for splitting multiline text <span style="background-color:#1e4d3e;color:#34d399;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">INT</span>o individual lines with advanced pagination and selection capabilities.

## Features

- Split multiline text <span style="background-color:#1e4d3e;color:#34d399;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">INT</span>o individual lines
- Automatic filtering of empty lines
- Pagination support with `start_index` and `max_rows`
- Advanced range selection with string syntax
- Multiple output formats (raw and numbered)
- Line counting (input and output)

## Inputs

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prompt` | STRING | "text" | Multiline text to process |
| `start_index` | <span style="background-color:#1e4d3e;color:#34d399;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;"><span style="background-color:#1e4d3e;color:#34d399;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">INT</span></span> | 0 | Starting line index (0-based) |
| `max_rows` | <span style="background-color:#1e4d3e;color:#34d399;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">INT</span> | 1000 | Maximum number of lines to return |
| `range_str` | STRING | "" | Range selector (takes priority if filled) |

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| `STRING` | LIST | Raw text lines |
| `COMBO` | LIST | Numbered text lines (format: `index: text`) |
| `input_count` | <span style="background-color:#1e4d3e;color:#34d399;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">INT</span> | Total number of non-empty lines in input |
| `output_count` | <span style="background-color:#1e4d3e;color:#34d399;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">INT</span> | Number of lines returned in current selection |

## Range Syntax

The `range_str` parameter takes **priority** over `start_index` and `max_rows` when filled. It supports multiple formats:

### Range with Dash (continuous sequence)
- **`0-2`** → Indices 0, 1, 2
- **`1-4`** → Indices 1, 2, 3, 4
- **`4-1`** → Indices 4, 3, 2, 1 (reversed)
- **`2--1`** → From index 2 to last element
- **`-3--1`** → Last three elements

### Specific Indices with Comma (precise selection)
- **`1,4`** → Only indices 1 and 4
- **`1,2,5`** → Only indices 1, 2, and 5
- **`0,3,-1`** → Indices 0, 3, and last element
- **`-2,-1,1,2`** → Second-to-last, last, 1, and 2

### Single Index
- **`3`** → Only index 3
- **`-1`** → Last element
- **`-2`** → Second-to-last element

## Usage Examples

### Example 1: Basic Pagination

**Input text:**
```
Apple
Banana
Orange
Strawberry
Kiwi
Mango
Pineapple
```

**Settings:**
- `start_index`: 2
- `max_rows`: 3
- `range`: (empty)

**Output STRING:** `["Orange", "Strawberry", "Kiwi"]`  
**Output COMBO:** `["2: Orange", "3: Strawberry", "4: Kiwi"]`  
**input_count:** `7`  
**output_count:** `3`

### Example 2: Specific Indices

**Input text:** (same as above)

**Settings:**
- `range_str`: "1,2,5"

**Output STRING:** `["Banana", "Orange", "Mango"]`  
**Output COMBO:** `["1: Banana", "2: Orange", "5: Mango"]`  
**input_count:** `7`  
**output_count:** `3`

### Example 3: Range to Last Element

**Input text:** (same as above)

**Settings:**
- `range_str`: "5--1"

**Output STRING:** `["Mango", "Pineapple"]`  
**Output COMBO:** `["5: Mango", "6: Pineapple"]`  
**input_count:** `7`  
**output_count:** `2`

### Example 4: Mix with Negative Indices

**Input text:** (same as above)

**Settings:**
- `range_str`: "0,3,-1"

**Output STRING:** `["Apple", "Strawberry", "Pineapple"]`  
**Output COMBO:** `["0: Apple", "3: Strawberry", "6: Pineapple"]`  
**input_count:** `7`  
**output_count:** `3`

## Practical Use Cases

### 1. LoRA Selection
Extract specific LoRAs from a list using the Extract Widget node, then use View Combo to select and number them for further processing.

### 2. Batch Processing
Process text data in chunks using pagination (`start_index` + `max_rows`), useful for workflows that need to handle large datasets incrementally.

### 3. Dynamic Selection
Connect other nodes to `range_str` to dynamically select specific lines based on workflow logic.

### 4. Data Validation
Use `input_count` and `output_count` to verify data <span style="background-color:#1e4d3e;color:#34d399;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">INT</span>egrity and track processing progress.

## Tips

- Leave `range_str` empty to use `start_index` and `max_rows` for simple pagination
- Use **dash (`-`)** for continuous ranges: `0-5`, `10-15`, `3--1`
- Use **comma (`,`)** for specific indices only: `0,5,10`, `1,3,-1`
- The `COMBO` output preserves original indices for easy traceability
- Empty lines are automatically filtered out
- Connect nodes to `start_index` and `max_rows` for dynamic pagination control

## Category

**TOO-Pack/View**

## Node Display Name

**View Combo 📋**
