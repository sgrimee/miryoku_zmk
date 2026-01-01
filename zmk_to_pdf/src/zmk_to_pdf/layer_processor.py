"""Layer processing and data structure building."""

from .data_models import LayerAccessInfo, LayerData, ThumbKeysActive, ThumbKeysDict


def create_page_groupings(layers: list[str]) -> list[list[str]]:
    """Group layers into pages dynamically.

    - First page gets up to 4 layers, preferring TAP, NUM, SYM, NAV if present
    - Subsequent pages get up to 4 layers each
    - Remaining layers fill in order of appearance in config

    Args:
        layers: List of layer names to group

    Returns:
        List of pages, where each page is a list of layer names
    """
    preferred_first = ["TAP", "NUM", "SYM", "NAV"]

    # Build first page: preferred layers first (if they exist), in preferred order
    page1 = [layer for layer in preferred_first if layer in layers]

    # Fill remaining page1 slots with other layers (up to 4 total)
    remaining = [layer for layer in layers if layer not in page1]
    while len(page1) < 4 and remaining:
        page1.append(remaining.pop(0))

    # Build subsequent pages with remaining layers (4 per page)
    pages = [page1] if page1 else []
    while remaining:
        page = remaining[:4]
        remaining = remaining[4:]
        pages.append(page)

    return pages


def determine_active_thumb(
    layer_name: str, layer_access: dict[str, list[LayerAccessInfo]]
) -> dict[str, str | int | None]:
    """Determine which thumb keys are the access keys for this layer.

    Returns:
        Dictionary with "left" and "right" active thumb info

    Note: This function identifies which thumb key is used to ACCESS the layer,
    not which thumb keys are active IN the layer. A thumb key being the access key
    gets highlighted in yellow. All other keys with actual keycodes (not U_NA or U_NP)
    are considered active in the layer.
    """
    # For TAP layer, no thumb keys are used to access it (it's accessed via →TAP)
    # So we return None to indicate no access keys, but thumb keys will still be
    # shown as active if they have keycodes
    if layer_name == "TAP":
        return {"left": None, "right": None}

    if layer_name not in layer_access:
        return {"left": None, "right": None}

    active: dict[str, str | int | None] = {"left": None, "right": None}

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


def generate_access_text(
    layer_name: str, layer_access: dict[str, list[LayerAccessInfo]]
) -> str:
    """Generate access text for a layer based on how it's accessed from BASE.

    Args:
        layer_name: Name of the layer
        layer_access: Access map from BASE layer

    Returns:
        Human-readable access description
    """
    if layer_name == "TAP":
        return "→TAP from other layers"

    if layer_name not in layer_access:
        return "Access unknown"

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


def build_layer_data(
    layer_name: str,
    keys: list[str | None],
    layer_access: dict[str, list[LayerAccessInfo]],
) -> LayerData:
    """Build the layer data structure for rendering.

    Args:
        layer_name: Name of the layer (e.g., "TAP", "NAV")
        keys: List of 40 translated key labels (with U_NP as None)
        layer_access: Access map from parse_layer_access_from_base()

    Returns:
        Dictionary with left_hand, right_hand, left_thumbs, right_thumbs, access
    """
    # Split into rows (3 rows of 10 keys each for finger keys)
    # Row 0: keys[0:10] -> left[0:5], right[5:10]
    # Row 1: keys[10:20]
    # Row 2: keys[20:30]

    left_hand: list[list[str | None]] = [
        [keys[0], keys[1], keys[2], keys[3], keys[4]],  # Row 0 left
        [keys[10], keys[11], keys[12], keys[13], keys[14]],  # Row 1 left
        [keys[20], keys[21], keys[22], keys[23], keys[24]],  # Row 2 left
    ]

    right_hand: list[list[str | None]] = [
        [keys[5], keys[6], keys[7], keys[8], keys[9]],  # Row 0 right
        [keys[15], keys[16], keys[17], keys[18], keys[19]],  # Row 1 right
        [keys[25], keys[26], keys[27], keys[28], keys[29]],  # Row 2 right
    ]

    # Extract this layer's thumb keys from its own keys array
    # Indices: 32=left_combined, 33=left_outer, 34=left_inner
    #          35=right_inner, 36=right_outer, 37=right_combined
    layer_left_thumbs: ThumbKeysDict = {
        "physical": [keys[33], keys[34]],  # left outer, left inner
        "combined": keys[32],
    }
    layer_right_thumbs: ThumbKeysDict = {
        "physical": [keys[35], keys[36]],  # right inner, right outer
        "combined": keys[37],
    }

    # Determine active thumbs
    active_thumbs = determine_active_thumb(layer_name, layer_access)

    # Generate access text
    access_text = generate_access_text(layer_name, layer_access)

    return {
        "left_hand": left_hand,
        "right_hand": right_hand,
        "left_thumbs": ThumbKeysActive(
            physical=layer_left_thumbs["physical"],
            combined=layer_left_thumbs["combined"],
            active=active_thumbs["left"],
        ),
        "right_thumbs": ThumbKeysActive(
            physical=layer_right_thumbs["physical"],
            combined=layer_right_thumbs["combined"],
            active=active_thumbs["right"],
        ),
        "access": access_text,
    }
