#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "reportlab",
# ]
# ///

import os
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, black

# Thumb key layout per spec:
# - 2 physical thumb keys per hand, aligned to interior
# - 1 combined thumb key per hand, positioned UNDER physical thumbs, centered
#
# LEFT: SPACE (physical) + TAB (physical) = ESC (combined, SPACE+TAB pressed together)
# RIGHT: BSPC (physical) + DEL (physical) = RET (combined, BSPC+DEL pressed together)

# Layer definitions from custom_config.h
# Structure: left_thumbs/right_thumbs = {"physical": [key1, key2], "combined": key}
# All 6 thumb keys shown for positional awareness; "active" marks the layer access key
# Physical thumbs: SPACE, TAB (left); BSPC, DEL (right)
# Combined thumbs: ESC (left, SPACE+TAB); RET (right, BSPC+DEL)
layers = {
    "TAP": {
        "description": "Tap layer (no hold modifiers)",
        "access": "Tap any key on BASE layer",
        "left_hand": [
            ["Q", "W", "E", "R", "T"],
            ["A", "S", "D", "F", "G"],
            ["Z", "X", "C", "V", "B"],
        ],
        "right_hand": [
            ["Y", "U", "I", "O", "P"],
            ["H", "J", "K", "L", "'"],
            ["N", "M", ",", ".", "/"],
        ],
        "left_thumbs": {
            "physical": ["SPACE", "TAB"],
            "combined": "ESC",
            "active": "all",
        },
        "right_thumbs": {
            "physical": ["BSPC", "DEL"],
            "combined": "RET",
            "active": "all",
        },
    },
    "BUTTON": {
        "description": "Mouse buttons & clipboard",
        "access": "Hold Z (left) OR SLASH (right) OR RET (both right thumbs)",
        "left_hand": [
            ["RDO", "UND", "PST", "CPY", "CUT"],
            ["LCTRL", "LALT", "LGUI", "LSHFT", "CPY"],
            ["UND", "CUT", "CPY", "PST", "PST"],
        ],
        "right_hand": [
            ["CUT", "CPY", "PST", "UND", "RDO"],
            ["CPY", "RSHFT", "RGUI", "LALT", "RCTRL"],
            ["PST", "PST", "CPY", "CUT", "UND"],
        ],
        "left_thumbs": {
            "physical": ["SPACE", "TAB"],
            "combined": "ESC",
            "active": None,
        },
        "right_thumbs": {
            "physical": ["BSPC", "DEL"],
            "combined": "RET",
            "active": "combined",
        },
    },
    "NAV": {
        "description": "Navigation & arrow keys",
        "access": "Hold TAB (left hand)",
        "left_hand": [
            ["BOOT", "→TAP", "→EXT", "→BASE", "-"],
            ["LCTRL", "LALT", "LGUI", "LSHFT", "-"],
            ["-", "RALT", "→NUM", "→NAV", "-"],
        ],
        "right_hand": [
            ["-", "-", "-", "-", "-"],
            ["←", "↓", "↑", "→", "-"],
            ["HOME", "PgDn", "PgUp", "END", "-"],
        ],
        "left_thumbs": {"physical": ["SPACE", "TAB"], "combined": "ESC", "active": 1},
        "right_thumbs": {
            "physical": ["BSPC", "DEL"],
            "combined": "RET",
            "active": None,
        },
    },
    "MOUSE": {
        "description": "Mouse movement & wheel",
        "access": "Hold DEL (right hand)",
        "left_hand": [
            ["BOOT", "→TAP", "→EXT", "→BASE", "-"],
            ["LCTRL", "LALT", "LGUI", "LSHFT", "-"],
            ["-", "RALT", "→SYM", "→MOUSE", "-"],
        ],
        "right_hand": [
            ["CUT", "CPY", "PST", "UND", "RDO"],
            ["CPY", "M↑", "M↓", "M←", "M→"],
            ["PST", "WH←", "WH↓", "WH↑", "WH→"],
        ],
        "left_thumbs": {
            "physical": ["SPACE", "TAB"],
            "combined": "ESC",
            "active": None,
        },
        "right_thumbs": {"physical": ["BSPC", "DEL"], "combined": "RET", "active": 1},
    },
    "MEDIA": {
        "description": "RGB, audio, bluetooth",
        "access": "Hold DEL (right hand)",
        "left_hand": [
            ["BOOT", "→TAP", "→EXT", "→BASE", "-"],
            ["LCTRL", "LALT", "LGUI", "LSHFT", "-"],
            ["-", "RALT", "→FUN", "→MEDIA", "-"],
        ],
        "right_hand": [
            ["RGB_T", "RGB_E", "RGB_H+", "RGB_S+", "RGB_B+"],
            ["EP_TOG", "PREV", "VOL-", "VOL+", "NEXT"],
            ["OUT_T", "BT0", "BT1", "BT2", "BT3"],
        ],
        "left_thumbs": {
            "physical": ["SPACE", "TAB"],
            "combined": "ESC",
            "active": None,
        },
        "right_thumbs": {"physical": ["BSPC", "DEL"], "combined": "RET", "active": 1},
    },
    "NUM": {
        "description": "Numbers & basic symbols",
        "access": "Hold SPACE (left hand)",
        "left_hand": [
            ["BOOT", "→TAP", "→EXT", "→BASE", "-"],
            ["LCTRL", "LALT", "LGUI", "LSHFT", "-"],
            ["-", "→NUM", "→NAV", "RALT", "-"],
        ],
        "right_hand": [
            ["[", "7", "8", "9", "]"],
            [";", "4", "5", "6", "="],
            ["`", "1", "2", "3", "\\"],
        ],
        "left_thumbs": {"physical": ["SPACE", "TAB"], "combined": "ESC", "active": 0},
        "right_thumbs": {
            "physical": ["BSPC", "DEL"],
            "combined": "RET",
            "active": None,
        },
    },
    "SYM": {
        "description": "Symbols & special characters (includes @ here)",
        "access": "Hold BSPC (right hand)",
        "left_hand": [
            ["{", "&", "*", "(", "}"],
            [":", "$", "%", "^", "+"],
            ["~", "!", "@", "#", "|"],
        ],
        "right_hand": [
            ["-", "→BASE", "→EXT", "→TAP", "BOOT"],
            ["-", "RSHFT", "RGUI", "LALT", "RCTRL"],
            ["-", "→SYM", "→MOUSE", "RALT", "-"],
        ],
        "left_thumbs": {
            "physical": ["SPACE", "TAB"],
            "combined": "ESC",
            "active": None,
        },
        "right_thumbs": {"physical": ["BSPC", "DEL"], "combined": "RET", "active": 0},
    },
    "FUN": {
        "description": "Function keys F1-F12",
        "access": "Hold ESC (left hand, SPACE+TAB combined)",
        "left_hand": [
            ["BOOT", "→TAP", "→EXT", "→BASE", "-"],
            ["LCTRL", "LALT", "LGUI", "LSHFT", "-"],
            ["-", "→NUM", "→NAV", "RALT", "-"],
        ],
        "right_hand": [
            ["F12", "F7", "F8", "F9", "PrSc"],
            ["F11", "F4", "F5", "F6", "SlLk"],
            ["F10", "F1", "F2", "F3", "Pause"],
        ],
        "left_thumbs": {
            "physical": ["SPACE", "TAB"],
            "combined": "ESC",
            "active": "combined",
        },
        "right_thumbs": {
            "physical": ["BSPC", "DEL"],
            "combined": "RET",
            "active": None,
        },
    },
}


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
    elif text == "-" or text == "":
        color = HexColor("#CCCCCC")  # Light grey for empty
        text_color = HexColor("#999999")
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
    # Key dimensions - wider for better readability, using more horizontal space
    key_width = 0.60 * inch
    key_height = 0.34 * inch
    key_spacing = 0.03 * inch
    hand_gap = 0.40 * inch  # Gap between the two hands

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

    # Title and description above left hand keyboard (on same line)
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(left_hand_x, y_offset, layer_name)

    # Description next to title, constrained to left hand width
    pdf.setFont("Helvetica", 9)
    pdf.setFillColor(HexColor("#666666"))
    title_width = pdf.stringWidth(layer_name, "Helvetica-Bold", 16)
    desc_text = layer_data["description"]
    # Calculate remaining width for description
    max_desc_width = hand_width - title_width - 0.2 * inch
    while (
        pdf.stringWidth(desc_text, "Helvetica", 9) > max_desc_width
        and len(desc_text) > 10
    ):
        desc_text = desc_text[:-4] + "..."
    pdf.drawString(
        left_hand_x + title_width + 0.1 * inch, y_offset + 0.02 * inch, desc_text
    )

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
            draw_key(pdf, x, y, key_width, key_height, key, font_size=9)

    # Calculate thumb row y positions (below finger keys)
    # After 3 rows of keys with spacing
    physical_thumb_y = first_row_y - (3 * (key_height + key_spacing)) - 0.04 * inch
    combined_thumb_y = physical_thumb_y - (
        key_height + 0.04 * inch
    )  # Below physical thumbs

    # Draw left hand thumb keys
    # Per spec: 2 physical thumbs aligned to interior (right side), combined key below centered
    # Always show all 3 keys for positional awareness; inactive ones are grayed out
    left_thumbs = layer_data["left_thumbs"]
    left_active = left_thumbs.get("active")  # None, 0, 1, "combined", or "all"

    # Draw physical thumb keys (aligned to interior = columns 3-4)
    for idx, key in enumerate(left_thumbs["physical"]):
        col_offset = 3 + idx  # Columns 3 and 4 (interior/right side)
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
    # Center between columns 3 and 4
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
            draw_key(pdf, x, y, key_width, key_height, key, font_size=9)

    # Draw right hand thumb keys
    # Per spec: 2 physical thumbs aligned to interior (left side), combined key below centered
    # Always show all 3 keys for positional awareness; inactive ones are grayed out
    right_thumbs = layer_data["right_thumbs"]
    right_active = right_thumbs.get("active")  # None, 0, 1, "combined", or "all"

    # Draw physical thumb keys (aligned to interior = columns 0-1)
    for idx, key in enumerate(right_thumbs["physical"]):
        col_offset = idx  # Columns 0 and 1 (interior/left side)
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
    # Center between columns 0 and 1
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


# Create PDF - output to repository root
script_dir = Path(__file__).parent
repo_root = script_dir.parent
pdf_path = repo_root / "layout.pdf"
pdf = canvas.Canvas(str(pdf_path), pagesize=letter)

width, height = letter

# Define page groupings per spec (BASE layer excluded)
# 3 layers per page for larger, more readable layout
# Page 1: TAP, NUM, SYM
# Page 2: NAV, BUTTON, MOUSE
# Page 3: MEDIA, FUN
page_groupings = [
    ["TAP", "NUM", "SYM"],
    ["NAV", "BUTTON", "MOUSE"],
    ["MEDIA", "FUN"],
]

total_pages = len(page_groupings)

for page_num, page_layers in enumerate(page_groupings):
    # Title on page
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(0.5 * inch, height - 0.35 * inch, f"Miryoku Keyboard Layers")

    # Legend for thumb keys
    pdf.setFont("Helvetica", 8)
    pdf.drawString(
        0.5 * inch,
        height - 0.55 * inch,
        "Legend: Red dashed border = Combined thumb key (SPACE+TAB on left, BSPC+DEL on right)",
    )

    # Page number
    pdf.setFont("Helvetica", 9)
    pdf.drawString(
        width - 1 * inch, height - 0.35 * inch, f"Page {page_num + 1}/{total_pages}"
    )

    # Draw 3 layers per page for larger layout
    layers_per_page = 3
    y_start = height - 0.85 * inch  # Start lower to avoid legend overlap
    # Calculate section height based on actual content needs
    section_height = 3.0 * inch

    for section_idx, layer_name in enumerate(page_layers):
        if layer_name in layers:
            layer_data = layers[layer_name]
            y_offset = y_start - (section_idx * section_height)
            create_layer_section(pdf, layer_name, layer_data, y_offset, width)

    pdf.showPage()

pdf.save()
print(f"PDF created: {pdf_path}")
