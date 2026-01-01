"""Configuration file parsing for ZMK custom_config.h files."""

import re
import sys
from pathlib import Path

from .data_models import LayerAccessInfo, ThumbKeyLabelDict
from .key_code_map import KeyCodeMap, translate_key_code


def parse_config_file(config_path: Path) -> str:
    """Read config file and return content.

    Args:
        config_path: Path to custom_config.h file

    Returns:
        File content as string

    Raises:
        SystemExit: If file cannot be read
    """
    try:
        return config_path.read_text(encoding="utf-8")
    except Exception as e:
        sys.exit(f"ERROR: Could not read {config_path}: {e}")


def extract_layer_definition(content: str, layer_name: str) -> str | None:
    """Extract the key definition for MIRYOKU_LAYER_{layer_name}.

    Returns the full definition with line continuations joined, or None if not found.

    Args:
        content: File content to search
        layer_name: Layer name (e.g., "BASE", "NAV")

    Returns:
        Layer definition string or None if not found
    """
    # Match #define MIRYOKU_LAYER_{NAME} \ ... up to next non-continuation line
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


def parse_layer_keys(definition: str, key_map: KeyCodeMap) -> list[str | None]:
    """Parse a layer definition into list of key codes.

    Returns list of translated key labels (U_NP filtered out as None).

    Args:
        definition: Layer definition string
        key_map: KeyCodeMap for translation

    Returns:
        List of translated key labels
    """
    # Split by comma
    keys_raw = [k.strip() for k in definition.split(",")]

    # Translate each key (include empty keys as None)
    keys = [translate_key_code(k, key_map) if k else None for k in keys_raw]

    return keys


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
        "left": ThumbKeyLabelDict(
            physical=[left_outer, left_inner],
            combined=left_combined,
        ),
        "right": ThumbKeyLabelDict(
            physical=[right_inner, right_outer],
            combined=right_combined,
        ),
    }


def parse_layer_access_from_base(
    base_definition: str, key_map: KeyCodeMap, layout: str = "40key"
) -> dict[str, list[LayerAccessInfo]]:
    """Parse BASE layer to determine which key accesses which layer.

    Looks for U_LT(U_LAYERNAME, KEY) patterns.

    Args:
        base_definition: Layer definition string for BASE layer
        key_map: KeyCodeMap for key translation
        layout: Keyboard layout type ("34key", "36key", "40key", or "unknown")

    Returns:
        Dictionary mapping layer names to list of access info
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
    access_map: dict[str, list[LayerAccessInfo]] = {}

    for idx, key_code in enumerate(keys_raw):
        match = re.match(lt_pattern, key_code)
        if match:
            layer_name = match.group(1)
            key_name = match.group(2).strip()

            # Translate the key name
            if key_name.startswith("&kp"):
                translated_key = translate_key_code(key_name, key_map)
            else:
                translated_key = translate_key_code(f"&kp {key_name}", key_map)

            # Determine position name
            position = determine_position_name(idx, layout)

            # Add to access map
            if layer_name not in access_map:
                access_map[layer_name] = []

            access_map[layer_name].append(
                {
                    "position": position,
                    "key": translated_key or key_name,
                    "index": idx,
                    "source_layer": None,  # BASE layer access has no source_layer
                }
            )

    return access_map


def parse_layer_access_from_all_layers(
    content: str, layers_to_scan: list[str], key_map: KeyCodeMap, layout: str = "40key"
) -> dict[str, list[LayerAccessInfo]]:
    """Parse all layers to find &u_to_U_* patterns indicating layer access.

    This scans non-BASE layers for &u_to_U_* behaviors which indicate
    that a layer can be accessed from another layer.

    Args:
        content: File content to search
        layers_to_scan: List of layer names to scan (excluding BASE)
        key_map: KeyCodeMap for key translation
        layout: Keyboard layout type ("34key", "36key", "40key", or "unknown")

    Returns:
        Dictionary mapping target layer names to access info from all sources
    """
    access_map: dict[str, list[LayerAccessInfo]] = {}

    # Scan each layer for &u_to_U_* patterns
    for source_layer in layers_to_scan:
        layer_def = extract_layer_definition(content, source_layer)
        if layer_def is None:
            continue

        # Parse keys from this layer
        keys_raw = []
        current_key = ""
        paren_depth = 0

        for char in layer_def:
            if char == "(":
                paren_depth += 1
                current_key += char
            elif char == ")":
                paren_depth -= 1
                current_key += char
            elif char == "," and paren_depth == 0:
                if current_key.strip():
                    keys_raw.append(current_key.strip())
                current_key = ""
            else:
                current_key += char

        if current_key.strip():
            keys_raw.append(current_key.strip())

        # Search for &u_to_U_* patterns
        u_to_pattern = r"&u_to_U_(\w+)"

        for idx, key_code in enumerate(keys_raw):
            match = re.search(u_to_pattern, key_code)
            if match:
                target_layer = match.group(1)

                # Determine position name
                position = determine_position_name(idx, layout)

                # Add to access map
                if target_layer not in access_map:
                    access_map[target_layer] = []

                access_map[target_layer].append(
                    {
                        "position": position,
                        "key": f"→{source_layer}",  # Show source layer in key field
                        "index": idx,
                        "source_layer": source_layer,
                    }
                )

    return access_map


def detect_keyboard_layout(content: str) -> str:
    """Detect keyboard layout type based on key count.

    Analyzes the config file to determine the keyboard layout by counting
    the number of keys in the BASE layer definition.

    Args:
        content: File content to analyze

    Returns:
        Layout type: "34key", "36key", "40key", or "unknown"
    """
    base_def = extract_layer_definition(content, "BASE")
    if base_def is None:
        return "unknown"

    # Count keys by splitting on commas while respecting parentheses
    key_count = 0
    paren_depth = 0

    for char in base_def:
        if char == "(":
            paren_depth += 1
        elif char == ")":
            paren_depth -= 1
        elif char == "," and paren_depth == 0:
            key_count += 1

    key_count += 1  # Add 1 for the last key (no trailing comma)

    # Classify layout based on key count
    if key_count <= 34:
        return "34key"
    elif key_count <= 36:
        return "36key"
    elif key_count <= 40:
        return "40key"
    else:
        return "unknown"


def determine_position_name(index: int, layout: str = "40key") -> str:
    """Determine the position name for a key index (0-39).

    Maps key indices to physical positions based on keyboard layout type.

    Args:
        index: Key index (0-39)
        layout: Keyboard layout type ("34key", "36key", "40key", or "unknown")

    Returns:
        Position name (e.g., "left_row0_col0", "left_inner")
    """
    # Thumb row (indices 30-39)
    if 30 <= index <= 39:
        # For 34-key layouts (Ferris-like with 2 thumbs per hand):
        # Combos use indices 30-31 (left) and 32-33 (right)
        # Physical keys use indices 33-34 (left) and 35-36 (right)
        if layout == "34key":
            thumb_positions_34 = {
                30: "left_combined",  # left thumbs combo
                31: "left_combined",  # left thumbs combo (second key)
                32: "right_combined",  # right thumbs combo
                33: "left_outer",  # left physical key 1
                34: "left_inner",  # left physical key 2
                35: "right_inner",  # right physical key 1
                36: "right_outer",  # right physical key 2
            }
            return thumb_positions_34.get(index, f"thumb_{index}")

        # For 36-40 key layouts (Corne-like with more thumb options):
        # Index 32 = left combo (3 physical keys available)
        # Index 37 = right combo (3 physical keys available)
        else:
            thumb_positions_default = {
                32: "left_combined",
                33: "left_outer",
                34: "left_inner",
                35: "right_inner",
                36: "right_outer",
                37: "right_combined",
            }
            return thumb_positions_default.get(index, f"thumb_{index}")

    # Finger keys (indices 0-29)
    row = index // 10
    col = index % 10
    hand = "left" if col < 5 else "right"
    local_col = col if col < 5 else col - 5

    return f"{hand}_row{row}_col{local_col}"


def discover_layers(content: str) -> list[str]:
    """Discover all MIRYOKU_LAYER_* definitions in the config file.

    Returns layer names in the order they appear in the config file.
    Excludes BASE by default.

    Args:
        content: File content to search

    Returns:
        List of layer names found in config (e.g., ["TAP", "NUM", "SYM", ...])
    """
    pattern = r"#define\s+MIRYOKU_LAYER_([A-Z_]+)\s"
    matches = re.findall(pattern, content)

    # Filter out BASE (always excluded)
    excluded = {"BASE"}

    layers = [m for m in matches if m not in excluded]

    return layers
