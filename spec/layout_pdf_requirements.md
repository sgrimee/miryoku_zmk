# Layout PDF Generation Requirements

## Overview

Generate a keyboard layout visualization PDF (`layout.pdf`) that displays all Miryoku keyboard layers in a clear, printable reference format. All layer data is dynamically parsed from `miryoku/custom_config.h` to ensure the PDF always reflects the current configuration.

## File Organization

- **Output**: `layout.pdf` in repository root
- **Script**: `scripts/generate_layout_pdf.py`
- **Source**: `miryoku/custom_config.h` (parsed for layer definitions)
- **Build target**: `just pdf`

## Layout Structure

### Page Organization

- **Portrait orientation** (Letter size)
- **2 pages total for 7 layers**
- **Page 1**: TAP, NUM, SYM, NAV (4 layers, tighter spacing)
- **Page 2**: BUTTON, MEDIA, FUN (3 layers)
- **Excluded layers**: BASE (covered by TAP), EXTRA (not used), MOUSE (removed)

### Layer Display Format

Each layer section contains:

1. **Layer name** (bold 16pt heading, left-aligned above left hand keyboard)
2. **Access instructions** (8pt bold blue text, right-aligned above right hand keyboard)
3. **Keyboard layout visualization** (both hands with thumb keys)

**Note**: Layer descriptions are NOT displayed (removed for cleaner layout).

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

From `custom_config.h` MIRYOKU_LAYER_TAP, thumb row (indices 30-39 of 40 total keys):

```
[30, 31] = U_NP (not present, skipped)
[32] = left_combined (ESC)
[33] = left_outer (SPACE)
[34] = left_inner (TAB)
[35] = right_inner (BSPC)
[36] = right_outer (RET)
[37] = right_combined (DEL)
[38, 39] = U_NP (not present, skipped)
```

**Layout in PDF:**
- **Left hand**: SPACE (outer), TAB (inner) - aligned to interior (columns 3-4)
- **Right hand**: BSPC (inner), RET (outer) - aligned to interior (columns 0-1)
- **Active state**: Highlighted with normal colors when the key accesses the current layer
- **Inactive state**: Light grey background (#E8E8E8) with grey text (#AAAAAA)

##### Combined Thumb Keys (1 per hand - virtual keys)

- **Left hand**: ESC (SPACE+TAB pressed together) - centered below physical thumbs
- **Right hand**: DEL (BSPC+RET pressed together) - centered below physical thumbs
- **Visual indicator**: Red dashed border (#FF0000, 2px dash pattern)
- **Active/Inactive**: Same highlighting rules as physical thumbs

##### Thumb Key Active States

The `active` field in layer data indicates which thumb key(s) access the current layer:

- `None`: No thumb key active on this hand
- `0`: First physical thumb key active (SPACE or BSPC)
- `1`: Second physical thumb key active (TAB or RET)
- `"combined"`: Combined thumb key active (ESC or DEL)
- `"all"`: All thumb keys active (used for TAP layer)

Active states are determined by parsing `MIRYOKU_LAYER_BASE` to find `U_LT(U_LAYERNAME, KEY)` patterns.

### Text Layout

#### Left Side (above left hand keyboard)

- **Layer name**: Bold 16pt Helvetica, positioned at left edge of keyboard
- No description text (removed)

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
- **Access info**: Blue (#0066CC, Helvetica Bold 8pt)
- **Page number**: Black (Helvetica 9pt, top right)
- **Legend**: Black (Helvetica 8pt)

### Legend and Header

#### Page Header

- **Title**: "Miryoku Keyboard Layers" (14pt bold, top left)
- **Legend**: Dynamically generated from parsed thumb keys (8pt, below title)
  - Format: `"Legend: Red dashed border = Combined thumb key ({left_outer}+{left_inner} on left, {right_inner}+{right_outer} on right)"`
  - Example: `"Legend: Red dashed border = Combined thumb key (SPACE+TAB on left, BSPC+RET on right)"`
- **Page number**: "Page X/Y" format (9pt, top right corner)

## Parsing from custom_config.h

### Layer Definition Format

Each layer is defined as a C preprocessor macro in `miryoku/custom_config.h`:

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

### Parsing Logic

1. **Read config file**: `miryoku/custom_config.h`
2. **Extract layer definitions**: Find `#define MIRYOKU_LAYER_{NAME} \` and join continuation lines
3. **Parse key codes**: Split by commas, strip whitespace, extract 40 keys per layer
4. **Translate key codes**: Convert ZMK codes to display labels using translation table
5. **Handle macros**: Extract tap key from `U_MT(MOD, KEY)` and `U_LT(LAYER, KEY)` patterns
6. **Skip U_NP**: Filter out "not present" thumb keys (indices 30-31, 38-39)

### Key Code Translation Table

The script maintains a comprehensive mapping from ZMK key codes to display labels:

```python
KEY_CODE_MAP = {
    # Basic letters (A-Z)
    "&kp Q": "Q", "&kp W": "W", "&kp E": "E", ...
    
    # Numbers
    "&kp N0": "0", "&kp N1": "1", ..., "&kp N9": "9",
    
    # Symbols with clear labels
    "&kp AMPS": "&", "&kp ASTRK": "*", "&kp AT": "@",
    "&kp BSLH": "\\", "&kp CARET": "^", "&kp COLON": ":",
    "&kp COMMA": ",", "&kp DLLR": "$", "&kp DOT": ".",
    "&kp EQUAL": "=", "&kp EXCL": "!", "&kp GRAVE": "`",
    "&kp HASH": "#", "&kp LBKT": "[", "&kp LBRC": "{",
    "&kp LPAR": "(", "&kp PRCNT": "%", "&kp PIPE": "|",
    "&kp PLUS": "+", "&kp RBKT": "]", "&kp RBRC": "}",
    "&kp RPAR": ")", "&kp SEMI": ";", "&kp SLASH": "/",
    "&kp SQT": "'", "&kp TILDE": "~", "&kp UNDER": "_",
    
    # Navigation (with Unicode arrows)
    "&kp LEFT": "←", "&kp DOWN": "↓", "&kp UP": "↑", "&kp RIGHT": "→",
    "&kp HOME": "HOME", "&kp END": "END",
    "&kp PG_DN": "PgDn", "&kp PG_UP": "PgUp",
    
    # System keys
    "&kp BSPC": "BSPC", "&kp DEL": "DEL", "&kp RET": "RET",
    "&kp ESC": "ESC", "&kp SPACE": "SPACE", "&kp TAB": "TAB",
    
    # Modifiers
    "&kp LCTRL": "LCTRL", "&kp RCTRL": "RCTRL",
    "&kp LALT": "LALT", "&kp RALT": "RALT",
    "&kp LGUI": "LGUI", "&kp RGUI": "RGUI",
    "&kp LSHFT": "LSHFT", "&kp RSHFT": "RSHFT",
    
    # Function keys
    "&kp F1": "F1", ..., "&kp F12": "F12",
    "&kp PSCRN": "PrSc", "&kp SLCK": "SlLk", "&kp PAUSE_BREAK": "Pause",
    
    # Layer transitions (with arrow prefix)
    "&u_to_U_BASE": "→BASE", "&u_to_U_EXTRA": "→EXT", "&u_to_U_TAP": "→TAP",
    "&u_to_U_NAV": "→NAV", "&u_to_U_NUM": "→NUM", "&u_to_U_SYM": "→SYM",
    "&u_to_U_FUN": "→FUN", "&u_to_U_MEDIA": "→MEDIA", "&u_to_U_MOUSE": "→MOUSE",
    
    # Special macros
    "U_NA": "-",          # Not available (displayed as dash)
    "U_NP": None,         # Not present (filtered out, not displayed)
    "U_BOOT": "BOOT",
    
    # Clipboard operations
    "U_CPY": "CPY", "U_PST": "PST", "U_CUT": "CUT",
    "U_UND": "UND", "U_RDO": "RDO",
    
    # Mouse buttons
    "U_BTN1": "BTN1", "U_BTN2": "BTN2", "U_BTN3": "BTN3",
    
    # Mouse movement (with Unicode arrows)
    "U_MS_L": "M←", "U_MS_R": "M→", "U_MS_U": "M↑", "U_MS_D": "M↓",
    "U_WH_L": "WH←", "U_WH_R": "WH→", "U_WH_U": "WH↑", "U_WH_D": "WH↓",
    
    # RGB/Media controls
    "U_RGB_TOG": "RGB_T", "U_RGB_EFF": "RGB_E",
    "U_RGB_HUI": "RGB_H+", "U_RGB_SAI": "RGB_S+", "U_RGB_BRI": "RGB_B+",
    "U_EP_TOG": "EP_TOG",
    "&kp C_VOL_UP": "VOL+", "&kp C_VOL_DN": "VOL-",
    "&kp C_NEXT": "NEXT", "&kp C_PREV": "PREV",
    "&kp C_PP": "PP", "&kp C_STOP": "STOP", "&kp C_MUTE": "MUTE",
    
    # Bluetooth
    "&u_bt_sel_0": "BT0", "&u_bt_sel_1": "BT1",
    "&u_bt_sel_2": "BT2", "&u_bt_sel_3": "BT3",
    "&u_out_tog": "OUT_T",
}
```

**Fallback behavior**: If a key code is not found in the translation table, the raw key code is displayed (allowing unknown codes to be visible for debugging).

### Handling Mod-Tap and Layer-Tap Macros

ZMK uses special macros for hold-tap behaviors:

- **`U_MT(MOD, KEY)`**: Mod-tap - tap produces KEY, hold produces MOD
  - Display: Extract and show KEY (the tap behavior)
  - Example: `U_MT(LCTRL, A)` → display "A"

- **`U_LT(LAYER, KEY)`**: Layer-tap - tap produces KEY, hold activates LAYER
  - Display: Extract and show KEY (the tap behavior)
  - Example: `U_LT(U_NAV, TAB)` → display "TAB"

### Access Text Generation

Access text is generated by parsing `MIRYOKU_LAYER_BASE` to find how each layer is accessed:

**Examples of generated access text:**

| Layer | Access Pattern in BASE | Generated Access Text |
|-------|------------------------|----------------------|
| TAP | `&u_to_U_TAP` in other layers | "→TAP from other layers" |
| NUM | `U_LT(U_NUM, SPACE)` at index 33 | "Hold SPACE (left outer thumb)" |
| SYM | `U_LT(U_SYM, BSPC)` at index 35 | "Hold BSPC (right inner thumb)" |
| NAV | `U_LT(U_NAV, TAB)` at index 34 | "Hold TAB (left inner thumb)" |
| BUTTON | `U_LT(U_BUTTON, Z)` at index 20<br>`U_LT(U_BUTTON, SLASH)` at index 29<br>`U_LT(U_BUTTON, RET)` at index 36 | "Hold Z / SLASH / RET" |
| MEDIA | `U_LT(U_MEDIA, DEL)` at index 37 | "Hold DEL (right combined thumb)" |
| FUN | `U_LT(U_FUN, ESC)` at index 32 | "Hold ESC (left combined thumb)" |

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
2. Parse `miryoku/custom_config.h`
3. Generate `layout.pdf` in the repository root
4. Print confirmation message

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

The script MUST fail with clear, actionable error messages if:

- Config file cannot be read
- Layer definition is missing or malformed
- Layer has wrong number of keys (expected: 40)
- Parsing fails for any reason

**Error message format:**
```
ERROR: Could not find MIRYOKU_LAYER_NAV in miryoku/custom_config.h
ERROR: MIRYOKU_LAYER_TAP has 38 keys, expected 40
ERROR: Failed to parse MIRYOKU_LAYER_SYM: Invalid macro syntax at line 93
```

Exit with `sys.exit(1)` on any error (do not generate partial/incorrect PDF).

## Visual Requirements

### Alignment

- All layouts centered horizontally on page
- Consistent spacing between layers
  - **Page 1** (4 layers): ~2.25 inch section height (tighter)
  - **Page 2** (3 layers): ~3.0 inch section height (standard)
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

## Displayed Layers

The following 7 layers are included in the PDF (in display order):

1. **TAP** - Tap layer (no hold modifiers)
2. **NUM** - Numbers & basic symbols
3. **SYM** - Symbols & special characters
4. **NAV** - Navigation & arrow keys
5. **BUTTON** - Mouse buttons & clipboard operations
6. **MEDIA** - RGB, audio, bluetooth controls
7. **FUN** - Function keys F1-F12

## Excluded Layers

- **BASE**: Not displayed (covered by TAP layer for reference)
- **EXTRA**: Not displayed (alternative layout, not commonly used)
- **MOUSE**: Removed from both config and PDF

## Files Modified/Created

- **Script**: `scripts/generate_layout_pdf.py` (completely rewritten)
- **Output**: `layout.pdf` (generated, dynamically from config)
- **Spec**: `spec/layout_pdf_requirements.md` (this file, updated)
- **Config**: `miryoku/custom_config.h` (MOUSE layer removed)
- **Modified**: `justfile` (already has `pdf` target)
