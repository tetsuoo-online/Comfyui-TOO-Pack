# TOO Preset Text Node

Custom node for ComfyUI that allows managing text presets through a graphical interface.

## Usage

**Dropdown list**: Select an existing preset from the list

**"Manage" button**: Opens the preset management window where you can:
- Add new presets ("Add New" button)
- Edit existing presets
- Delete presets (by leaving the name or value empty)

**Output**: The node outputs the selected preset text as a STRING

### Saving

Presets are saved in:

```
Comfyui-TOO-Pack/presets/text_presets.json
```

This file is automatically created on first launch.

## Technical specifications

- **Category**: TOO/utils
- **Output type**: STRING
- **REST API**:
  - GET `/too/presets/list`: Lists all presets
  - POST `/too/presets/save`: Saves presets
- **Storage format**: JSON

## Notes

- Presets are shared across all instances of the node
- Modifying presets requires a page reload to update the dropdowns
- Preset names must be unique

## Possible future improvements

- Support for multiline fields (textarea) for values
- Preset import/export
- Preset categorization
- Real-time preview
