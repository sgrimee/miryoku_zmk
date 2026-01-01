# ZMK Layout PDF Generator

A standalone Python tool to generate PDF visualizations of ZMK keyboard layouts from `custom_config.h` files.

## Features

- Generates visual PDF representations of keyboard layers
- Shows key labels, modifiers, and layer access information
- Color-coded keys by function (navigation, modifiers, system keys, etc.)
- Displays physical and combined thumb keys
- Automatic layer discovery and grouping

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
uv run python src/generate_layout_pdf.py <config_file> [output_pdf]
```

### Arguments

- `<config_file>`: Path to your `custom_config.h` file (required)
- `[output_pdf]`: Path for the output PDF file (optional, defaults to `layout.pdf` in current directory)

### Examples

```bash
# Generate PDF from config file, output to current directory
uv run python src/generate_layout_pdf.py /path/to/custom_config.h

# Generate PDF with custom output path
uv run python src/generate_layout_pdf.py /path/to/custom_config.h my_layout.pdf

# Using from parent directory (e.g., in miryoku_zmk)
cd zmk_to_pdf
uv run python src/generate_layout_pdf.py ../miryoku/custom_config.h ../layout.pdf
```

## Development

### Install Development Dependencies

```bash
uv sync --dev
```

### Type Checking

```bash
uv run mypy src/generate_layout_pdf.py
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
3. **Determine access** - Identifies how each layer is accessed from the BASE layer
4. **Generate PDF** - Creates a visual representation with:
   - Color-coded keys by function
   - Layer access information
   - Physical and combined thumb keys
   - Multiple pages for layouts with many layers

## Color Coding

- **Green**: Navigation keys (arrows, home, end, etc.)
- **Pink**: Modifiers (Ctrl, Alt, Shift, GUI)
- **Blue**: Mouse and clipboard operations
- **Yellow**: System keys (Backspace, Enter, Delete, Escape, Space, Tab) and layer access keys
- **Purple**: Layer transitions
- **White**: Regular keys (letters, numbers, symbols)
- **Gray**: Empty or unavailable keys
- **Red dashed border**: Combined thumb keys

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
  - Access method (how to reach this layer)
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
   uv run python src/generate_layout_pdf.py /path/to/your/custom_config.h output.pdf
   ```
3. Optionally, adjust the `PDFConfig` class in the script to customize colors, fonts, and layout dimensions

## License

Part of the Miryoku ZMK project.
