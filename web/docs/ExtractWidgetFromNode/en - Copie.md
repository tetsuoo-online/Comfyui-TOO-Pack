# Extract Widget From Node 🔧

Extracts specific widget values from any node in the ComfyUI workflow.

**Category:** `TOO-Pack/utils`

---

## 📋 Features

- **Targeted extraction** of specific widgets by name
- **Compatible** with all ComfyUI nodes
- **Multiple extraction**: extract several widgets at once
- **Auto mode**: extracts all widgets if none specified
- **Smart handling** of dictionaries and nested values
- **"on" filter**: ignores disabled widgets

---

## ⚙️ Parameters

### Required Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| **node_name** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Node type name to target (e.g., "Power Lora Loader") | `Power Lora Loader` |
| **widget_names** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Widget names to extract (comma-separated) | `lora_name, strength_model` |

### Hidden Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| **extra_pnginfo** | <span style="background-color:#2d3748;color:#a0aec0;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">EXTRA_PNGINFO</span> | Workflow PNG metadata |
| **prompt** | <span style="background-color:#2d3748;color:#a0aec0;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">PROMPT</span> | Current workflow data |
| **unique_id** | <span style="background-color:#2d3748;color:#a0aec0;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">UNIQUE_ID</span> | Node unique ID |

### Outputs

| Parameter | Type | Description |
|-----------|------|-------------|
| **STRING** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Extracted values (one per line, separated by `\n`) |

---

## 💡 Usage Examples

### Case 1: Extract specific widgets from Lora Loader
```python
node_name = "LoraLoader"
widget_names = "lora_name, strength_model"
```
**Output:**
```
my_lora_v1.safetensors
0.85
```

### Case 2: Extract multiple parameters from KSampler
```python
node_name = "KSampler"
widget_names = "seed, steps, cfg"
```
**Output:**
```
123456789
20
7.5
```

### Case 3: Extract all widgets (auto mode)
```python
node_name = "CheckpointLoaderSimple"
widget_names = ""  # Empty = extract all
```
**Output:**
```
model_name.safetensors
```

### Case 4: Extract from multiple nodes of same type
```python
node_name = "Power Lora Loader"
widget_names = "lora_name"
```
**Output (if 3 Lora Loaders in workflow):**
```
lora1.safetensors
lora2.safetensors
lora3.safetensors
```

### Case 5: Use output in another node
```python
# Connect STRING output to a text node
# Example: Save Text, String Literal, etc.
```

---

## 🎯 Technical Details

### Node search

The node performs a **case-insensitive search** on `node_name`:
- `"power lora"` will find `"Power Lora Loader"`
- `"ksampler"` will find `"KSampler"` and `"KSamplerAdvanced"`

### widget_names format

Widget names must be **comma-separated**:
```python
"widget1, widget2, widget3"
```

Spaces are automatically stripped:
```python
"lora_name,strength_model,strength_clip"  # OK
"lora_name, strength_model, strength_clip"  # Also OK
```

### Nested values handling

The node intelligently handles nested dictionaries:

**Simple structure:**
```json
{
  "lora_name": "my_lora.safetensors",
  "strength_model": 0.85
}
```

**Nested structure (Power Lora Loader):**
```json
{
  "loras": {
    "on": true,
    "lora_name": "my_lora.safetensors",
    "strength_model": 0.85
  }
}
```

The node automatically extracts values from both structures.

### "on" filter

If a dictionary contains `"on": false`, its values are **ignored**:
```json
{
  "loras": {
    "on": false,  // This lora will be ignored
    "lora_name": "disabled_lora.safetensors"
  }
}
```

---

## 🔧 Advanced Use Cases

### 1. Extract prompts from workflow
```python
node_name = "CLIPTextEncode"
widget_names = "text"
```

### 2. Retrieve used seeds
```python
node_name = "KSampler"
widget_names = "seed"
```

### 3. List all loaded models
```python
node_name = "CheckpointLoader"
widget_names = "ckpt_name"
```

### 4. Extract control parameters
```python
node_name = "ControlNetLoader"
widget_names = "control_net_name, strength"
```

---

## 🔧 Troubleshooting

### ❌ Empty output
- Check that `node_name` matches a node present in the workflow
- Check spelling of `widget_names`
- Check that widgets are not disabled (`"on": false`)

### ❌ Some widgets not extracted
- Check that names exactly match the node's internal names
- Some widgets may have different names from their displayed labels
- Use auto mode (empty widget_names) to see all available widgets

### ⚠️ Duplicate values
- If multiple nodes of the same type exist, all their values will be extracted
- This is normal behavior: use a more specific node_name if needed

### ⚠️ Value order
- Order depends on node order in workflow
- Widget order follows `widget_names` order

---

## 📝 Notes

- Node auto-updates on every execution (`IS_CHANGED`)
- Compatible with all ComfyUI nodes (native and custom)
- Values are returned line by line with `\n` as separator
- Empty line added at end for easier concatenation

---

## 📄 License

MIT

---

## 🙏 Credits

- **ComfyUI** - Node-based framework

---

## 📧 Contact

To report a bug or suggest an improvement:
- Create an issue
- Submit a PR
