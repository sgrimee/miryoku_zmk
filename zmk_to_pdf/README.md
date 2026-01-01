# ZMK Layout PDF Generator

A standalone Python tool to generate PDF visualizations of ZMK keyboard layouts from `custom_config.h` files.

## Features

- Generates visual PDF representations of keyboard layers
- Shows key labels, modifiers, and layer access information
- Color-coded keys by function (navigation, modifiers, system keys, access keys, etc.)
- Displays physical and combined thumb keys
- Automatic layer discovery and grouping
- Clear visual distinction between access keys and system keys

## Requirements

- Python 3.11 or higher
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

## Installation

### Using uv (recommended)

```bash
# No installation needed - uv will handle dependencies automatically
```

### Using pip

```bash
pip install -r pyproject.toml
```

## Usage

### Basic Usage

```bash
uv run python -m zmk_to_pdf <config_file> [output_pdf]
```

### Arguments

- `<config_file>`: Path to your `custom_config.h` file (required)
- `[output_pdf]`: Path for the output PDF file (optional, defaults to `layout.pdf` in current directory)

### Examples

```bash
# Generate PDF from config file, output to current directory
uv run python -m zmk_to_pdf /path/to/custom_config.h

# Generate PDF with custom output path
uv run python -m zmk_to_pdf /path/to/custom_config.h my_layout.pdf

# Using from parent directory (e.g., in miryoku_zmk)
cd zmk_to_pdf
uv run python -m zmk_to_pdf ../miryoku/custom_config.h ../layout.pdf
```

## Development

### Install Development Dependencies

```bash
uv sync --dev
```

### Type Checking

```bash
uv run mypy src/
```

### Code Formatting

```bash
uv run ruff check src/
uv run ruff format src/
```

## How It Works

The tool parses ZMK `custom_config.h` files to:

1. **Discover layers** - Finds all `MIRYOKU_LAYER_*` definitions
2. **Parse key codes** - Translates ZMK key codes to readable labels
3. **Determine access** - Identifies how each layer is accessed from the BASE layer using `U_LT` macros
4. **Generate PDF** - Creates a visual representation with:
   - Color-coded keys by function
   - Layer access information (position-based, layout-agnostic)
   - Physical and combined thumb keys
   - Multiple pages for layouts with many layers

## Color Coding

| Color | Hex Code | Purpose |
|-------|----------|---------|
| 🟨 Khaki/Yellow | #F0E68C | **Access keys** - thumb key used to access this layer from BASE |
| 🟦 Light Blue | #ADD8E6 | **System keys** - Backspace, Enter, Delete, Escape, Space, Tab |
| 🟩 Light Green | #90EE90 | **Navigation keys** - Arrows, Home, End, Page Up/Down |
| 🟥 Light Pink | #FFB6C1 | **Modifiers** - Ctrl, Alt, Shift, GUI |
| 🟦 Cyan | #87CEEB | **Mouse/Clipboard** - BTN1, BTN2, BTN3, Undo, Cut, Copy, Paste, Redo |
| 🟪 Plum | #DDA0DD | **Layer transitions** - Layer names like BOOT, →NAV, →NUM, etc. |
| ⬜ Light Gray | #CCCCCC | **Empty** - Unavailable key slots |
| ⬜ White | #FFFFFF | **Regular keys** - Letters, numbers, symbols |

### Understanding Access Keys

Each layer (except TAP) has exactly **one yellow access key** on the thumb row. This represents the thumb key you hold in the BASE layer to enter that layer.

Example: In the NUM layer, the left outer thumb is yellow because you hold that key (mapped to SPACE in BASE) to access the NUM layer.

## Layer Access Text

Access information is shown as position names (not key codes) to remain stable regardless of layout customization:

- `Access: left outer` - Hold the left outer thumb key
- `Access: left inner` - Hold the left inner thumb key
- `Access: left combined` - Hold the combined left thumb key
- `Access: right inner` - Hold the right inner thumb key
- `Access: right outer` - Hold the right outer thumb key
- `Access: right combined` - Hold the combined right thumb key

## Supported Key Codes

The tool supports a wide range of ZMK key codes including:

- Basic letters (A-Z) and numbers (0-9)
- Symbols and punctuation
- Navigation keys (arrows, home, end, page up/down)
- Function keys (F1-F12)
- Modifiers (Ctrl, Alt, Shift, GUI)
- System keys (Backspace, Enter, Delete, etc.)
- Layer transitions (`U_LT`, `&u_to_*`)
- Mod-tap behaviors (`U_MT`)
- Mouse keys and clipboard operations
- Media controls

## Output Format

The generated PDF includes:

- **Title**: "Miryoku Keyboard Layers"
- **Legend**: Explanation of combined thumb keys
- **Layer sections**: Each layer shows:
   - Layer name
   - Access method (which thumb key accesses this layer)
   - Left and right hand key layouts (3 rows of 5 keys each)
   - Physical thumb keys (2 per hand)
   - Combined thumb keys (1 per hand, shown with red dashed border)
- **Page numbers**: Multi-page layouts are numbered

## Reusing in Other Projects

This tool is designed to be reusable. To integrate it into your own ZMK project:

1. Copy the `zmk_to_pdf` directory to your project
2. Update your build scripts to call the generator:
   ```bash
   cd zmk_to_pdf
   uv run python -m zmk_to_pdf /path/to/your/custom_config.h output.pdf
   ```
3. Optionally, adjust the `PDFConfig` class in `src/zmk_to_pdf/config.py` to customize colors, fonts, and layout dimensions

## License

Part of the Miryoku ZMK project.

