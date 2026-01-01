"""Tests for key code translation and color categorization."""

from reportlab.lib.colors import HexColor

from zmk_to_pdf.config import PDFConfig
from zmk_to_pdf.key_code_map import KeyColorizer, KeyCodeMap, translate_key_code


class TestKeyCodeMap:
    """Test KeyCodeMap loading and lookups."""

    def test_load_key_codes(self, key_map: KeyCodeMap) -> None:
        """Test loading key codes from YAML."""
        assert key_map.has("&kp A")
        assert key_map.has("&kp Q")

    def test_basic_letter_lookup(self, key_map: KeyCodeMap) -> None:
        """Test looking up basic letters."""
        assert key_map.get("&kp A") == "A"
        assert key_map.get("&kp Q") == "Q"

    def test_symbol_lookup(self, key_map: KeyCodeMap) -> None:
        """Test looking up symbols."""
        assert key_map.get("&kp COMMA") == ","
        assert key_map.get("&kp DOT") == "."
        assert key_map.get("&kp SLASH") == "/"

    def test_navigation_lookup(self, key_map: KeyCodeMap) -> None:
        """Test looking up navigation keys."""
        assert key_map.get("&kp LEFT") == "←"
        assert key_map.get("&kp UP") == "↑"
        assert key_map.get("&kp RIGHT") == "→"

    def test_modifier_lookup(self, key_map: KeyCodeMap) -> None:
        """Test looking up modifier keys."""
        assert key_map.get("&kp LCTRL") == "LCTRL"
        assert key_map.get("&kp LALT") == "LALT"

    def test_system_key_lookup(self, key_map: KeyCodeMap) -> None:
        """Test looking up system keys."""
        assert key_map.get("&kp BSPC") == "BSPC"
        assert key_map.get("&kp RET") == "RET"
        assert key_map.get("&kp DEL") == "DEL"

    def test_layer_transition_lookup(self, key_map: KeyCodeMap) -> None:
        """Test looking up layer transitions."""
        assert key_map.get("&u_to_U_NAV") == "→NAV"
        assert key_map.get("&u_to_U_NUM") == "→NUM"

    def test_missing_key_returns_none(self, key_map: KeyCodeMap) -> None:
        """Test that missing keys return None from has."""
        assert not key_map.has("&kp UNKNOWN")

    def test_special_u_np_returns_none(self, key_map: KeyCodeMap) -> None:
        """Test that U_NP maps to None."""
        assert key_map.get("U_NP") is None

    def test_special_u_na_returns_dash(self, key_map: KeyCodeMap) -> None:
        """Test that U_NA maps to dash."""
        assert key_map.get("U_NA") == "-"


class TestTranslateKeyCode:
    """Test translate_key_code function."""

    def test_direct_lookup(self, key_map: KeyCodeMap) -> None:
        """Test direct key code lookup."""
        result = translate_key_code("&kp A", key_map)
        assert result == "A"

    def test_u_np_returns_none(self, key_map: KeyCodeMap) -> None:
        """Test U_NP translates to None."""
        result = translate_key_code("U_NP", key_map)
        assert result is None

    def test_u_mt_macro_extraction(self, key_map: KeyCodeMap) -> None:
        """Test U_MT macro parsing."""
        result = translate_key_code("U_MT(LCTRL, A)", key_map)
        assert result == "A"

    def test_u_mt_macro_with_spaces(self, key_map: KeyCodeMap) -> None:
        """Test U_MT macro parsing with spaces."""
        result = translate_key_code("U_MT( LCTRL , A )", key_map)
        assert result == "A"

    def test_u_lt_macro_extraction(self, key_map: KeyCodeMap) -> None:
        """Test U_LT macro parsing."""
        result = translate_key_code("U_LT(U_NAV, TAB)", key_map)
        assert result == "TAB"

    def test_u_lt_with_kp_key(self, key_map: KeyCodeMap) -> None:
        """Test U_LT with &kp prefixed key."""
        result = translate_key_code("U_LT(U_NAV, &kp TAB)", key_map)
        assert result == "TAB"

    def test_unknown_code_returns_raw(self, key_map: KeyCodeMap) -> None:
        """Test unknown codes return raw value."""
        result = translate_key_code("&kp UNKNOWN_KEY", key_map)
        assert result == "&kp UNKNOWN_KEY"

    def test_nested_u_mt_with_symbols(self, key_map: KeyCodeMap) -> None:
        """Test U_MT with symbol extraction."""
        result = translate_key_code("U_MT(LCTRL, COMMA)", key_map)
        assert result == ","


class TestKeyColorizer:
    """Test KeyColorizer color assignment."""

    def test_colorizer_initialization(self, pdf_config: PDFConfig) -> None:
        """Test creating a KeyColorizer."""
        colorizer = KeyColorizer(pdf_config)
        assert colorizer.config == pdf_config

    def test_empty_key_color(self, pdf_config: PDFConfig) -> None:
        """Test color for empty/empty keys."""
        colorizer = KeyColorizer(pdf_config)
        bg, text = colorizer.get_colors(None)
        assert bg == HexColor(pdf_config.color_empty)

    def test_dash_key_color(self, pdf_config: PDFConfig) -> None:
        """Test color for dash."""
        colorizer = KeyColorizer(pdf_config)
        bg, text = colorizer.get_colors("-")
        assert bg == HexColor(pdf_config.color_empty)

    def test_navigation_key_color(self, pdf_config: PDFConfig) -> None:
        """Test color for navigation keys."""
        colorizer = KeyColorizer(pdf_config)
        bg, text = colorizer.get_colors("←")
        assert bg == HexColor(pdf_config.color_navigation)

    def test_modifier_key_color(self, pdf_config: PDFConfig) -> None:
        """Test color for modifier keys."""
        colorizer = KeyColorizer(pdf_config)
        bg, text = colorizer.get_colors("LCTRL")
        assert bg == HexColor(pdf_config.color_modifier)

    def test_system_key_color(self, pdf_config: PDFConfig) -> None:
        """Test color for system keys."""
        colorizer = KeyColorizer(pdf_config)
        bg, text = colorizer.get_colors("BSPC")
        assert bg == HexColor(pdf_config.color_system)

    def test_mouse_button_color(self, pdf_config: PDFConfig) -> None:
        """Test color for mouse buttons."""
        colorizer = KeyColorizer(pdf_config)
        bg, text = colorizer.get_colors("BTN1")
        assert bg == HexColor(pdf_config.color_mouse_clipboard)

    def test_clipboard_key_color(self, pdf_config: PDFConfig) -> None:
        """Test color for clipboard keys."""
        colorizer = KeyColorizer(pdf_config)
        bg, text = colorizer.get_colors("CPY")
        assert bg == HexColor(pdf_config.color_mouse_clipboard)

    def test_layer_access_key_color(self, pdf_config: PDFConfig) -> None:
        """Test color for layer access keys."""
        colorizer = KeyColorizer(pdf_config)
        bg, text = colorizer.get_colors("→NAV")
        assert bg == HexColor(pdf_config.color_layer_access)

    def test_regular_key_color(self, pdf_config: PDFConfig) -> None:
        """Test color for regular keys."""
        colorizer = KeyColorizer(pdf_config)
        bg, text = colorizer.get_colors("A")
        assert bg == HexColor(pdf_config.color_regular)

    def test_inactive_key_color(self, pdf_config: PDFConfig) -> None:
        """Test color for inactive keys."""
        colorizer = KeyColorizer(pdf_config)
        bg, text = colorizer.get_colors("A", is_inactive=True)
        assert bg == HexColor(pdf_config.color_inactive_bg)
        assert text == HexColor(pdf_config.color_inactive_text)
