# Smart Image Loader 🖼️

A flexible image loader that supports multiple input sources with priority order.

**Category:** `TOO-Pack/image`

---

## 📋 Features

- **Multiple sources**: txt, direct path, directory, or direct image
- **Smart priority order** with configurable inputs
- **Random selection** with reproducible seed
- **Multiple formats** supported (PNG, JPG, JPEG, BMP, WEBP, TIFF)
- **Returns file path** of loaded image

---

## ⚙️ Parameters

### Required Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| **seed** | <span style="background-color:#1e4d3e;color:#34d399;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">INT</span> | Seed for reproducible random selection | `0` |
| **img_dir_level** | <span style="background-color:#1e4d3e;color:#34d399;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">INT</span> | Subdirectory depth: -1=all, 0=current, 1-10=levels | `0` |

### Optional Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| **txt_path** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Path to text file containing image paths | - |
| **img_path** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Direct path to an image file | - |
| **img_directory** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Path to directory containing images | - |
| **image** | <span style="background-color:#7c2d12;color:#fb923c;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">IMAGE</span> | Direct image input | - |

### Outputs

| Parameter | Type | Description |
|-----------|------|-------------|
| **IMAGE** | <span style="background-color:#7c2d12;color:#fb923c;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">IMAGE</span> | The loaded image as tensor |
| **FILE_PATH** | <span style="background-color:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em;">STRING</span> | Path of loaded file ("external_input" or "none") |

---

## 🎯 Priority Order

The node loads images in this order (from highest to lowest priority):

1. **txt_path** 📄 : Randomly selects a path from text file
2. **img_path** 🖼️ : Loads the specific image file
3. **img_directory** 📁 : Randomly selects an image from directory
4. **image** ⚡ : Uses the provided image input

---

## 💡 Usage Examples

### Case 1: Text file with image list
```python
# Content of image_list.txt:
# /path/to/image1.png
# /path/to/image2.jpg
# /path/to/image3.webp

txt_path = "/path/to/image_list.txt"
seed = 42  # Reproducible
```
➜ Randomly selects one image from the list

### Case 2: Direct path to image
```python
img_path = "/path/to/specific/image.png"
```
➜ Loads this image directly

### Case 3: Image directory
```python
img_directory = "/path/to/images/"
seed = 123
```
➜ Randomly selects an image from directory

### Case 4: Direct image input
```python
# Connect an IMAGE from another node
image = <IMAGE from another node>
```
➜ Uses the provided image

### Case 5: Combination with priority
```python
txt_path = "/path/to/list.txt"       # Priority 1
img_path = "/path/to/fallback.png"   # Priority 2 (if txt_path fails)
img_directory = "/path/to/backup/"   # Priority 3 (if img_path fails)
```
➜ Uses the first valid source found

---

## 📂 Supported Formats

| Extension | Description |
|-----------|-------------|
| `.png` | Portable Network Graphics |
| `.jpg`, `.jpeg` | JPEG |
| `.bmp` | Bitmap |
| `.webp` | WebP |
| `.tiff` | Tagged Image File Format |

---

## 🔧 Technical Details

### Text file format (txt_path)

The text file should contain one image path per line:

```
/home/user/images/photo1.png
/home/user/images/photo2.jpg
/home/user/images/photo3.webp
```

- Empty lines are ignored
- UTF-8 encoding supported
- A random path is selected using the seed

### Seed handling

- **seed = 0**: Different random selection each run
- **seed > 0**: Identical selection with same parameters (reproducible)

### FILE_PATH values

| Value | Description |
|-------|-------------|
| Full path | Image loaded from txt_path, img_path or img_directory |
| `"external_input"` | Image provided via image parameter |
| `"none"` | No valid source found (error) |

---

## 🔧 Troubleshooting

### ❌ "No valid image source found"
- Check that at least one optional parameter is provided
- Check that paths exist and are accessible
- Check read permissions

### ❌ "Error loading image"
- Check that the file is a valid image
- Check format (must be in supported list)
- Check that file is not corrupted

### ❌ "Error reading txt_path"
- Check that text file exists
- Check encoding (UTF-8 recommended)
- Check that paths in file are valid

### ⚠️ Always same image
- Increase seed value to vary selection
- Check that you have multiple images in your source

---

## 📝 Notes

- Node automatically converts all images to RGB
- Images are normalized (0-1 values) for ComfyUI
- Seed only affects txt_path and img_directory (random selection)
- img_path and image input are not affected by seed

---

## 📄 License

MIT

---

## 🙏 Credits

- **ComfyUI** - Node-based framework
- **PIL/Pillow** - Image manipulation
- **PyTorch** - Tensors for ComfyUI

---

## 📧 Contact

To report a bug or suggest an improvement:
- Create an issue
- Submit a PR
