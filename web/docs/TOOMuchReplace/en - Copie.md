# TOO Much Replace 🔄

A string replacement node with 5 successive rules.

**Category:** `TOO-Pack/utils`

---

## 📋 Features

- **5 replacement rules** applied successively
- **Priority order**: rules apply in order 1→5
- **STRING connection** input supported
- **Simple and stable**: no JavaScript dependencies

---

## ⚙️ Parameters

### Required Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| **string** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Input string to process | `""` |
| **input_1** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Pattern to search for (rule 1) | `""` |
| **output_1** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Replacement value (rule 1) | `""` |
| **input_2** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Pattern to search for (rule 2) | `""` |
| **output_2** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Replacement value (rule 2) | `""` |
| **input_3** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Pattern to search for (rule 3) | `""` |
| **output_3** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Replacement value (rule 3) | `""` |
| **input_4** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Pattern to search for (rule 4) | `""` |
| **output_4** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Replacement value (rule 4) | `""` |
| **input_5** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Pattern to search for (rule 5) | `""` |
| **output_5** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Replacement value (rule 5) | `""` |

### Outputs

| Parameter | Type | Description |
|-----------|------|-------------|
| **STRING** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | String after applying all replacements |

---

## 🎯 How It Works

The node applies replacement rules in order:

1. Search for `input_1` in the string → replace with `output_1`
2. Search for `input_2` in the result → replace with `output_2`
3. Search for `input_3` in the result → replace with `output_3`
4. Search for `input_4` in the result → replace with `output_4`
5. Search for `input_5` in the result → replace with `output_5`

⚠️ **Important**: Replacements are successive - each rule applies to the result of the previous rule.

---

## 💡 Usage Examples

### Case 1: Clean model names

**Input:**
```
Flux2\flux-2-klein-base-9b-fp8.safetensors
```

**Rules:**
- `input_1`: `Flux2\flux-2-klein-base-9b-fp8.safetensors`
- `output_1`: `Flux2-Klein-Base-9B`

**Output:**
```
Flux2-Klein-Base-9B
```

---

### Case 2: Multiple replacements

**Input:**
```
Flux2\flux-2-klein-9b-fp8.safetensors
Flux2\flux-2-klein-base-9b-fp8.safetensors
=============================
```

**Rules:**
- `input_1`: `Flux2\flux-2-klein-base-9b-fp8.safetensors` → `output_1`: `Flux2-Klein-Base-9B`
- `input_2`: `Flux2\flux-2-klein-9b-fp8.safetensors` → `output_2`: `Flux2-Klein-9B`
- `input_3`: `Flux2\flux-2-klein-4b-fp8.safetensors` → `output_3`: `Flux2-Klein-4B`
- `input_4`: `=============================` → `output_4`: ` ` (space)

**Output:**
```
Flux2-Klein-9B
Flux2-Klein-Base-9B
 
```

---

### Case 3: Remove text

**Input:**
```
My text [TO REMOVE] important
```

**Rule:**
- `input_1`: `[TO REMOVE]` → `output_1`: `` (empty)

**Output:**
```
My text  important
```

---

## 🔗 Typical Combination

```
[Extract Widget From Node] → STRING → [TOO Much Replace] → STRING → [Show Text]
```

Example: Extract widget names from nodes and clean them for display.

---

## 📝 Notes

- Rules with empty `input_X` are ignored
- Leave `output_X` empty to delete text
- Rule order matters (they apply sequentially)
- For more than 5 rules, duplicate the node and chain them
- The `string` field accepts connections from other nodes

---

## 🔧 Technical Details

### Text Replacement

The node uses Python `str.replace()`:
- Case sensitive
- Replaces all occurrences of the pattern
- No regex (exact match only)

### Performance

- Very lightweight (pure Python)
- No JavaScript dependencies
- Works synchronously

---

## 📄 License

MIT

---

## 🙏 Credits

Part of **Comfyui-TOO-Pack**
