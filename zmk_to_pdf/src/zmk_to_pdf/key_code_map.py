"""Key code translation and color categorization."""

import re
from pathlib import Path
from typing import TYPE_CHECKING

import yaml
from reportlab.lib.colors import Color, HexColor, black

if TYPE_CHECKING:
    from .config import PDFConfig


class KeyCodeMap:
    """Manages ZMK key code translation from YAML file."""

    def __init__(self, yaml_path: Path | None = None) -> None:
        """Initialize with key codes from YAML file.

        Args:
            yaml_path: Path to key_codes.yaml. If None, loads from package directory.
        """
        if yaml_path is None:
            yaml_path = Path(__file__).parent / "key_codes.yaml"

        self._map: dict[str, str | None] = {}
        self._load_yaml(yaml_path)

    def _load_yaml(self, yaml_path: Path) -> None:
        """Load and flatten YAML key code mapping."""
        with open(yaml_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            raise ValueError("Key codes YAML must be a dictionary")

        # Flatten nested structure
        for category, codes in data.items():
            if isinstance(codes, dict):
                self._map.update(codes)

    def get(self, key: str) -> str | None:
        """Get translated label for a key code.

        Args:
            key: ZMK key code (e.g., "&kp A", "U_NP")

        Returns:
            Translated label or None if U_NP
        """
        return self._map.get(key)

    def has(self, key: str) -> bool:
        """Check if key code is in map."""
        return key in self._map


class KeyColorizer:
    """Determines colors for keys based on their function."""

    def __init__(self, config: "PDFConfig") -> None:
        """Initialize with color configuration.

        Args:
            config: PDFConfig instance with color definitions
        """
        self.config = config

    def get_colors(
        self, text: str | None, is_inactive: bool = False
    ) -> tuple[Color, Color]:
        """Get background and text colors for a key.

        Args:
            text: Key label text
            is_inactive: Whether key is inactive for current layer

        Returns:
            Tuple of (background_color, text_color)
        """
        if is_inactive:
            return (
                HexColor(self.config.color_inactive_bg),
                HexColor(self.config.color_inactive_text),
            )

        if text is None or text == "-" or text == "":
            return (
                HexColor(self.config.color_empty),
                HexColor(self.config.color_empty_text),
            )

        # Layer transitions and special keys (check before navigation)
        # These include layer names like "→NAV", "→NUM", "BOOT", etc.
        if "BOOT" in text or any(
            layer in text
            for layer in [
                "NAV",
                "SYM",
                "NUM",
                "FUN",
                "MEDIA",
                "BUTTON",
                "BASE",
                "TAP",
            ]
        ):
            return (HexColor(self.config.color_layer_access), black)

        # Navigation keys (single arrow keys without layer names)
        if any(c in text for c in ["→", "↑", "↓", "←"]):
            return (HexColor(self.config.color_navigation), black)

        # Modifiers
        if any(
            c in text
            for c in ["CTRL", "ALT", "SHIFT", "LGUI", "RGUI", "LSHFT", "RSHFT"]
        ):
            return (HexColor(self.config.color_modifier), black)

        # Mouse and clipboard
        if text in ["BTN1", "BTN2", "BTN3", "RDO", "UND", "PST", "CPY", "CUT"]:
            return (HexColor(self.config.color_mouse_clipboard), black)

        # System keys
        if text in ["BSPC", "RET", "DEL", "ESC", "SPC", "TAB", "SPACE"]:
            return (HexColor(self.config.color_system), black)

        # Regular keys
        return (HexColor(self.config.color_regular), black)


def translate_key_code(code: str, key_map: KeyCodeMap) -> str | None:
    """Translate ZMK key code to display label.

    Handles:
    - Direct lookup in key code map
    - U_MT(MOD, KEY) macros -> extract KEY
    - U_LT(LAYER, KEY) macros -> extract KEY
    - U_NP -> None (filtered out)
    - Unknown codes -> return raw code for debugging

    Args:
        code: ZMK key code to translate
        key_map: KeyCodeMap instance for lookups

    Returns:
        Translated label or None for U_NP
    """
    code = code.strip()

    # Handle U_NP specially (filtered out)
    if code == "U_NP":
        return None

    # Direct lookup
    if key_map.has(code):
        return key_map.get(code)

    # Handle U_MT(MOD, KEY) - extract KEY (tap behavior)
    mt_match = re.match(r"U_MT\s*\(\s*([^,]+)\s*,\s*([^)]+)\s*\)", code)
    if mt_match:
        key = mt_match.group(2).strip()
        # Recursively translate the extracted key
        if not key.startswith("&kp"):
            return translate_key_code(f"&kp {key}", key_map)
        return translate_key_code(key, key_map)

    # Handle U_LT(LAYER, KEY) - extract KEY (tap behavior)
    lt_match = re.match(r"U_LT\s*\(\s*([^,]+)\s*,\s*([^)]+)\s*\)", code)
    if lt_match:
        key = lt_match.group(2).strip()
        # Recursively translate the extracted key
        if not key.startswith("&kp"):
            return translate_key_code(f"&kp {key}", key_map)
        return translate_key_code(key, key_map)

    # Fallback: return the raw code (for debugging unknown codes)
    return code
