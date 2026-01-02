# ComfyUI-TOO-Pack 🎨

**Tetsuoo's custom nodes pack for ComfyUI**

A collection of utility nodes designed to enhance your ComfyUI workflow with smart image loading, Krita integration, widget extraction, and more.

**Category:** `TOO-Pack`

---

## 📦 Installation

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/tetsuoo-online/Comfyui-TOO-Pack
```


### Requirements

- **ComfyUI** (latest version recommended)
- **Python** 3.8+
- **PyTorch**
- **Pillow** (PIL)
- **NumPy**

---

## 🎯 Nodes Overview

| Node | Category | Description |
|------|----------|-------------|
| [Smart Image Loader](#smart-image-loader-) | `TOO-Pack/image` | Flexible image loader with multiple sources |
| [Krita Bridge](#krita-bridge-) | `TOO-Pack/image` | Auto-load images from Krita |
| [Extract Widget From Node](#extract-widget-from-node-) | `TOO-Pack/utils` | Extract widget values from workflow nodes |
| [Collection Categorizer](#collection-categorizer-llm-) | `TOO-Pack/utils` | Categorize files with local LLM (Ollama) |

---

## 📚 Node Documentation

### Smart Image Loader 🖼

<details>
<summary><b><a href="#" style="color:#60a5fa;text-decoration:none;">Click to expand full documentation</a></b></summary>

A flexible image loader that supports multiple input sources with priority order.

#### Features

- **Multiple sources**: txt, direct path, directory, or direct image
- **Smart priority order** with configurable inputs
- **Random selection** with reproducible seed
- **Multiple formats** supported (PNG, JPG, JPEG, BMP, WEBP, TIFF)
- **Returns file path** of loaded image

#### Parameters

**Required Parameters**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| **seed** | <span style="background-color:#1e4d3e;color:#34d399;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">INT</span> | Seed for reproducible random selection | `0` |

**Optional Parameters**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| **txt_path** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Path to text file containing image paths | - |
| **img_path** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Direct path to an image file | - |
| **img_directory** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Path to directory containing images | - |
| **image** | <span style="background-color:#7c2d12;color:#fb923c;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">IMAGE</span> | Direct image input | - |

**Outputs**

| Parameter | Type | Description |
|-----------|------|-------------|
| **IMAGE** | <span style="background-color:#7c2d12;color:#fb923c;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">IMAGE</span> | The loaded image as tensor |
| **FILE_PATH** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Path of loaded file ("external_input" or "none") |

#### Priority Order

The node loads images in this order (from highest to lowest priority):

1. **txt_path** 📄 : Randomly selects a path from text file
2. **img_path** 🖼 : Loads the specific image file
3. **img_directory** 📁 : Randomly selects an image from directory
4. **image** ⚡ : Uses the provided image input

#### Usage Examples

**Case 1: Text file with image list**
```python
# Content of image_list.txt:
# /path/to/image1.png
# /path/to/image2.jpg
# /path/to/image3.webp

txt_path = "/path/to/image_list.txt"
seed = 42  # Reproducible
```

**Case 2: Direct path to image**
```python
img_path = "/path/to/specific/image.png"
```

**Case 3: Image directory**
```python
img_directory = "/path/to/images/"
seed = 123
```

**Case 4: Combination with priority**
```python
txt_path = "/path/to/list.txt"       # Priority 1
img_path = "/path/to/fallback.png"   # Priority 2 (if txt_path fails)
img_directory = "/path/to/backup/"   # Priority 3 (if img_path fails)
```

#### Technical Details

**Text file format (txt_path)**

The text file should contain one image path per line:

```
/home/user/images/photo1.png
/home/user/images/photo2.jpg
/home/user/images/photo3.webp
```

- Empty lines are ignored
- UTF-8 encoding supported
- A random path is selected using the seed

**Seed handling**

- **seed = 0**: Different random selection each run
- **seed > 0**: Identical selection with same parameters (reproducible)

**FILE_PATH values**

| Value | Description |
|-------|-------------|
| Full path | Image loaded from txt_path, img_path or img_directory |
| `"external_input"` | Image provided via image parameter |
| `"none"` | No valid source found (error) |

</details>

---

### Krita Bridge 🎨

<details>
<summary><b><a href="#" style="color:#60a5fa;text-decoration:none;">Click to expand full documentation</a></b></summary>

Automatically loads the latest image from the `input/krita/` folder for seamless Krita integration.

#### Features

- **Automatic loading** of latest image from krita folder
- **Real-time detection** of new files
- **Auto-update** during generation
- **Alpha support**: extracts alpha channel as mask
- **Auto-create** folder if doesn't exist
- **No parameters** - works directly

#### Parameters

**Required Parameters**

**No parameters required** - The node works automatically!

**Outputs**

| Parameter | Type | Description |
|-----------|------|-------------|
| **image** | <span style="background-color:#7c2d12;color:#fb923c;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">IMAGE</span> | The loaded image (RGB) |
| **mask** | <span style="background-color:#4c1d95;color:#c4b5fd;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">MASK</span> | Mask extracted from alpha channel |

#### Setup

**Working Directory**

The node automatically loads from:
```
ComfyUI/input/krita/
```

If the folder doesn't exist, it's created automatically on first launch.

**Export from Krita**

1. **Open Krita**
2. **Create or modify** your image
3. **Export as PNG**: `File > Export`
4. **Destination**: `ComfyUI/input/krita/filename.png`
5. The node automatically detects the new file

**Recommended Workflow**

```
Krita → Export PNG → ComfyUI/input/krita/ → Krita Bridge → [your workflow]
```

#### Usage Examples

**Case 1: Simple loading**
```python
# No configuration needed
# Node automatically loads latest image
```

**Case 2: Using alpha mask**
```python
# Connect 'mask' to a mask node (Mask Composite, etc.)
# Krita image's alpha channel becomes usable mask
```

**Case 3: Iterative Krita ↔ ComfyUI workflow**
```
1. Draw in Krita
2. Export → input/krita/sketch.png
3. ComfyUI detects and generates
4. Get result
5. Refine in Krita
6. Re-export → Node loads new version
```

**Case 4: Inpainting with Krita mask**
```python
# Workflow:
# Krita Bridge (image + mask) → Inpaint Model → VAE Decode
# Krita's alpha mask defines inpainting area
```

#### Technical Details

**File Detection**

The node:
1. Scans `input/krita/` folder for all `.png` files
2. Finds file with **most recent modification**
3. Compares timestamp with last loaded file
4. Reloads if change detected

**Alpha Channel Handling**

**RGBA image (with transparency):**
- RGB channels → `image` output
- Alpha channel → `mask` output (0-1 values)

**RGB image (no transparency):**
- RGB → `image` output
- Uniform white mask → `mask` output

**Automatic Update**

The `IS_CHANGED` function returns current timestamp, forcing ComfyUI to:
- Re-evaluate node on every execution
- Detect new files in real-time
- Update image automatically

#### Krita Integration

**Krita Configuration**

1. **Set default export folder**
   - `Settings > Configure Krita > General`
   - Set default folder: `ComfyUI/input/krita/`

2. **Keyboard shortcut for quick export**
   - `Settings > Configure Krita > Keyboard Shortcuts`
   - Assign key to `Export`
   - Example: `Ctrl+Shift+E`

3. **Export format**
   - Format: **PNG**
   - Compression: as preferred
   - **Important**: Enable "Save alpha channel" if using mask

**Optimal Workflow**

```
┌─────────┐    Export PNG    ┌──────────────┐
│  Krita  │ ───────────────> │ input/krita/ │
└─────────┘                   └──────────────┘
                                      │
                                      ▼
                              ┌──────────────┐
                              │ Krita Bridge │
                              └──────────────┘
                                      │
                     ┌────────────────┴────────────────┐
                     ▼                                 ▼
                ┌────────┐                        ┌──────┐
                │ image  │                        │ mask │
                └────────┘                        └──────┘
```

</details>

---

### Extract Widget From Node 🔧

<details>
<summary><b><a href="#" style="color:#60a5fa;text-decoration:none;">Click to expand full documentation</a></b></summary>

Extracts specific widget values from any node in the ComfyUI workflow.

#### Features

- **Targeted extraction** of specific widgets by name
- **Compatible** with all ComfyUI nodes
- **Multiple extraction**: extract several widgets at once
- **Auto mode**: extracts all widgets if none specified
- **Smart handling** of dictionaries and nested values
- **"on" filter**: ignores disabled widgets

#### Parameters

**Required Parameters**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| **node_name** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Node type name to target (e.g., "Power Lora Loader") | `Power Lora Loader` |
| **widget_names** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Widget names to extract (comma-separated) | `lora_name, strength_model` |

**Hidden Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| **extra_pnginfo** | <span style="background-color:#2d3748;color:#a0aec0;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">EXTRA_PNGINFO</span> | Workflow PNG metadata |
| **prompt** | <span style="background-color:#2d3748;color:#a0aec0;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">PROMPT</span> | Current workflow data |
| **unique_id** | <span style="background-color:#2d3748;color:#a0aec0;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">UNIQUE_ID</span> | Node unique ID |

**Outputs**

| Parameter | Type | Description |
|-----------|------|-------------|
| **STRING** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Extracted values (one per line, separated by `\n`) |

#### Usage Examples

**Case 1: Extract specific widgets from Lora Loader**
```python
node_name = "Power Lora Loader"
widget_names = "lora_name, strength_model"
```
**Output:**
```
my_lora_v1.safetensors
0.85
```

**Case 2: Extract multiple parameters from KSampler**
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

**Case 3: Extract all widgets (auto mode)**
```python
node_name = "CheckpointLoaderSimple"
widget_names = ""  # Empty = extract all
```

**Case 4: Extract from multiple nodes of same type**
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

#### Technical Details

**Node search**

The node performs a **case-insensitive search** on `node_name`:
- `"power lora"` will find `"Power Lora Loader"`
- `"ksampler"` will find `"KSampler"` and `"KSamplerAdvanced"`

**widget_names format**

Widget names must be **comma-separated**:
```python
"widget1, widget2, widget3"
```

Spaces are automatically stripped.

**Nested values handling**

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

**"on" filter**

If a dictionary contains `"on": false`, its values are **ignored**.

#### Advanced Use Cases

**1. Extract prompts from workflow**
```python
node_name = "CLIPTextEncode"
widget_names = "text"
```

**2. Retrieve used seeds**
```python
node_name = "KSampler"
widget_names = "seed"
```

**3. List all loaded models**
```python
node_name = "CheckpointLoader"
widget_names = "ckpt_name"
```

**4. Extract control parameters**
```python
node_name = "ControlNetLoader"
widget_names = "control_net_name, strength"
```

</details>

---

### Collection Categorizer (LLM) 🗂

<details>
<summary><b><a href="#" style="color:#60a5fa;text-decoration:none;">Click to expand full documentation</a></b></summary>

A ComfyUI node that automatically scans your folders and categorizes content with a local LLM (Ollama).

#### Features

- **Automatic scanning** of folders (video files, archives, documents)
- **Smart categorization** via local LLM (Ollama)
- **Recursive scanning** of subfolders (optional)
- **Reproducible seed** for identical results
- **Custom Ollama models** supported
- **Auto-save** JSON output
- **Compatible** with Collection Manager
- **100% local** - no external APIs

#### Parameters

**Main Parameters**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| **ollama_model** | <span style="background-color:#4a5568;color:#a0aec0;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">COMBO</span> | LLM model to use (or "custom") | `qwen2.5:7b` |
| **custom_ollama_model** | <span style="background-color:#2563eb;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Model name if "custom" selected | - |
| **folder_path** | <span style="background-color:#2563eb;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Path to folder to scan | - |
| **scan_subfolders** | <span style="background-color:#7c3aed;color:#a78bfa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">BOOLEAN</span> | Recursively scan subfolders | `False` |
| **save_json** | <span style="background-color:#7c3aed;color:#a78bfa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">BOOLEAN</span> | Auto-save JSON output | `True` |
| **collection_title** | <span style="background-color:#2563eb;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Collection title | `Ma Collection` |
| **content_type** | <span style="background-color:#4a5568;color:#a0aec0;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">COMBO</span> | Content type (or "custom") | `films` |

**Optional Parameters**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| **custom_type_name** | <span style="background-color:#2563eb;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Type name if "custom" selected | - |
| **custom_categories** | <span style="background-color:#2563eb;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Custom categorization criteria (multiline) | (empty = LLM decides) |
| **seed** | <span style="background-color:#059669;color:#34d399;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">INT</span> | Seed for reproducible results | `0` (random) |

**Outputs**

| Parameter | Type | Description |
|-----------|------|-------------|
| **json_output** | <span style="background-color:#2563eb;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | The complete collection JSON |
| **summary** | <span style="background-color:#2563eb;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Categorization summary |

#### Usage Examples

**Case 1: Movies with automatic categories**
```python
content_type = "films"
custom_categories = ""  # Empty
# LLM decides categories (Genre, Era, etc.)
```

**Case 2: TV Series with custom criteria**
```python
content_type = "series"
custom_categories = "Genre, Year, Studio"
# LLM categorizes by these criteria
```

**Case 3: Custom type**
```python
content_type = "custom"
custom_type_name = "Documentaries"
custom_categories = "Theme, Duration"
```

**Case 4: Custom model**
```python
ollama_model = "custom"
custom_ollama_model = "mistral:7b"
```

**Case 5: Reproducible results**
```python
seed = 42
# Always same result with same parameters
```

#### Installation

**Requirements**

1. **Ollama** installed and running
   ```bash
   # Download: https://ollama.ai
   ollama --version
   ```

2. **Python requests** (for local HTTP API)
   ```bash
   pip install requests --break-system-packages
   ```

3. **At least one LLM model**
   ```bash
   ollama pull qwen2.5:7b
   ```

#### Supported File Types

**Videos**
`.mp4`, `.mkv`, `.avi`, `.mov`, `.wmv`, `.flv`

**Archives**
`.cbz`, `.cbr`, `.zip`, `.rar`

**Documents**
`.epub`, `.pdf`, `.mobi`

**Folders**
Subfolders are treated as individual items (unless `scan_subfolders` is enabled)

#### Recommended Models

| Model | Size | Speed | Quality | Usage |
|-------|------|-------|---------|--------|
| **qwen2.5:7b** | 7B | ⚡⚡⚡ | ⭐⭐⭐⭐ | Recommended |
| **gemma3:12b** | 12B | ⚡⚡ | ⭐⭐⭐⭐⭐ | Best quality |
| **llama3.1:8b** | 8B | ⚡⚡⚡ | ⭐⭐⭐⭐ | Very reliable |
| **gemma3:4b** | 4B | ⚡⚡⚡⚡ | ⭐⭐⭐ | Fast |

#### Output Format (JSON)

```json
{
  "title": "My Collection",
  "icon": "🎬",
  "type": "Films",
  "filename": "films.json",
  "categories": [
    {
      "id": 1,
      "name": "Science Fiction",
      "subcategories": [],
      "games": ["Blade Runner", "The Matrix"]
    },
    {
      "id": 2,
      "name": "Comedy",
      "subcategories": [],
      "games": ["Superbad", "The Hangover"]
    }
  ]
}
```

</details>

---


## 🗺 ToDo

- Extract Widget From Node : aiming at nodes using name, title or ID


---

## 📄 License

MIT License

---

## 👤 Author

**Tetsuoo**

---

## 🙏 Credits

- **Claude AI ❤** - AI assistant extraordinaire
- **ComfyUI** - Amazing node-based interface
- **Ollama** - Local LLM runtime
- **Krita** - Open-source digital painting software