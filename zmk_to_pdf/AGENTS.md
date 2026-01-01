# ZMK Layout PDF Generator - Agent Guidelines

This document provides guidance for agentic coding assistants working on the ZMK Layout PDF Generator tool.

## Project Overview

**ZMK Layout PDF Generator** is a standalone Python tool that parses ZMK keyboard layout configuration files and generates visual PDF documentation. It reads `custom_config.h` files containing layer definitions and produces color-coded keyboard layout diagrams.

- **Language**: Python 3.11+
- **Dependencies**: reportlab (PDF generation)
- **Package Manager**: uv (recommended) or pip
- **Type Checking**: mypy with type hints throughout
- **Code Quality**: ruff for linting and formatting

## Project Structure

```
zmk_to_pdf/
├── src/
│   └── generate_layout_pdf.py    # Main script (all-in-one implementation)
├── pyproject.toml                 # Project configuration and dependencies
├── uv.lock                        # Locked dependency versions
├── README.md                      # User documentation
└── AGENTS.md                      # This file
```

## Build & Test Commands

### Running the Script

```bash
# From zmk_to_pdf directory
uv run python src/generate_layout_pdf.py <config_file> [output_pdf]

# Example
uv run python src/generate_layout_pdf.py ../miryoku/custom_config.h ../layout.pdf
```

### Development Setup

```bash
# Install all dependencies including dev tools
uv sync --dev

# Type checking
uv run mypy src/generate_layout_pdf.py

# Code formatting
uv run ruff format src/

# Linting
uv run ruff check src/
```

### Testing

```bash
# Test with a real config file (if miryoku is in parent directory)
uv run python src/generate_layout_pdf.py ../miryoku/custom_config.h test_output.pdf

# Verify PDF was created
ls -lh test_output.pdf
```

## Code Style Guidelines

### File Organization

The script is organized as a single-file implementation with clear sections:

1. **Constants** - `KEY_CODE_MAP` translation table
2. **Data Models** - TypedDict and dataclass definitions
3. **Key Colorizer** - Color determination logic
4. **PDF Renderer** - Drawing and layout functions
5. **Parsing Functions** - Config file parsing and layer extraction
6. **Main Logic** - Entry point and orchestration

### Naming Conventions

#### Classes
- **Case**: PascalCase
- **Examples**: `PDFConfig`, `KeyColorizer`, `PDFRenderer`
- **TypedDict**: Use for structured dictionaries (`LayerData`, `ThumbKeysDict`, etc.)
- **Dataclass**: Use for configuration objects with defaults (`PDFConfig`)

#### Functions
- **Case**: snake_case
- **Pattern**: Verb-first for actions (`parse_layer_keys`, `draw_key`, `generate_access_text`)
- **Internal**: Prefix with underscore if truly private (rare in this project)

#### Variables
- **Case**: snake_case
- **Constants**: ALL_UPPERCASE for module-level constants (`KEY_CODE_MAP`)
- **Type hints**: Required for all function signatures

#### Key Code Constants
- **Pattern**: `&kp X` format for ZMK key codes in `KEY_CODE_MAP`
- **Macro patterns**: `U_MT`, `U_LT`, `U_NP`, `U_NA`, etc.
- **Layer references**: `&u_to_U_LAYERNAME` format

### Type Hints

**All functions must have complete type hints:**

```python
def parse_layer_keys(definition: str) -> list[str | None]:
    """Parse a layer definition into list of 40 key codes."""
    ...

def draw_key(
    self,
    pdf: canvas.Canvas,
    x: float,
    y: float,
    text: str | None,
    is_combined: bool = False,
    is_inactive: bool = False,
    is_access_key: bool = False,
) -> None:
    """Draw a single key."""
    ...
```

### Formatting Standards

#### Line Length
- **Soft limit**: 88 characters (ruff default)
- **Hard limit**: 100 characters for clarity
- Long lines should be broken at logical points

#### String Formatting
- Use **f-strings** for string interpolation
- Use **raw strings** (`r"..."`) for regex patterns
- Use **triple quotes** for docstrings

#### Docstrings
- **Style**: Google-style docstrings
- **Required**: All public functions and classes
- **Content**: Include Args, Returns, and examples where helpful

Example:
```python
def extract_thumb_keys(tap_keys: list[str | None]) -> dict[str, ThumbKeysDict]:
    """Extract thumb key labels from TAP layer.

    Thumb row is indices 30-39 (out of 40 total keys):
    [30, 31] = U_NP (None, not present)
    [32] = left_combined
    ...

    Returns:
        Dictionary with "left" and "right" thumb key structures
    """
```

### Error Handling

#### User-Facing Errors
Use `sys.exit()` with clear error messages:

```python
if len(sys.argv) < 2:
    sys.exit("Usage: generate_layout_pdf.py <config_file> [output_pdf]")

if not config_path.exists():
    sys.exit(f"ERROR: Config file not found: {config_path}")
```

#### Parse Errors
Provide context about what failed:

```python
if base_def is None:
    sys.exit("ERROR: Could not find MIRYOKU_LAYER_BASE in config")

if len(tap_keys) < 38:
    sys.exit(f"ERROR: TAP layer has {len(tap_keys)} keys, expected at least 38")
```

#### Warnings vs Errors
- **Errors**: Missing required layers (BASE), file not found, invalid arguments
- **Warnings**: Optional layers missing, skipped layers with parsing issues

### Data Structures

#### TypedDict for Structured Data

```python
class LayerData(TypedDict):
    """Complete layer structure for rendering."""
    left_hand: list[list[str | None]]
    right_hand: list[list[str | None]]
    left_thumbs: ThumbKeysActive
    right_thumbs: ThumbKeysActive
    access: str
```

#### Dataclass for Configuration

```python
@dataclass
class PDFConfig:
    """PDF rendering configuration and constants."""
    key_width: float = 0.60
    key_height: float = 0.34
    # ... more fields with defaults
```

### Color Management

#### Hex Color Format
All colors in `PDFConfig` use hex strings:

```python
color_navigation: str = "#90EE90"
color_modifier: str = "#FFB6C1"
color_system: str = "#F0E68C"
```

#### Color Usage
Convert to ReportLab colors with `HexColor()`:

```python
bg_color = HexColor(self.config.color_navigation)
pdf.setFillColor(bg_color)
```

## Key Concepts

### Layer Structure

Each ZMK layer has **40 keys** (for Miryoku):
- **Finger keys**: Indices 0-29 (3 rows × 10 keys)
  - Left hand: columns 0-4 in each row
  - Right hand: columns 5-9 in each row
- **Thumb keys**: Indices 30-39
  - Indices 30-31, 38-39: `U_NP` (not present)
  - Indices 32-37: Actual thumb keys (combined + physical)

### Key Code Translation

The `KEY_CODE_MAP` dictionary translates ZMK codes to display labels:

```python
"&kp A": "A"
"&kp LEFT": "←"
"&u_to_U_NAV": "→NAV"
"U_NP": None  # Filtered out
```

### Macro Handling

Special handling for ZMK macros:

- **`U_MT(MOD, KEY)`**: Mod-tap behavior → extract and translate `KEY`
- **`U_LT(LAYER, KEY)`**: Layer-tap behavior → extract and translate `KEY`
- **`U_NP`**: Not present → returns `None` (filtered out)

### Layer Access Detection

The script analyzes the BASE layer to determine how other layers are accessed:

1. Find all `U_LT(U_LAYERNAME, KEY)` patterns
2. Map layer name to accessing key(s)
3. Generate descriptive access text
4. Highlight access keys in yellow on layer diagrams

### PDF Layout

**Coordinate system**: Bottom-left origin (ReportLab standard)

**Structure**:
- Title and legend at top
- Up to 4 layers per page
- Each layer shows:
  - Left and right hand grids (3×5 keys each)
  - Physical thumb keys (2 per hand)
  - Combined thumb keys (1 per hand, red dashed border)
  - Layer name and access information

## Common Tasks

### Adding Support for New Key Codes

1. Add entry to `KEY_CODE_MAP`:
   ```python
   "&kp NEW_KEY": "LABEL",
   ```

2. Optionally update `KeyColorizer.get_colors()` if special color needed:
   ```python
   if "SPECIAL" in text:
       return (HexColor(self.config.color_special), black)
   ```

### Modifying PDF Layout

1. Adjust dimensions in `PDFConfig` dataclass
2. Update `draw_layer_section()` calculation logic if needed
3. Test with `just pdf` from parent directory

### Changing Color Scheme

1. Update hex colors in `PDFConfig`
2. Modify `KeyColorizer.get_colors()` logic if categorization changes
3. Update README.md color legend

### Adding New Layer Information

1. Define new TypedDict or extend `LayerData`
2. Update parsing functions to extract data
3. Update `draw_layer_section()` to render new information
4. Add tests/examples

### Debugging Parse Errors

The script includes helpful debug output:

```python
print(f"Discovered layers: {layers_to_display}")
print(f"  Processing layer: {layer_name}")
print(f"Page groupings: {page_groupings}")
```

Add more `print()` statements as needed during development.

## Dependencies

### Core Dependencies

- **reportlab** (≥4.0.0): PDF generation library
  - Used for: Canvas, colors, drawing primitives
  - Key APIs: `canvas.Canvas`, `HexColor`, `letter` page size

### Development Dependencies

- **mypy** (≥1.19.1): Static type checker
- **ruff** (≥0.14.10): Fast Python linter and formatter
- **types-reportlab** (≥4.4.7.20251223): Type stubs for reportlab

### Python Version

- **Minimum**: Python 3.11
- **Reason**: Modern type hint syntax (e.g., `list[str]`, `dict[str, int]`)

## Testing Strategy

### Manual Testing

1. **Valid input**: Test with known good `custom_config.h`
2. **Missing layers**: Remove optional layers, verify graceful handling
3. **Invalid syntax**: Test error messages for malformed input
4. **Edge cases**: Unusual key combinations, long layer names

### Regression Testing

When making changes:

1. Generate PDF with current version
2. Make changes
3. Generate PDF again
4. Compare outputs visually or with diff tools

### Type Checking

Always run mypy before committing:

```bash
uv run mypy src/generate_layout_pdf.py
```

Should produce no errors or warnings.

## Performance Considerations

### Parsing

- Regex patterns are compiled once per match (Python default)
- File is read once into memory
- No heavy computation or iteration

### PDF Generation

- ReportLab is optimized for PDF creation
- Most time spent in font rendering and drawing
- Typical execution time: < 1 second for most configs

### Memory Usage

- Entire config file loaded into memory (typically < 100KB)
- Layer data structures are small (< 1MB total)
- PDF generation is incremental (low memory overhead)

## Integration with Parent Projects

This tool is designed to be **standalone and reusable**.

### Using from Another ZMK Project

1. **Copy directory**: Copy entire `zmk_to_pdf/` to your project
2. **Install dependencies**: Run `uv sync` in the directory
3. **Call script**: 
   ```bash
   cd zmk_to_pdf
   uv run python src/generate_layout_pdf.py /path/to/custom_config.h output.pdf
   ```

### Using from Build Scripts

Example justfile recipe:

```justfile
pdf:
    cd zmk_to_pdf && uv run python src/generate_layout_pdf.py ../config/custom_config.h ../layout.pdf
```

Example Makefile:

```makefile
layout.pdf: config/custom_config.h
    cd zmk_to_pdf && uv run python src/generate_layout_pdf.py ../$< ../$@
```

## Versioning and Compatibility

### Semantic Versioning

Follow semver (major.minor.patch):
- **Major**: Breaking changes to command-line interface or output format
- **Minor**: New features, new key code support
- **Patch**: Bug fixes, documentation updates

### Config File Compatibility

The tool should handle:
- Standard Miryoku layer definitions
- Custom layer names
- Missing optional layers (TAP, etc.)
- Future ZMK key codes (fall back to raw code display)

## Known Limitations

1. **Fixed layout assumption**: Assumes 40-key Miryoku layout
2. **No validation**: Doesn't validate ZMK syntax, just parses patterns
3. **English only**: Labels and messages are in English
4. **Single file output**: Generates one PDF file, not multiple formats

## Future Enhancements

Potential improvements (not currently implemented):

- Support for non-Miryoku layouts (configurable key counts)
- SVG output in addition to PDF
- Interactive HTML output
- Configuration file for colors and layout
- Unit tests with pytest
- CI/CD with GitHub Actions

## Getting Help

When working on this project:

1. **Read the code**: Single-file implementation is well-documented
2. **Check README.md**: User-facing documentation
3. **Run type checker**: `mypy` catches many issues
4. **Test incrementally**: Make small changes and test often
5. **Study examples**: Look at `KEY_CODE_MAP` and parsing patterns

## Best Practices

### When Adding Features

1. Maintain single-file structure (easier to distribute)
2. Add type hints for all new functions
3. Update docstrings with examples
4. Add new key codes to `KEY_CODE_MAP`
5. Update README.md with new capabilities

### When Fixing Bugs

1. Identify minimal reproduction case
2. Add debug output if needed
3. Fix the root cause, not symptoms
4. Test with original failing case
5. Remove debug output before committing

### When Refactoring

1. Keep the command-line interface stable
2. Maintain backward compatibility with config files
3. Run type checker after changes
4. Verify PDF output looks correct
5. Update documentation if behavior changes

## Code Review Checklist

Before considering changes complete:

- [ ] Type hints added to all new functions
- [ ] Docstrings added to all public functions
- [ ] Error messages are clear and actionable
- [ ] Code follows snake_case naming
- [ ] `mypy` passes with no errors
- [ ] `ruff format` applied to code
- [ ] `ruff check` passes with no errors
- [ ] Manual test with real config file succeeds
- [ ] README.md updated if user-facing changes
- [ ] AGENTS.md updated if development process changes
