# Layout PDF Generation Requirements

## Overview

Generate a keyboard layout visualization PDF (`layout.pdf`) that displays all Miryoku keyboard layers in a clear, printable reference format.

## File Organization

- **Output**: `layout.pdf` in repository root
- **Script**: `scripts/generate_layout_pdf.py`
- **Build target**: `just pdf`

## Layout Structure

### Page Organization

- **Portrait orientation** (Letter size)
- **3 layers per page** (3 pages total for 8 layers)
- **Page 1**: TAP, NUM, SYM
- **Page 2**: NAV, BUTTON, MOUSE
- **Page 3**: MEDIA, FUN
- **Base layer**: Excluded (not displayed)

### Layer Display Format

Each layer section contains:

1. **Layer name** (bold 16pt heading, left-aligned above left hand keyboard)
2. **Description** (9pt, next to layer name, constrained to left hand width)
3. **Access instructions** (8pt bold blue text, right-aligned above right hand keyboard)
4. **Keyboard layout visualization** (both hands with thumb keys)

### Keyboard Layout Visualization

#### Structure per Hand

- **3 rows of 5 finger keys** (columns 0-4)
- **1 row of 2 physical thumb keys** (positioned below finger keys, aligned to interior)
- **1 combined thumb key** (positioned below physical thumbs, centered between them)
- **Horizontal spacing**: 0.40 inch gap between left and right hands
- **Vertical spacing**: 0.03 inch gap between key rows

#### Key Dimensions

- **Key width**: 0.60 inch
- **Key height**: 0.34 inch
- **Key spacing**: 0.03 inch

#### Thumb Keys

All 6 thumb keys are always shown for positional awareness. Inactive keys are grayed out.

##### Physical Thumb Keys (2 per hand)

- **Left hand**: SPACE, TAB - aligned to interior (columns 3-4)
- **Right hand**: BSPC, DEL - aligned to interior (columns 0-1)
- **Active state**: Highlighted with normal colors when the key accesses the current layer
- **Inactive state**: Light grey background (#E8E8E8) with grey text (#AAAAAA)

##### Combined Thumb Keys (1 per hand - virtual keys)

- **Left hand**: ESC (SPACE+TAB pressed together) - centered below physical thumbs
- **Right hand**: RET (BSPC+DEL pressed together) - centered below physical thumbs
- **Visual indicator**: Red dashed border (#FF0000, 2px dash pattern)
- **Active/Inactive**: Same highlighting rules as physical thumbs

##### Thumb Key Active States

The `active` field in layer data can be:
- `None`: No thumb key active on this hand
- `0`: First physical thumb key active (SPACE or BSPC)
- `1`: Second physical thumb key active (TAB or DEL)
- `"combined"`: Combined thumb key active (ESC or RET)
- `"all"`: All thumb keys active (used for TAP layer)

### Text Layout

#### Left Side (above left hand keyboard)

- **Layer name**: Bold 16pt Helvetica, positioned at left edge of keyboard
- **Description**: 9pt Helvetica grey (#666666), positioned next to title
- Text is truncated with "..." if it exceeds the left hand keyboard width

#### Right Side (above right hand keyboard)

- **Access info**: Bold 8pt Helvetica blue (#0066CC), right-aligned to right edge of keyboard
- Format: "Access: {access instructions}"
- Text is truncated with "..." if it exceeds the right hand keyboard width

**Important**: No text should appear in the gap between the left and right hand keyboards.

### Color Coding

#### Key Background Colors

- **Regular keys**: White (#FFFFFF)
- **Modifiers** (CTRL, ALT, SHIFT, GUI, LSHFT, RSHFT, LGUI, RGUI): Light pink (#FFB6C1)
- **Navigation** (arrows, layer transitions with arrows): Light green (#90EE90)
- **Mouse/Clipboard** (BTN1-3, RDO, UND, PST, CPY, CUT): Sky blue (#87CEEB)
- **System keys** (BSPC, RET, DEL, ESC, SPC, TAB, SPACE): Khaki (#F0E68C)
- **Layer access** (BOOT): Plum (#DDA0DD)
- **Empty/unused keys** ("-"): Light grey (#CCCCCC)
- **Inactive keys**: Very light grey (#E8E8E8)

#### Text Colors

- **Key text**: Black (default)
- **Empty key text**: Grey (#999999)
- **Inactive key text**: Grey (#AAAAAA)
- **Layer name**: Black (Helvetica Bold 16pt)
- **Description**: Grey (#666666, Helvetica 9pt)
- **Access info**: Blue (#0066CC, Helvetica Bold 8pt)
- **Page number**: Black (Helvetica 9pt, top right)
- **Legend**: Black (Helvetica 8pt)

### Legend and Header

#### Page Header

- **Title**: "Miryoku Keyboard Layers" (14pt bold, top left)
- **Legend**: "Legend: Red dashed border = Combined thumb key (SPACE+TAB on left, BSPC+DEL on right)" (8pt, below title)
- **Page number**: "Page X/Y" format (9pt, top right corner)

## Layer Data Structure

### Python Data Format

```python
layers = {
    "LAYER_NAME": {
        "description": "Brief description of layer purpose",
        "access": "How to access this layer (e.g., 'Hold SPACE (left hand)')",
        "left_hand": [
            ["Q", "W", "E", "R", "T"],  # Top row
            ["A", "S", "D", "F", "G"],  # Home row
            ["Z", "X", "C", "V", "B"],  # Bottom row
        ],
        "right_hand": [
            ["Y", "U", "I", "O", "P"],  # Top row
            ["H", "J", "K", "L", "'"],  # Home row
            ["N", "M", ",", ".", "/"],  # Bottom row
        ],
        "left_thumbs": {
            "physical": ["SPACE", "TAB"],  # Two physical thumb keys
            "combined": "ESC",              # Combined key (both pressed)
            "active": 0,                    # Which key is active (None, 0, 1, "combined", "all")
        },
        "right_thumbs": {
            "physical": ["BSPC", "DEL"],
            "combined": "RET",
            "active": None,
        },
    },
}
```

### Mapping from custom_config.h

Example layer definition in custom_config.h:

```c
#define MIRYOKU_LAYER_TAP \
&kp Q,             &kp W,             &kp E,             &kp R,             &kp T,             \
&kp Y,             &kp U,             &kp I,             &kp O,             &kp P,             \
\
&kp A,             &kp S,             &kp D,             &kp F,             &kp G,             \
&kp H,             &kp J,             &kp K,             &kp L,             &kp SQT,           \
\
&kp Z,             &kp X,             &kp C,             &kp V,             &kp B,             \
&kp N,             &kp M,             &kp COMMA,         &kp DOT,           &kp SLASH,         \
\
U_NP,              U_NP,              &kp ESC,           &kp SPACE,         &kp TAB,         \
&kp BSPC,          &kp RET,           &kp DEL,           U_NP,              U_NP
```

Note: The script currently has layer data hardcoded. Future enhancement could parse custom_config.h directly.

## Implementation Requirements

### Technology

- **Language**: Python 3.11+
- **Library**: ReportLab for PDF generation
- **Dependency management**: `uv` for Python environment
- **Script format**: PEP 723 inline script metadata

### Script Header

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "reportlab",
# ]
# ///
```

### Build Command

```bash
just pdf
```

This command should:

1. Run `scripts/generate_layout_pdf.py` via `uv run`
2. Generate `layout.pdf` in the repository root
3. Print confirmation message

### Preview Generation (for debugging)

To generate PNG previews of the PDF pages:

```bash
uv run --with pymupdf python3 -c "
import fitz
doc = fitz.open('layout.pdf')
for i, page in enumerate(doc):
    pix = page.get_pixmap(dpi=150)
    pix.save(f'layout_page{i+1}.png')
"
```

### Error Handling

- Script should validate layer definitions before rendering
- Exit gracefully if invalid data is encountered
- Print clear error messages for debugging

## Visual Requirements

### Alignment

- All layouts centered horizontally on page
- Consistent spacing between all layers (3.0 inch section height)
- Layer sections start at y_start = page_height - 0.85 inch

### Readability

- Keys must be clearly distinguished from each other
- Text must not overlap with keys or appear in the gap between hands
- Sufficient contrast between background and text
- Combined keys visually distinct from physical keys (red dashed border)
- Long text automatically truncated with "..."

### Printability

- Layout must remain clear when printed (B&W or color)
- All text readable at 100% zoom
- Proper margins and spacing for printing

## Included Layers

1. **TAP** - Tap layer (no hold modifiers) - All thumbs active
2. **NUM** - Numbers & basic symbols - SPACE active
3. **SYM** - Symbols & special characters - BSPC active
4. **NAV** - Navigation & arrow keys - TAB active
5. **BUTTON** - Mouse buttons & clipboard - RET (combined) active
6. **MOUSE** - Mouse movement & wheel - DEL active
7. **MEDIA** - RGB, audio, bluetooth - DEL active
8. **FUN** - Function keys F1-F12 - ESC (combined) active

## Excluded Elements

- **BASE layer**: Not displayed (covered by TAP layer for reference)
- **EXT layer**: Not displayed

## Files Modified/Created

- **Script**: `scripts/generate_layout_pdf.py`
- **Output**: `layout.pdf` (generated)
- **Spec**: `spec/layout_pdf_requirements.md` (this file)
- **Modified**: `justfile` (added `pdf` target)
