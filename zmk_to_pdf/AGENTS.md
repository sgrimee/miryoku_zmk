# ZMK Layout PDF Generator - Agent Guidelines

This document provides guidance for agentic coding assistants working on the ZMK Layout PDF Generator tool.

## Project Overview

**ZMK Layout PDF Generator** is a standalone Python tool that parses ZMK keyboard layout configuration files and generates visual PDF documentation. It reads `custom_config.h` files containing layer definitions and produces color-coded keyboard layout diagrams with layer access information.

- **Language**: Python 3.11+
- **Dependencies**: reportlab (PDF generation), pdf2image (optional, for testing)
- **Package Manager**: uv (recommended) or pip
- **Type Checking**: mypy with type hints throughout
- **Code Quality**: ruff for linting and formatting

## Project Structure

```
zmk_to_pdf/
├── src/
│   └── zmk_to_pdf/
│       ├── __main__.py                 # CLI entry point
│       ├── main.py                     # Main orchestration
│       ├── config.py                   # PDF configuration and colors
│       ├── parser.py                   # ZMK config file parsing
│       ├── key_code_map.py            # Key code translation and colorization
│       ├── layer_processor.py         # Layer data processing
│       ├── data_models.py             # TypedDict data structures
│       └── pdf_renderer.py            # PDF drawing and rendering
├── tests/
│   ├── fixtures/                       # Test data files
│   ├── conftest.py                     # Pytest configuration
│   ├── test_parser.py                  # Parser unit tests
│   ├── test_key_code_map.py           # Key code translation tests
│   ├── test_layer_processor.py        # Layer processing tests
│   ├── test_pdf_renderer.py           # Renderer tests
│   └── test_data_models.py            # Data structure tests
├── pyproject.toml                      # Project configuration and dependencies
├── uv.lock                             # Locked dependency versions
├── README.md                           # User documentation
├── AGENTS.md                           # This file
└── justfile                            # Development recipes

```

## Build & Test Commands

### Running the Tool

```bash
# From zmk_to_pdf directory (module invocation)
uv run python -m zmk_to_pdf <config_file> [output_pdf]

# Example
uv run python -m zmk_to_pdf ../miryoku/custom_config.h ../layout.pdf
```

### Development Setup

```bash
# Install all dependencies including dev tools
uv sync --dev

# Type checking
uv run mypy src/

# Code formatting and linting
uv run ruff format src/ tests/
uv run ruff check src/ tests/

# Run all tests
uv run pytest tests/ -v
```

### Testing

```bash
# Run specific test file
uv run pytest tests/test_parser.py -v

# Run with coverage
uv run pytest tests/ --cov=src/zmk_to_pdf

# Test with real config file (if miryoku is in parent directory)
uv run python -m zmk_to_pdf ../miryoku/custom_config.h test_output.pdf

# Verify PDF was created
ls -lh test_output.pdf
```

## Code Style Guidelines

### File Organization

The project is organized into focused modules:

1. **`__main__.py`** - CLI entry point and argument parsing
2. **`main.py`** - High-level orchestration (generate_pdf function)
3. **`config.py`** - PDFConfig dataclass with all configuration and colors
4. **`data_models.py`** - TypedDict definitions for data structures
5. **`parser.py`** - Config file parsing and layer extraction
6. **`key_code_map.py`** - Key code translation and KeyColorizer logic
7. **`layer_processor.py`** - Layer data processing and access detection
8. **`pdf_renderer.py`** - PDF drawing and rendering logic

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
- **Constants**: ALL_UPPERCASE for module-level constants
- **Type hints**: Required for all function signatures

#### Key Code Constants
- **Pattern**: `&kp X` format for ZMK key codes in key_code_map.yaml
- **Macro patterns**: `U_MT`, `U_LT`, `U_NP`, `U_NA`, etc.
- **Layer references**: `&u_to_U_LAYERNAME` format

### Type Hints

**All functions must have complete type hints:**

```python
def parse_layer_keys(definition: str, key_map: KeyCodeMap) -> list[str | None]:
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
- **Content**: Include Args, Returns, Raises, and examples where helpful

Example:
```python
def extract_thumb_keys(
    tap_keys: list[str | None],
) -> dict[str, ThumbKeyLabelDict]:
    """Extract thumb key labels from TAP layer.

    Thumb row is indices 30-39 (out of 40 total keys):
    [30, 31] = U_NP (None, not present)
    [32] = left_combined
    [33] = left_outer
    [34] = left_inner
    [35] = right_inner
    [36] = right_outer
    [37] = right_combined
    [38, 39] = U_NP (None, not present)

    Args:
        tap_keys: List of 40+ key labels from TAP layer

    Returns:
        Dictionary with "left" and "right" thumb key structures

    Raises:
        SystemExit: If layer has fewer than 38 keys
    """
```

### Error Handling

#### User-Facing Errors
Use `sys.exit()` with clear error messages:

```python
if len(sys.argv) < 2:
    sys.exit("Usage: python -m zmk_to_pdf <config_file> [output_pdf]")

if not config_path.exists():
    sys.exit(f"ERROR: Config file not found: {config_path}")
```

#### Parse Errors
Provide context about what failed:

```python
if base_def is None:
    sys.exit("ERROR: Could not find MIRYOKU_LAYER_BASE in config")

if len(tap_keys) < 38:
    sys.exit(
        f"ERROR: Layer for thumb keys has {len(tap_keys)} keys, expected at least 38"
    )
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
color_navigation: str = "#90EE90"      # Light green
color_modifier: str = "#FFB6C1"        # Light pink
color_system: str = "#ADD8E6"          # Light blue
color_access_key: str = "#F0E68C"      # Khaki/yellow
```

#### Color Usage in Code
Convert to ReportLab colors with `HexColor()`:

```python
if is_access_key:
    bg_color = HexColor(self.config.color_access_key)
else:
    bg_color, text_color = self.colorizer.get_colors(text, is_inactive)
```

#### Color Semantics
**Important**: Different colors have specific meanings:

- `color_access_key` (#F0E68C): Thumb key used to enter this layer
- `color_system` (#ADD8E6): System keys (BSPC, RET, DEL, etc.)
- `color_navigation` (#90EE90): Arrow keys and navigation
- `color_modifier` (#FFB6C1): Modifier keys (Ctrl, Alt, Shift, GUI)
- `color_mouse_clipboard` (#87CEEB): Mouse buttons and clipboard operations
- `color_layer_access` (#DDA0DD): Layer transition names

## Key Concepts

### Layer Structure

Each ZMK layer has **40 keys** (for Miryoku):
- **Finger keys**: Indices 0-29 (3 rows × 10 keys)
  - Left hand: columns 0-4 in each row
  - Right hand: columns 5-9 in each row
- **Thumb keys**: Indices 30-39
  - Indices 30-31, 38-39: `U_NP` (not present)
  - Indices 32-37: Actual thumb keys (combined + physical)

### Thumb Key Layout

```
Left hand:                    Right hand:
Col 3-4 (physical):          Col 0-1 (physical):
[32] [33] [34]              [35] [36] [37]
    \  /                       \  /
   [combined]                 [combined]
```

### Key Code Translation

The `KeyCodeMap` loads translations from YAML and translates ZMK codes to display labels:

```
&kp A → "A"
&kp LEFT → "←"
&u_to_U_NAV → "→NAV"
U_NP → None (filtered out)
&kp BSPC → "BSPC"
```

### Macro Handling

Special handling for ZMK macros:

- **`U_MT(MOD, KEY)`**: Mod-tap behavior → extract and translate `KEY`
- **`U_LT(LAYER, KEY)`**: Layer-tap behavior → extract and translate `KEY`
- **`U_NP`**: Not present → returns `None` (filtered out)

### Layer Access Detection

The script analyzes the BASE layer to determine how other layers are accessed:

1. Find all `U_LT(U_LAYERNAME, KEY)` patterns in BASE layer
2. Map layer name to accessing thumb key position and key name
3. Generate position-only access text (e.g., "Access: left outer")
4. Highlight access key in yellow on layer diagrams
5. Highlight thumb keys as follows:
   - Yellow: Access key (always exactly one per layer, or none for TAP)
   - Light blue: System keys (BSPC, RET, DEL, etc.)
   - Other colors: Navigation, modifiers, etc.

### PDF Layout

**Coordinate system**: Bottom-left origin (ReportLab standard)

**Structure**:
- Title and legend at top (position-only, layout-agnostic)
- Up to 4 layers per page
- Each layer shows:
  - Left and right hand grids (3×5 keys each)
  - Physical thumb keys (2 per hand)
  - Combined thumb keys (1 per hand, red dashed border)
  - Layer name and access information (position-based)

## Common Tasks

### Adding Support for New Key Codes

1. Add entry to `src/zmk_to_pdf/key_code_map.yaml`:
   ```yaml
   "&kp NEW_KEY": "LABEL"
   ```

2. Optionally update `KeyColorizer.get_colors()` in `key_code_map.py` if special color needed:
   ```python
   if "SPECIAL" in text:
       return (HexColor(self.config.color_special), black)
   ```

3. Add test case to `tests/test_key_code_map.py`

### Modifying PDF Layout

1. Adjust dimensions in `PDFConfig` dataclass in `config.py`
2. Update `draw_layer_section()` calculation logic in `pdf_renderer.py` if needed
3. Test with `uv run python -m zmk_to_pdf ../miryoku/custom_config.h test.pdf`
4. Verify PDF visually

### Changing Color Scheme

1. Update hex colors in `PDFConfig` in `config.py`
2. Modify `KeyColorizer.get_colors()` logic in `key_code_map.py` if categorization changes
3. Update README.md color legend table
4. Ensure `color_access_key` is used for access keys in `pdf_renderer.py`
5. Test with real configuration

### Adding New Layer Information

1. Define new TypedDict or extend `LayerData` in `data_models.py`
2. Update parsing functions in `parser.py` to extract data
3. Update `build_layer_data()` in `layer_processor.py` to populate new fields
4. Update `draw_layer_section()` in `pdf_renderer.py` to render new information
5. Add tests in `tests/test_layer_processor.py`

### Debugging Parse Errors

The script includes helpful debug output:

```python
print(f"Discovered layers: {layers_to_display}")
print(f"  Processing layer: {layer_name}")
print(f"Page groupings: {page_groupings}")
```

Add more `print()` statements as needed during development. Run with:

```bash
uv run python -m zmk_to_pdf <config> output.pdf 2>&1
```

## Dependencies

### Core Dependencies

- **reportlab** (≥4.0.0): PDF generation library
  - Used for: Canvas, colors, drawing primitives
  - Key APIs: `canvas.Canvas`, `HexColor`, `letter` page size

- **PyYAML** (≥6.0): YAML parsing for key code mappings
  - Used for: Loading key_code_map.yaml

### Development Dependencies

- **mypy** (≥1.19.1): Static type checker
- **ruff** (≥0.14.10): Fast Python linter and formatter
- **pytest** (≥8.0.0): Testing framework
- **types-reportlab** (≥4.4.7.20251223): Type stubs for reportlab

### Optional Dependencies

- **pdf2image** (for testing/debugging): Convert PDF pages to images for visual inspection

### Python Version

- **Minimum**: Python 3.11
- **Reason**: Modern type hint syntax (e.g., `list[str]`, `dict[str, int]`)

## Testing Strategy

### Unit Tests

Located in `tests/` directory, using pytest:

```bash
uv run pytest tests/ -v
```

Test files:
- `test_parser.py`: Layer parsing and extraction
- `test_key_code_map.py`: Key code translation
- `test_layer_processor.py`: Layer data processing
- `test_pdf_renderer.py`: PDF rendering operations
- `test_data_models.py`: Data structure validation

### Manual Testing

1. **Valid input**: Test with known good `custom_config.h`
   ```bash
   uv run python -m zmk_to_pdf ../miryoku/custom_config.h output.pdf
   ```

2. **Missing layers**: Remove optional layers, verify graceful handling

3. **Invalid syntax**: Test error messages for malformed input

4. **Edge cases**: Unusual key combinations, long layer names

5. **Visual inspection**: Open generated PDF and verify:
   - Correct color assignments
   - Yellow highlighting only on access keys
   - Proper layer grouping and page layout

### Regression Testing

When making changes:

1. Generate PDF with current version
2. Make changes
3. Generate PDF again
4. Compare outputs visually or with PDF diff tools

### Type Checking

Always run mypy before committing:

```bash
uv run mypy src/
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
   uv run python -m zmk_to_pdf /path/to/custom_config.h output.pdf
   ```

### Using from Build Scripts

Example justfile recipe:

```justfile
pdf:
    cd zmk_to_pdf && uv run python -m zmk_to_pdf ../miryoku/custom_config.h ../layout.pdf
```

Example Makefile:

```makefile
layout.pdf: miryoku/custom_config.h
    cd zmk_to_pdf && uv run python -m zmk_to_pdf ../$< ../$@
```

## Recent Changes and Important Notes

### Color Scheme Refinement (Recent)

The color scheme was updated to provide clearer visual distinction:

**Before**: System keys (BSPC, RET, DEL) and access keys both used yellow (#F0E68C)

**After**: 
- Access keys: Yellow (#F0E68C) - thumb key to enter the layer
- System keys: Light blue (#ADD8E6) - functional system keys

This prevents confusion where you couldn't tell which thumb key was the access key in layers like NAV.

### Access Text Format (Recent)

Access text is now position-based (not key-based) to be layout-agnostic:

**Before**: "Hold SPACE (left outer)" - SPACE could change if user customizes BASE

**After**: "Access: left outer" - position never changes

This ensures consistency even when users customize their BASE layer configuration.

### Modular Structure (Recent)

The tool was refactored from a single monolithic file into organized modules:

- Easier to test individual components
- Clearer separation of concerns
- Better type safety with TypedDict structures
- Improved maintainability

## Known Limitations

1. **Fixed layout assumption**: Assumes 40-key Miryoku layout
2. **No validation**: Doesn't validate ZMK syntax, just parses patterns
3. **English only**: Labels and messages are in English
4. **Single file output**: Generates one PDF file, not multiple formats
5. **YAML key maps**: Requires key_code_map.yaml to be present (not editable via CLI)

## Future Enhancements

Potential improvements (not currently implemented):

- Support for non-Miryoku layouts (configurable key counts)
- SVG output in addition to PDF
- Interactive HTML output
- Configuration file for colors and layout
- CLI options for customizing colors
- Layered PDF annotations with layer-specific links

## Getting Help

When working on this project:

1. **Read the code**: Modular structure with clear separation of concerns
2. **Check README.md**: User-facing documentation
3. **Check AGENTS.md**: This file, with development guidance
4. **Run type checker**: `uv run mypy src/` catches many issues
5. **Run tests**: `uv run pytest tests/ -v` validates functionality
6. **Test incrementally**: Make small changes and test often

## Best Practices

### When Adding Features

1. Maintain modular structure (separate concerns)
2. Add type hints for all new functions
3. Update docstrings with examples
4. Add new key codes to `key_code_map.yaml`
5. Add corresponding tests
6. Update README.md with new capabilities
7. Run `mypy` and `ruff` before committing

### When Fixing Bugs

1. Write a test that reproduces the bug
2. Identify root cause (not symptoms)
3. Fix the root cause
4. Ensure test passes
5. Run full test suite
6. Remove debug output before committing

### When Refactoring

1. Keep the command-line interface stable
2. Maintain backward compatibility with config files
3. Run type checker after changes
4. Run full test suite
5. Verify PDF output looks correct
6. Update documentation if behavior changes

## Code Review Checklist

Before considering changes complete:

- [ ] Type hints added to all new functions
- [ ] Docstrings added to all public functions
- [ ] Error messages are clear and actionable
- [ ] Code follows snake_case naming
- [ ] `mypy src/` passes with no errors
- [ ] `ruff format src/` applied to code
- [ ] `ruff check src/` passes with no errors
- [ ] `pytest tests/` passes with all tests
- [ ] Manual test with real config file succeeds
- [ ] Color logic verified (access vs system keys)
- [ ] README.md updated if user-facing changes
- [ ] AGENTS.md updated if development process changes
