# 💾 TOO Smart Image Saver (Advanced)

Node for saving images with advanced file naming and A1111/Civitai Auto V3 compatible metadata.

**Category:** TOO-Pack/image

## Features

- Dynamic file naming with workflow extraction
- Metadata injection/editing
- Support for 3 universal inputs (`any1`, `any2`, `any3`)
- Automatic model and LoRA extraction with hash calculation
- Targeted text replacement
- Customizable date formatting
- A1111/Civitai compatible metadata
- Output formats: PNG, JPG, WebP

## Inputs

| Parameter | Type | Description |
|-----------|------|-------------|
| `images` | IMAGE | Images to save (required) |
| `metadata` | METADATA | Optional metadata |
| `workflow` | WORKFLOW | Workflow to embed |
| `any1` | * | Universal input 1 |
| `any2` | * | Universal input 2 |
| `any3` | * | Universal input 3 |

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| `images` | IMAGE | Images passthrough |
| `filepath` | STRING | Saved file path |

## Configuration (JS Interface)

### DATA
Create custom data fields for metadata and naming.

**Value formats:**
- **Static text:** `"my_text"`
- **Widget extraction:** `#123:widget_name` (node ID) or `ClassName:widget_name`
- **Any input:** `[any1]`, `[any2]`, `[any3]`

**Example:**
```
name: positive
value: #45:text

name: model_used
value: [any1]
```

### DATE FORMAT
Format dates for naming.

- **date1:** Date format (e.g. `YYYY-MM-DD`)
- **date2:** Time format (e.g. `HHmmss`)
- **date3:** Custom format

**Available tokens:** `YYYY`, `YY`, `MM`, `DD`, `HH`, `mm`, `ss`, `timestamp`

### MODEL
Automatic model extraction.

**Value:** `#123:ckpt_name` or `[any1]`

The node automatically calculates:
- Model name (basename without extension)
- Model hash (first 10 characters of SHA256)

### LORAS
Automatic LoRA extraction with Civitai-compatible hash.

**Add multiple loras:**
- Lora 1: `#45:lora_name` or `[any1]`
- Lora 2: `#67:lora_name` or `[any2]`

**Multiline support:** If `[any1]` contains:
```
lora1.safetensors
lora2.safetensors
```
→ Both are parsed automatically

### TEXT REPLACE
Replace text in fields before naming.

**Target:**
- Empty or `[any1]`/`[any2]`/`[any3]` → Apply to all fields
- `positive` → Apply only to "positive" field
- `model` → Apply only to model

**Example:**
```
target: positive
in: (masterpiece)
out: 
```
→ Removes "(masterpiece)" from positive prompt

### NAMING
Build filename with available elements.

**Available fields:**
- `output_folder` : Output subfolder
- `prefix` : File prefix
- `extra1`, `extra2`, `extra3` : Additional fields
- `model` : Model name
- `suffix` : File suffix
- `separator` : Separator character (default: `_`)

**Available sources:**
- Empty (ignored)
- `[any1]`, `[any2]`, `[any3]` : Universal inputs
- Data field name: `positive`, `seed`, `steps`, etc.
- `model`, `loras` : Extracted values
- `%date1`, `%date2`, `%date3` : Formatted dates

**Naming example:**
```
prefix: %date1
extra1: positive
model: model
suffix: seed
separator: _
```
→ `2025-02-12_beautiful_landscape_MyModel_12345.webp`

### OUTPUT
Output configuration.

- **format:** `png`, `jpg`, `webp`
- **quality:** 1-100 (for jpg/webp)
- **save metadata:** Include A1111 metadata
- **embed workflow:** Embed ComfyUI workflow (except JPG)

## Usage Examples

### Example 1: Naming with model and seed

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

**Result:** `2025-02-12_MyCheckpoint_8675309.webp`

### Example 2: LoRA extraction from any1

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

**If any1 contains:**
```
style_lora_v2.safetensors
quality_lora_v1.safetensors
```

**Generated metadata:**
```
Lora hashes: "style_lora_v2: a1b2c3d4e5f6, quality_lora_v1: f6e5d4c3b2a1"
```

### Example 3: Prompt cleanup with Text Replace

**Configuration:**
```
TEXT REPLACE:
  - target: positive
  - in: (masterpiece, best quality)
  - out: 

NAMING:
  - prefix: positive
```

**If positive = "beautiful landscape, (masterpiece, best quality)"**  
**→ Filename:** `beautiful_landscape.webp`

## Practical Use Cases

### 1. Multi-LoRA Workflow
Use `ExtractWidgetFromNode` to retrieve all used LoRAs → connect to `any1` → The node automatically calculates all hashes for Civitai compatibility.

### 2. Organization by Model
Configure `output_folder: model` to automatically sort images by model used.

### 3. Complete Metadata
Create data fields for all important parameters (seed, steps, cfg, sampler, scheduler) → The node generates complete A1111 metadata readable by Civitai and Automatic1111.

### 4. Smart Naming
Use `any` inputs to inject dynamic information from other nodes (tags, descriptions, scores, etc.).

## Tips

- **Data fields** are flexible: create as many fields as needed
- **[any1]**, **[any2]**, **[any3]** accept any data type (converted to string)
- **Multiline** is supported for loras: one line = one lora
- **LoRA hashes** exclude safetensors metadata (Civitai AutoV3 compatible)
- **Text replace** applies to extracted values before filename construction
- **Empty lines** in data fields are automatically ignored
- The **metadata** input has priority over node data fields, unless data fields are explicitly set (enables metadata injection/editing)
