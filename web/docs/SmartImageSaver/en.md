# Smart Image Saver 💾

An intelligent image saver that replaces the SAVE_IMG subgraph with flexible filename customization.

**Category:** `TOO-Pack/image`

---

## 📋 Features

- **Flexible naming**: Customizable prefix, suffix, and separator
- **Date tokens**: YYYY, MM, DD, HH, mm, ss, timestamp support
- **Smart metadata extraction**: Auto-extract seed and model name from workflow
- **Node targeting**: Target nodes by class name or direct ID (#10)
- **Multiple formats**: WEBP (lossy/lossless), PNG, JPG/JPEG
- **Metadata preservation**: Saves prompt and workflow in EXIF/PNG info
- **Auto-increment**: Prevents overwriting existing files

---

## ⚙️ Parameters

### Required Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| **images** | <span style="background-color:#7c2d12;color:#fb923c;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">IMAGE</span> | Images to save | - |
| **output_folder** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Output folder (supports date tokens) | `YYYY-MM-DD` |
| **prefix** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Filename prefix (supports date tokens) | `ComfyUI_YYYY-MM-DD_HHmmss` |
| **seed_node_name** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Node containing seed (class name or #ID) | `KSampler` |
| **seed_widget_name** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Widget name for seed | `seed` |
| **model_node_name** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Node containing model (class name or #ID) | `CheckpointLoaderSimple` |
| **model_widget_name** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Widget name for model | `ckpt_name` |
| **suffix** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Filename suffix (supports date tokens) | `""` |
| **output_format** | <span style="background-color:#4a5568;color:#a0aec0;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">COMBO</span> | Image format | `webp` |
| **webp_lossless** | <span style="background-color:#7c3aed;color:#a78bfa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">BOOLEAN</span> | WEBP lossless mode (larger files) | `False` |
| **quality** | <span style="background-color:#1e4d3e;color:#34d399;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">INT</span> | Compression quality (1-100) | `97` |
| **separator** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Separator between filename elements | `_` |

### Outputs

| Parameter | Type | Description |
|-----------|------|-------------|
| **images** | <span style="background-color:#7c2d12;color:#fb923c;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">IMAGE</span> | Pass-through of input images |
| **filepath** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Path of the first saved file |

---

## 🎯 Filename Structure

The node builds filenames in this order:

```
[prefix]_[seed]_[model_name]_[suffix].[format]
```

Elements are joined by the separator character. Empty elements are skipped.

**Example outputs:**
- `render_2024-01-30_123456_mymodel_final.webp`
- `ComfyUI_2024-01-30_143025_987654_sd15.png`
- `test_500_juggernaut_v9.jpg`

---

## 💡 Usage Examples

### Case 1: Basic usage with date folder
```python
output_folder = "YYYY-MM-DD"           # → 2024-01-30/
prefix = "render_YYYYMMDD"              # → render_20240130
seed_node_name = "KSampler"
model_node_name = "CheckpointLoaderSimple"
```
**Output:** `2024-01-30/render_20240130_123456_mymodel.webp`

### Case 2: Target node by ID
```python
seed_node_name = "#10"                  # Target node with ID 10
model_node_name = "#5"                  # Target node with ID 5
```

### Case 3: Disable seed or model
```python
seed_node_name = ""                     # Don't include seed
model_node_name = ""                    # Don't include model
prefix = "my_render"
suffix = "HHmmss"                       # Add timestamp
```
**Output:** `my_render_143025.webp`

### Case 4: Project organization
```python
output_folder = "projects/character_design/YYYY-MM-DD"
prefix = "char"
suffix = "v1"
```
**Output:** `projects/character_design/2024-01-30/char_123456_model_v1.webp`

### Case 5: High-quality PNG
```python
output_format = "png"
# PNG ignores quality and webp_lossless settings
```

### Case 6: Lossless WEBP
```python
output_format = "webp"
webp_lossless = True                    # Larger but lossless
# quality is ignored when lossless=True
```

---

## 📅 Date Tokens

All date tokens are replaced with current date/time values:

| Token | Description | Example |
|-------|-------------|---------|
| `YYYY` | Year (4 digits) | 2024 |
| `YY` | Year (2 digits) | 24 |
| `MM` | Month (2 digits) | 01 |
| `DD` | Day (2 digits) | 30 |
| `HH` | Hour 24h (2 digits) | 14 |
| `mm` | Minute (2 digits) | 30 |
| `ss` | Second (2 digits) | 25 |
| `timestamp` | Unix timestamp | 1706623825 |

**Examples:**
- `YYYY-MM-DD` → `2024-01-30`
- `YYYYMMDD_HHmmss` → `20240130_143025`
- `backup_timestamp` → `backup_1706623825`

---

## 🎯 Node Targeting

Two methods to target nodes:

### By Class Name (default)
```python
seed_node_name = "KSampler"              # Finds any KSampler node
model_node_name = "CheckpointLoaderSimple"
```
- Case-insensitive search
- Finds first matching node of that type

### By Node ID (precise)
```python
seed_node_name = "#10"                   # Targets node with ID 10
model_node_name = "#5"                   # Targets node with ID 5
```
- Direct targeting by node ID
- Use when you have multiple nodes of same type
- Node IDs visible in ComfyUI workflow

---

## 🔧 Technical Details

### Model Name Cleaning

The node automatically cleans model names:
- Removes path: `/models/checkpoints/model.safetensors` → `model`
- Removes extensions: `.safetensors`, `.ckpt`, `.pt`, `.pth`, `.bin`

### File Safety

- Invalid characters are automatically removed from filenames
- Existing files are never overwritten (auto-increment: `_001`, `_002`, etc.)
- Empty folder names are handled gracefully

### Metadata Storage

**WEBP/JPG:** Metadata stored in EXIF tags
- Tag 0x010f (Make): Prompt JSON
- Tag 0x010e (ImageDescription): Workflow JSON

**PNG:** Metadata stored in PNG info chunks
- `prompt`: Prompt JSON
- `workflow`: Workflow JSON

Metadata can be disabled with ComfyUI's `--disable-metadata` flag.

### Multi-Image Batches

When saving multiple images:
```
render_0000.webp
render_0001.webp
render_0002.webp
```

---

## 📂 Output Formats

| Format | Description | Quality | Use Case |
|--------|-------------|---------|----------|
| **WEBP** | Modern format, good compression | Lossy/Lossless | Recommended for most cases |
| **PNG** | Lossless, large files | Always lossless | Final exports, transparency |
| **JPG/JPEG** | Lossy, small files | Lossy | Web sharing, space-constrained |

---

## 🔧 Troubleshooting

### ❌ Seed/Model not appearing in filename
- Check that node names match your workflow
- Try using `#ID` format to target specific nodes
- Verify widget names are correct (`seed`, `ckpt_name`, etc.)
- Leave field empty to disable that element

### ❌ Invalid filename characters
- The node automatically removes invalid characters
- If issues persist, avoid special characters in custom fields

### ⚠️ Files being overwritten
- The node prevents overwrites with auto-increment
- If this fails, check folder permissions

---

## 📝 Notes

- All date tokens work in `output_folder`, `prefix`, and `suffix`
- Empty `seed_node_name` or `model_node_name` disables that element
- Node searches are case-insensitive
- WEBP lossless ignores quality setting
- PNG format ignores both quality and lossless settings

---

## 📄 License

MIT

---

## 🙏 Credits

- **ComfyUI** - Node-based framework
- **PIL/Pillow** - Image manipulation
- **PyTorch** - Tensor operations
