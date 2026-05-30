# TOO LoRA Grid 🧪

Compare several LoRAs side by side by generating an image grid. Each cell corresponds to a different LoRA, with the same seed and the same parameters — ideal for quickly choosing the right LoRA or strength.

**Category:** `TOO-Pack/utils`

---

## 📋 Features

- **Comparison grid**: generates one image per LoRA, assembled into a grid
- **"null" slot**: include a cell without a LoRA as a reference
- **Automatic labels**: LoRA name (+ weight if specified) shown under each image
- **Footer**: free text under the grid (prompt, notes, etc.)
- **Internal cache**: already generated images are not recalculated if nothing has changed
- **Compatible** with SD, SDXL, FLUX, Cosmos/Anima

---

## ⚙️ Inputs

### Connections

| Entrée | Type | Description |
|--------|------|-------------|
| **model** | MODEL | Base model |
| **clip** | CLIP | CLIP encoder |
| **vae** | VAE | VAE for decoding latents |
| **positive** | CONDITIONING | Positive prompt |
| **negative** | CONDITIONING | Negative prompt |
| **latent_image** | LATENT | Starting latent |

### Sampling parameters

| Paramètre | Défaut | Description |
|-----------|--------|-------------|
| **seed** | `0` | Generation seed |
| **steps** | `20` | Number of steps |
| **cfg** | `7.0` | CFG scale |
| **sampler_name** | — | Sampler |
| **scheduler** | — | Scheduler |
| **denoise** | `1.0` | Denoising strength |

### LoRA list

The `loras` widget accepts one entry per line:

```
# commentaire ignoré
chemin/vers/lora.safetensors
chemin/vers/lora.safetensors:0.75
chemin/vers/lora.safetensors:"sans LoRA"
```

| Syntax | Result |
|---------|----------|
| `name.safetensors` | LoRA with weight `1.0`, label = filename |
| `name.safetensors:0.75` | LoRA with weight `0.75`, label = `name:0.75` |
| `name.safetensors:"label"` | Null slot (generates without LoRA), custom label |

> Paths are relative to ComfyUI’s `loras` folder.

### Grid parameters

| Paramètre | Défaut | Description |
|-----------|--------|-------------|
| **grid_cols** | `4` | Number of columns |
| **grid_padding** | `4` | Spacing between cells (px) |
| **add_labels** | `True` | Show labels under images |
| **label_height** | `24` | Label area height (px) |
| **font_size** | `14` | Label font size |
| **label_color** | `#ffffff` | Text color |
| **bg_color** | `#111111` | Grid background color |
| **footer_text** | — | Text shown under the grid (multiline supported) |

---

## 📤 Outputs

| Sortie | Type | Description |
|--------|------|-------------|
| **grid** | IMAGE | Complete assembled grid |
| **images** | IMAGE | Batch of all individual images |

---

## 💡 Examples

### Test 3 different strengths for the same LoRA

```
my_style.safetensors:0.5
my_style.safetensors:0.75
my_style.safetensors:1.0
my_style.safetensors:"référence"
```

The last line generates an image without a LoRA for comparison.

### Compare several LoRAs

```
styles/lora_A.safetensors
styles/lora_B.safetensors
styles/lora_C.safetensors
styles/lora_C.safetensors:0.5
```

---

## 📝 Notes

- The cache is based on all input parameters. Changing only `grid_cols`, `label_color`, etc. (visual parameters) does **not** regenerate the images — only the grid is rebuilt.
- Empty lines and lines starting with `#` are ignored.
- If no valid entry is found in `loras`, the node still generates an image without a LoRA.
