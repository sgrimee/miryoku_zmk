#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "reportlab",
# ]
# ///

import re
import sys
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, black

# === KEY CODE TRANSLATION TABLE ===
KEY_CODE_MAP = {
    # Basic letters A-Z
    "&kp A": "A",
    "&kp B": "B",
    "&kp C": "C",
    "&kp D": "D",
    "&kp E": "E",
    "&kp F": "F",
    "&kp G": "G",
    "&kp H": "H",
    "&kp I": "I",
    "&kp J": "J",
    "&kp K": "K",
    "&kp L": "L",
    "&kp M": "M",
    "&kp N": "N",
    "&kp O": "O",
    "&kp P": "P",
    "&kp Q": "Q",
    "&kp R": "R",
    "&kp S": "S",
    "&kp T": "T",
    "&kp U": "U",
    "&kp V": "V",
    "&kp W": "W",
    "&kp X": "X",
    "&kp Y": "Y",
    "&kp Z": "Z",
    # Numbers
    "&kp N0": "0",
    "&kp N1": "1",
    "&kp N2": "2",
    "&kp N3": "3",
    "&kp N4": "4",
    "&kp N5": "5",
    "&kp N6": "6",
    "&kp N7": "7",
    "&kp N8": "8",
    "&kp N9": "9",
    # Symbols
    "&kp AMPS": "&",
    "&kp ASTRK": "*",
    "&kp AT": "@",
    "&kp BSLH": "\\",
    "&kp CARET": "^",
    "&kp COLON": ":",
    "&kp COMMA": ",",
    "&kp DLLR": "$",
    "&kp DOT": ".",
    "&kp EQUAL": "=",
    "&kp EXCL": "!",
    "&kp GRAVE": "`",
    "&kp HASH": "#",
    "&kp LBKT": "[",
    "&kp LBRC": "{",
    "&kp LPAR": "(",
    "&kp MINUS": "-",
    "&kp PRCNT": "%",
    "&kp PIPE": "|",
    "&kp PLUS": "+",
    "&kp RBKT": "]",
    "&kp RBRC": "}",
    "&kp RPAR": ")",
    "&kp SEMI": ";",
    "&kp SLASH": "/",
    "&kp SQT": "'",
    "&kp TILDE": "~",
    "&kp UNDER": "_",
    # Navigation (with Unicode arrows)
    "&kp LEFT": "←",
    "&kp DOWN": "↓",
    "&kp UP": "↑",
    "&kp RIGHT": "→",
    "&kp HOME": "HOME",
    "&kp END": "END",
    "&kp PG_DN": "PgDn",
    "&kp PG_UP": "PgUp",
    # System keys
    "&kp BSPC": "BSPC",
    "&kp DEL": "DEL",
    "&kp RET": "RET",
    "&kp ESC": "ESC",
    "&kp SPACE": "SPACE",
    "&kp TAB": "TAB",
    # Modifiers
    "&kp LCTRL": "LCTRL",
    "&kp RCTRL": "RCTRL",
    "&kp LALT": "LALT",
    "&kp RALT": "RALT",
    "&kp LGUI": "LGUI",
    "&kp RGUI": "RGUI",
    "&kp LSHFT": "LSHFT",
    "&kp RSHFT": "RSHFT",
    # Function keys
    "&kp F1": "F1",
    "&kp F2": "F2",
    "&kp F3": "F3",
    "&kp F4": "F4",
    "&kp F5": "F5",
    "&kp F6": "F6",
    "&kp F7": "F7",
    "&kp F8": "F8",
    "&kp F9": "F9",
    "&kp F10": "F10",
    "&kp F11": "F11",
    "&kp F12": "F12",
    "&kp PSCRN": "PrSc",
    "&kp SLCK": "SlLk",
    "&kp PAUSE_BREAK": "Pause",
    # Layer transitions (with arrow prefix)
    "&u_to_U_BASE": "→BASE",
    "&u_to_U_EXTRA": "→EXT",
    "&u_to_U_TAP": "→TAP",
    "&u_to_U_NAV": "→NAV",
    "&u_to_U_NUM": "→NUM",
    "&u_to_U_SYM": "→SYM",
    "&u_to_U_FUN": "→FUN",
    "&u_to_U_MEDIA": "→MEDIA",
    "&u_to_U_MOUSE": "→MOUSE",
    # Special macros
    "U_NA": "-",  # Not available
    "U_NP": None,  # Not present (will be filtered out)
    "U_BOOT": "BOOT",
    # Clipboard operations
    "U_CPY": "CPY",
    "U_PST": "PST",
    "U_CUT": "CUT",
    "U_UND": "UND",
    "U_RDO": "RDO",
    # Mouse buttons
    "U_BTN1": "BTN1",
    "U_BTN2": "BTN2",
    "U_BTN3": "BTN3",
    # Mouse movement (with Unicode arrows)
    "U_MS_L": "M←",
    "U_MS_R": "M→",
    "U_MS_U": "M↑",
    "U_MS_D": "M↓",
    "U_WH_L": "WH←",
    "U_WH_R": "WH→",
    "U_WH_U": "WH↑",
    "U_WH_D": "WH↓",
    # RGB/Media controls
    "U_RGB_TOG": "RGB_T",
    "U_RGB_EFF": "RGB_E",
    "U_RGB_HUI": "RGB_H+",
    "U_RGB_SAI": "RGB_S+",
    "U_RGB_BRI": "RGB_B+",
    "U_EP_TOG": "EP_TOG",
    "&kp C_VOL_UP": "VOL+",
    "&kp C_VOL_DN": "VOL-",
    "&kp C_NEXT": "NEXT",
    "&kp C_PREV": "PREV",
    "&kp C_PP": "PP",
    "&kp C_STOP": "STOP",
    "&kp C_MUTE": "MUTE",
    # Bluetooth
    "&u_bt_sel_0": "BT0",
    "&u_bt_sel_1": "BT1",
    "&u_bt_sel_2": "BT2",
    "&u_bt_sel_3": "BT3",
    "&u_out_tog": "OUT_T",
}


# === PARSING FUNCTIONS ===


def parse_config_file(config_path: Path) -> str:
    """Read config file and return content."""
    try:
        return config_path.read_text()
    except Exception as e:
        sys.exit(f"ERROR: Could not read {config_path}: {e}")


def extract_layer_definition(content: str, layer_name: str) -> str | None:
    """Extract the key definition for MIRYOKU_LAYER_{layer_name}.

    Returns the full definition with line continuations joined, or None if not found.
    """
    # Match #define MIRYOKU_LAYER_{NAME} \ ... up to next non-continuation line
    # Look for lines starting with #define, then capture all continuation lines
    pattern = rf"#define\s+MIRYOKU_LAYER_{layer_name}\s+(.+?)(?=\n#define|\n\n|\Z)"
    match = re.search(pattern, content, re.DOTALL | re.MULTILINE)

    if not match:
        return None

    # Get the definition text
    definition = match.group(1)

    # Join line continuations (remove backslashes and newlines)
    definition = re.sub(r"\\\s*\n\s*", " ", definition)
    # Remove extra whitespace
    definition = re.sub(r"\s+", " ", definition)

    return definition.strip()


def translate_key_code(code: str) -> str | None:
    """Translate ZMK key code to display label.

    Handles:
    - Direct lookup in KEY_CODE_MAP
    - U_MT(MOD, KEY) macros -> extract KEY
    - U_LT(LAYER, KEY) macros -> extract KEY
    - U_NP -> None (filtered out)
    - Unknown codes -> return raw code for debugging
    """
    code = code.strip()

    # Handle U_NP specially (filtered out)
    if code == "U_NP":
        return None

    # Direct lookup
    if code in KEY_CODE_MAP:
        result = KEY_CODE_MAP[code]
        return result  # May be None for U_NP

    # Handle U_MT(MOD, KEY) - extract KEY (tap behavior)
    mt_match = re.match(r"U_MT\s*\(\s*([^,]+)\s*,\s*([^)]+)\s*\)", code)
    if mt_match:
        key = mt_match.group(2).strip()
        # Recursively translate the extracted key
        return (
            translate_key_code(key)
            if not key.startswith("&kp")
            else translate_key_code(f"&kp {key}")
        )

    # Handle U_LT(LAYER, KEY) - extract KEY (tap behavior)
    lt_match = re.match(r"U_LT\s*\(\s*([^,]+)\s*,\s*([^)]+)\s*\)", code)
    if lt_match:
        key = lt_match.group(2).strip()
        # Recursively translate the extracted key
        return (
            translate_key_code(key)
            if not key.startswith("&kp")
            else translate_key_code(f"&kp {key}")
        )

    # Fallback: return the raw code (for debugging unknown codes)
    return code


def parse_layer_keys(definition: str) -> list[str | None]:
    """Parse a layer definition into list of 40 key codes.

    Returns list of translated key labels (U_NP filtered out as None).
    """
    # Split by comma
    keys_raw = [k.strip() for k in definition.split(",")]

    # Translate each key
    keys = [translate_key_code(k) for k in keys_raw if k]

    return keys


def extract_thumb_keys(tap_keys: list[str | None]) -> dict:
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

    Returns:
    {
        "left": {"physical": [outer, inner], "combined": combined},
        "right": {"physical": [inner, outer], "combined": combined},
    }
    """
    if len(tap_keys) < 38:
        sys.exit(f"ERROR: TAP layer has {len(tap_keys)} keys, expected at least 38")

    # Extract thumb keys (indices 32-37)
    left_combined = tap_keys[32]
    left_outer = tap_keys[33]
    left_inner = tap_keys[34]
    right_inner = tap_keys[35]
    right_outer = tap_keys[36]
    right_combined = tap_keys[37]

    return {
        "left": {
            "physical": [left_outer, left_inner],
            "combined": left_combined,
        },
        "right": {
            "physical": [right_inner, right_outer],
            "combined": right_combined,
        },
    }


def parse_layer_access_from_base(base_definition: str) -> dict:
    """Parse BASE layer to determine which key accesses which layer.

    Looks for U_LT(U_LAYERNAME, KEY) patterns.

    Returns dict like:
    {
        "NAV": [{"position": "left_inner", "key": "TAB", "index": 34}],
        "BUTTON": [
            {"position": "left_bottom_0", "key": "Z", "index": 20},
            {"position": "right_bottom_4", "key": "SLASH", "index": 29},
            {"position": "right_outer", "key": "RET", "index": 36}
        ],
        ...
    }
    """
    # First, properly parse all keys to get correct indices
    # Split by comma, but need to handle nested commas in macros
    keys_raw = []
    current_key = ""
    paren_depth = 0

    for char in base_definition:
        if char == "(":
            paren_depth += 1
            current_key += char
        elif char == ")":
            paren_depth -= 1
            current_key += char
        elif char == "," and paren_depth == 0:
            # Top-level comma - end of key
            if current_key.strip():
                keys_raw.append(current_key.strip())
            current_key = ""
        else:
            current_key += char

    # Don't forget the last key
    if current_key.strip():
        keys_raw.append(current_key.strip())

    # Now search for U_LT patterns in each key
    lt_pattern = r"U_LT\s*\(\s*U_(\w+)\s*,\s*([^)]+)\s*\)"
    access_map = {}

    for idx, key_code in enumerate(keys_raw):
        match = re.match(lt_pattern, key_code)
        if match:
            layer_name = match.group(1)
            key_name = match.group(2).strip()

            # Translate the key name
            if key_name.startswith("&kp"):
                translated_key = translate_key_code(key_name)
            else:
                translated_key = translate_key_code(f"&kp {key_name}")

            # Determine position name
            position = determine_position_name(idx)

            # Add to access map
            if layer_name not in access_map:
                access_map[layer_name] = []

            access_map[layer_name].append(
                {"position": position, "key": translated_key or key_name, "index": idx}
            )

    return access_map


def determine_position_name(index: int) -> str:
    """Determine the position name for a key index (0-39)."""
    # Thumb row (indices 30-39)
    if 30 <= index <= 39:
        thumb_positions = {
            32: "left_combined",
            33: "left_outer",
            34: "left_inner",
            35: "right_inner",
            36: "right_outer",
            37: "right_combined",
        }
        return thumb_positions.get(index, f"thumb_{index}")

    # Finger keys (indices 0-29)
    row = index // 10
    col = index % 10
    hand = "left" if col < 5 else "right"
    local_col = col if col < 5 else col - 5

    return f"{hand}_row{row}_col{local_col}"


def generate_access_text(layer_name: str, layer_access: dict, thumb_keys: dict) -> str:
    """Generate access text for a layer based on how it's accessed from BASE.

    Examples:
    - NAV: "Hold TAB (left inner thumb)"
    - FUN: "Hold ESC (left combined thumb)"
    - BUTTON: "Hold Z / SLASH / RET"
    - TAP: "→TAP from other layers"
    """
    if layer_name == "TAP":
        return "→TAP from other layers"

    if layer_name not in layer_access:
        return f"Access unknown"

    access_info = layer_access[layer_name]

    if len(access_info) == 1:
        # Single access key
        info = access_info[0]
        position = info["position"]
        key = info["key"]

        # Add position description for thumb keys
        if "thumb" in position or position in [
            "left_combined",
            "left_outer",
            "left_inner",
            "right_combined",
            "right_inner",
            "right_outer",
        ]:
            pos_desc = position.replace("_", " ")
            return f"Hold {key} ({pos_desc})"
        else:
            return f"Hold {key}"
    else:
        # Multiple access keys - list them with better formatting
        keys = [info["key"] for info in access_info]
        # Replace slash symbol with word to avoid confusion
        keys = ["SLASH" if k == "/" else k for k in keys]
        return "Hold " + " / ".join(keys)


def determine_active_thumb(layer_name: str, layer_access: dict):
    """Determine which thumb keys are active for accessing this layer.

    Returns:
    {
        "left": None | 0 | 1 | "combined" | "all",
        "right": None | 0 | 1 | "combined" | "all",
    }
    """
    if layer_name == "TAP":
        return {"left": "all", "right": "all"}

    if layer_name not in layer_access:
        return {"left": None, "right": None}

    active: dict = {"left": None, "right": None}

    for info in layer_access[layer_name]:
        position = info["position"]

        if position == "left_combined":
            active["left"] = "combined"
        elif position == "left_outer":
            active["left"] = 0
        elif position == "left_inner":
            active["left"] = 1
        elif position == "right_combined":
            active["right"] = "combined"
        elif position == "right_inner":
            active["right"] = 0
        elif position == "right_outer":
            active["right"] = 1

    return active


def discover_layers(content: str) -> list[str]:
    """Discover all MIRYOKU_LAYER_* definitions in the config file.

    Returns layer names in the order they appear in the config file.
    Excludes BASE and EXTRA (not displayed in PDF).

    Returns:
        List of layer names found in config (e.g., ["TAP", "NUM", "SYM", ...])
    """
    pattern = r"#define\s+MIRYOKU_LAYER_([A-Z_]+)\s"
    matches = re.findall(pattern, content)

    # Filter out BASE and EXTRA (these are not displayed)
    excluded = {"BASE", "EXTRA"}
    layers = [m for m in matches if m not in excluded]

    return layers


def create_page_groupings(layers: list[str]) -> list[list[str]]:
    """Group layers into pages dynamically.

    - First page gets up to 4 layers, preferring TAP, NUM, SYM, NAV if present
    - Subsequent pages get up to 4 layers each
    - Remaining layers fill in order of appearance in config

    Args:
        layers: List of layer names to group

    Returns:
        List of pages, where each page is a list of layer names
        Example: [["TAP", "NUM", "SYM", "NAV"], ["BUTTON", "MEDIA", "FUN"]]
    """
    preferred_first = ["TAP", "NUM", "SYM", "NAV"]

    # Build first page: preferred layers first (if they exist), in preferred order
    page1 = [l for l in preferred_first if l in layers]

    # Fill remaining page1 slots with other layers (up to 4 total)
    remaining = [l for l in layers if l not in page1]
    while len(page1) < 4 and remaining:
        page1.append(remaining.pop(0))

    # Build subsequent pages with remaining layers (4 per page)
    pages = [page1] if page1 else []
    while remaining:
        page = remaining[:4]
        remaining = remaining[4:]
        pages.append(page)

    return pages


def build_layer_data(
    layer_name: str, keys: list[str | None], thumb_keys: dict, layer_access: dict
) -> dict:
    """Build the layer data structure for rendering.

    Args:
        layer_name: Name of the layer (e.g., "TAP", "NAV")
        keys: List of 40 translated key labels (with U_NP as None)
        thumb_keys: Thumb key structure from extract_thumb_keys()
        layer_access: Access map from parse_layer_access_from_base()

    Returns:
        Dictionary with left_hand, right_hand, left_thumbs, right_thumbs, access
    """
    # Split into rows (3 rows of 10 keys each for finger keys)
    # Row 0: keys[0:10] -> left[0:5], right[5:10]
    # Row 1: keys[10:20]
    # Row 2: keys[20:30]

    left_hand = [
        [keys[0], keys[1], keys[2], keys[3], keys[4]],  # Row 0 left
        [keys[10], keys[11], keys[12], keys[13], keys[14]],  # Row 1 left
        [keys[20], keys[21], keys[22], keys[23], keys[24]],  # Row 2 left
    ]

    right_hand = [
        [keys[5], keys[6], keys[7], keys[8], keys[9]],  # Row 0 right
        [keys[15], keys[16], keys[17], keys[18], keys[19]],  # Row 1 right
        [keys[25], keys[26], keys[27], keys[28], keys[29]],  # Row 2 right
    ]

    # Determine active thumbs
    active_thumbs = determine_active_thumb(layer_name, layer_access)

    # Generate access text
    access_text = generate_access_text(layer_name, layer_access, thumb_keys)

    return {
        "left_hand": left_hand,
        "right_hand": right_hand,
        "left_thumbs": {
            "physical": thumb_keys["left"]["physical"],
            "combined": thumb_keys["left"]["combined"],
            "active": active_thumbs["left"],
        },
        "right_thumbs": {
            "physical": thumb_keys["right"]["physical"],
            "combined": thumb_keys["right"]["combined"],
            "active": active_thumbs["right"],
        },
        "access": access_text,
    }


# === PDF RENDERING FUNCTIONS ===


def draw_key(
    pdf, x, y, width, height, text, font_size=7, is_combined=False, is_inactive=False
):
    """Draw a single key.

    Args:
        is_combined: True for combined thumb keys (red dashed border)
        is_inactive: True for grayed out keys (not relevant for current layer)
    """
    # Determine color based on key type
    if is_inactive:
        # Grayed out keys for positional awareness
        color = HexColor("#E8E8E8")  # Very light grey background
        text_color = HexColor("#AAAAAA")  # Grey text
    elif text == "-" or text == "" or text is None:
        color = HexColor("#CCCCCC")  # Light grey for empty
        text_color = HexColor("#999999")
        text = "-" if text is None else text
    elif "→" in text or "↑" in text or "↓" in text or "←" in text:
        color = HexColor("#90EE90")  # Light green for navigation
        text_color = black
    elif any(
        c in text for c in ["CTRL", "ALT", "SHIFT", "LGUI", "RGUI", "LSHFT", "RSHFT"]
    ):
        color = HexColor("#FFB6C1")  # Light pink for modifiers
        text_color = black
    elif text in ["BTN1", "BTN2", "BTN3", "RDO", "UND", "PST", "CPY", "CUT"]:
        color = HexColor("#87CEEB")  # Sky blue for mouse/clipboard
        text_color = black
    elif "BOOT" in text or "→" in text:
        color = HexColor("#DDA0DD")  # Plum for layer access
        text_color = black
    elif text in ["BSPC", "RET", "DEL", "ESC", "SPC", "TAB", "SPACE"]:
        color = HexColor("#F0E68C")  # Khaki for system keys
        text_color = black
    else:
        color = HexColor("#FFFFFF")  # White for regular keys
        text_color = black

    # Draw key background
    pdf.setFillColor(color)
    pdf.setStrokeColor(black if not is_inactive else HexColor("#CCCCCC"))
    pdf.setLineWidth(0.5)
    pdf.rect(x, y, width, height, fill=1)

    # Add red dashed border for combined thumb keys (active ones)
    if is_combined and not is_inactive:
        pdf.setLineWidth(1)
        pdf.setStrokeColor(HexColor("#FF0000"))
        pdf.setDash(2, 2)
        pdf.rect(x, y, width, height, fill=0)
        pdf.setDash()

    # Draw text
    pdf.setFont("Helvetica-Bold", font_size)
    pdf.setFillColor(text_color)

    # Center text
    text_width = pdf.stringWidth(text, "Helvetica-Bold", font_size)
    text_x = x + (width - text_width) / 2
    text_y = y + (height - font_size) / 2
    pdf.drawString(text_x, text_y, text)


def create_layer_section(pdf, layer_name, layer_data, y_offset, width):
    """Create a single layer section on a page"""
    # Key dimensions
    key_width = 0.60 * inch
    key_height = 0.34 * inch
    key_spacing = 0.03 * inch
    hand_gap = 0.40 * inch

    # Calculate positions
    left_hand = layer_data["left_hand"]
    right_hand = layer_data["right_hand"]

    # Total width needed for one hand (5 keys + 4 spacings)
    hand_width = 5 * key_width + 4 * key_spacing
    # Total width for both hands with proper gap
    total_width = 2 * hand_width + hand_gap

    # Center the keyboard layout horizontally on the page
    page_center = width / 2
    left_hand_x = page_center - total_width / 2
    right_hand_x = left_hand_x + hand_width + hand_gap

    # Reset fill color to black for text
    pdf.setFillColor(black)

    # Title above left hand keyboard
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(left_hand_x, y_offset, layer_name)

    # Access info above right hand keyboard (right-aligned)
    pdf.setFont("Helvetica-Bold", 8)
    pdf.setFillColor(HexColor("#0066CC"))
    access_text = f"Access: {layer_data['access']}"
    # Truncate access text if too long for right hand area
    max_access_width = hand_width - 0.1 * inch
    while (
        pdf.stringWidth(access_text, "Helvetica-Bold", 8) > max_access_width
        and len(access_text) > 15
    ):
        access_text = access_text[:-4] + "..."
    access_width = pdf.stringWidth(access_text, "Helvetica-Bold", 8)
    pdf.drawString(right_hand_x + hand_width - access_width, y_offset, access_text)
    pdf.setFillColor(black)

    # Content area y positions - start keys below the title (with adequate spacing)
    keys_start_y = y_offset - 0.45 * inch
    first_row_y = keys_start_y

    # Draw left hand regular keys (3 rows of 5 keys)
    for row_idx, row in enumerate(left_hand):
        y = first_row_y - (row_idx * (key_height + key_spacing))
        for col_idx, key in enumerate(row):
            x = left_hand_x + col_idx * (key_width + key_spacing)
            key_text = key if key is not None else "-"
            draw_key(pdf, x, y, key_width, key_height, key_text, font_size=9)

    # Calculate thumb row y positions (below finger keys)
    physical_thumb_y = first_row_y - (3 * (key_height + key_spacing)) - 0.04 * inch
    combined_thumb_y = physical_thumb_y - (key_height + 0.04 * inch)

    # Draw left hand thumb keys
    left_thumbs = layer_data["left_thumbs"]
    left_active = left_thumbs.get("active")

    # Draw physical thumb keys (aligned to interior = columns 3-4)
    for idx, key in enumerate(left_thumbs["physical"]):
        col_offset = 3 + idx  # Columns 3 and 4
        x = left_hand_x + col_offset * (key_width + key_spacing)
        is_inactive = left_active != "all" and left_active != idx
        draw_key(
            pdf,
            x,
            physical_thumb_y,
            key_width,
            key_height,
            key,
            font_size=9,
            is_inactive=is_inactive,
        )

    # Draw combined thumb key (centered under physical thumbs)
    x = left_hand_x + 3 * (key_width + key_spacing) + (key_width + key_spacing) / 2
    is_inactive = left_active != "all" and left_active != "combined"
    draw_key(
        pdf,
        x,
        combined_thumb_y,
        key_width,
        key_height,
        left_thumbs["combined"],
        font_size=9,
        is_combined=True,
        is_inactive=is_inactive,
    )

    # Draw right hand regular keys (3 rows of 5 keys)
    for row_idx, row in enumerate(right_hand):
        y = first_row_y - (row_idx * (key_height + key_spacing))
        for col_idx, key in enumerate(row):
            x = right_hand_x + col_idx * (key_width + key_spacing)
            key_text = key if key is not None else "-"
            draw_key(pdf, x, y, key_width, key_height, key_text, font_size=9)

    # Draw right hand thumb keys
    right_thumbs = layer_data["right_thumbs"]
    right_active = right_thumbs.get("active")

    # Draw physical thumb keys (aligned to interior = columns 0-1)
    for idx, key in enumerate(right_thumbs["physical"]):
        col_offset = idx  # Columns 0 and 1
        x = right_hand_x + col_offset * (key_width + key_spacing)
        is_inactive = right_active != "all" and right_active != idx
        draw_key(
            pdf,
            x,
            physical_thumb_y,
            key_width,
            key_height,
            key,
            font_size=9,
            is_inactive=is_inactive,
        )

    # Draw combined thumb key (centered under physical thumbs)
    x = right_hand_x + (key_width + key_spacing) / 2
    is_inactive = right_active != "all" and right_active != "combined"
    draw_key(
        pdf,
        x,
        combined_thumb_y,
        key_width,
        key_height,
        right_thumbs["combined"],
        font_size=9,
        is_combined=True,
        is_inactive=is_inactive,
    )


# === MAIN LOGIC ===


def main():
    # Paths
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    config_path = repo_root / "miryoku" / "custom_config.h"
    pdf_path = repo_root / "layout.pdf"

    # Parse config file
    print(f"Reading config from {config_path}")
    content = parse_config_file(config_path)

    # Discover layers from config file
    layers_to_display = discover_layers(content)
    print(f"Discovered layers: {layers_to_display}")

    if not layers_to_display:
        sys.exit("ERROR: No layers found in config (excluding BASE and EXTRA)")

    # Parse BASE layer for access information
    print("Parsing BASE layer for access information...")
    base_def = extract_layer_definition(content, "BASE")
    if base_def is None:
        sys.exit("ERROR: Could not find MIRYOKU_LAYER_BASE in config")
    layer_access = parse_layer_access_from_base(base_def)

    # Parse TAP layer for thumb key labels (fall back to BASE if TAP doesn't exist)
    print("Parsing thumb key labels...")
    tap_def = extract_layer_definition(content, "TAP")
    if tap_def is None:
        print("  TAP layer not found, falling back to BASE layer for thumb keys")
        tap_def = base_def

    tap_keys = parse_layer_keys(tap_def)
    if len(tap_keys) < 38:
        sys.exit(
            f"ERROR: Layer for thumb keys has {len(tap_keys)} keys, expected at least 38"
        )
    thumb_keys = extract_thumb_keys(tap_keys)

    # Build layer data for each layer
    print("Building layer data...")
    layers = {}
    for layer_name in layers_to_display:
        print(f"  Processing layer: {layer_name}")
        layer_def = extract_layer_definition(content, layer_name)
        if layer_def is None:
            print(f"  WARNING: Skipping {layer_name} - definition not found")
            continue

        keys = parse_layer_keys(layer_def)
        if len(keys) < 30:  # At least 30 finger keys expected
            print(
                f"  WARNING: Skipping {layer_name} - has {len(keys)} keys, expected at least 30"
            )
            continue

        layers[layer_name] = build_layer_data(
            layer_name, keys, thumb_keys, layer_access
        )

    if not layers:
        sys.exit("ERROR: No valid layers found to display")

    # Generate PDF
    print(f"Generating PDF: {pdf_path}")
    pdf = canvas.Canvas(str(pdf_path), pagesize=letter)
    width, height = letter

    # Dynamically group layers into pages
    page_groupings = create_page_groupings(list(layers.keys()))
    print(f"Page groupings: {page_groupings}")

    total_pages = len(page_groupings)

    # Generate legend text dynamically
    left_outer, left_inner = thumb_keys["left"]["physical"]
    right_inner, right_outer = thumb_keys["right"]["physical"]
    legend = f"Legend: Red dashed border = Combined thumb key ({left_outer}+{left_inner} on left, {right_inner}+{right_outer} on right)"

    for page_num, page_layers in enumerate(page_groupings):
        # Title on page
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(0.5 * inch, height - 0.35 * inch, "Miryoku Keyboard Layers")

        # Legend for thumb keys
        pdf.setFont("Helvetica", 8)
        pdf.drawString(0.5 * inch, height - 0.55 * inch, legend)

        # Page number
        pdf.setFont("Helvetica", 9)
        pdf.drawString(
            width - 1 * inch, height - 0.35 * inch, f"Page {page_num + 1}/{total_pages}"
        )

        # Use consistent section height for all pages
        section_height = 2.25 * inch  # Same height for all pages

        y_start = height - 0.85 * inch

        for section_idx, layer_name in enumerate(page_layers):
            if layer_name in layers:
                layer_data = layers[layer_name]
                y_offset = y_start - (section_idx * section_height)
                create_layer_section(pdf, layer_name, layer_data, y_offset, width)

        pdf.showPage()

    pdf.save()
    print(f"PDF created: {pdf_path}")


if __name__ == "__main__":
    main()
