"""Tests for layer processing logic."""


from zmk_to_pdf.key_code_map import KeyCodeMap
from zmk_to_pdf.layer_processor import (
    build_layer_data,
    create_page_groupings,
    determine_active_thumb,
    generate_access_text,
)
from zmk_to_pdf.parser import (
    discover_layers,
    extract_layer_definition,
    parse_layer_access_from_base,
    parse_layer_keys,
)


class TestCreatePageGroupings:
    """Test page grouping logic."""

    def test_group_4_layers_single_page(self) -> None:
        """Test grouping 4 layers on single page."""
        layers = ["TAP", "NUM", "SYM", "NAV"]
        pages = create_page_groupings(layers)
        assert len(pages) == 1
        assert pages[0] == layers

    def test_group_8_layers_two_pages(self) -> None:
        """Test grouping 8 layers on two pages."""
        layers = ["TAP", "NUM", "SYM", "NAV", "BUTTON", "MEDIA", "FUN", "MOUSE"]
        pages = create_page_groupings(layers)
        assert len(pages) == 2
        assert len(pages[0]) == 4
        assert len(pages[1]) == 4

    def test_group_prefers_first_page_order(self) -> None:
        """Test that first page has preferred layers first."""
        layers = ["FUN", "BUTTON", "MEDIA", "TAP", "NUM", "SYM", "NAV"]
        pages = create_page_groupings(layers)
        # Preferred order: TAP, NUM, SYM, NAV
        first_page = pages[0]
        assert first_page[0] == "TAP"
        assert first_page[1] == "NUM"
        assert first_page[2] == "SYM"
        assert first_page[3] == "NAV"

    def test_group_missing_preferred_layers(self) -> None:
        """Test grouping when some preferred layers are missing."""
        layers = ["TAP", "FUN", "BUTTON", "MEDIA"]
        pages = create_page_groupings(layers)
        first_page = pages[0]
        assert "TAP" in first_page
        assert "FUN" in first_page

    def test_group_single_layer(self) -> None:
        """Test grouping single layer."""
        layers = ["NAV"]
        pages = create_page_groupings(layers)
        assert len(pages) == 1
        assert pages[0] == ["NAV"]

    def test_group_empty_list(self) -> None:
        """Test grouping empty layer list."""
        layers: list[str] = []
        pages = create_page_groupings(layers)
        assert len(pages) == 0


class TestDetermineActiveThumb:
    """Test active thumb determination."""

    def test_tap_layer_no_active_thumbs(self) -> None:
        """Test TAP layer has no active thumbs."""
        result = determine_active_thumb("TAP", {})
        assert result["left"] is None
        assert result["right"] is None

    def test_missing_layer_no_active_thumbs(self) -> None:
        """Test missing layer has no active thumbs."""
        result = determine_active_thumb("NONEXISTENT", {})
        assert result["left"] is None
        assert result["right"] is None

    def test_left_combined_active(self) -> None:
        """Test left combined thumb as active."""
        access = {
            "NAV": [
                {"position": "left_combined", "key": "ESC", "index": 32},
            ]
        }
        result = determine_active_thumb("NAV", access)
        assert result["left"] == "combined"
        assert result["right"] is None

    def test_left_outer_active(self) -> None:
        """Test left outer thumb as active."""
        access = {
            "NAV": [
                {"position": "left_outer", "key": "Z", "index": 33},
            ]
        }
        result = determine_active_thumb("NAV", access)
        assert result["left"] == 0
        assert result["right"] is None

    def test_right_inner_active(self) -> None:
        """Test right inner thumb as active."""
        access = {
            "NAV": [
                {"position": "right_inner", "key": "X", "index": 35},
            ]
        }
        result = determine_active_thumb("NAV", access)
        assert result["left"] is None
        assert result["right"] == 0


class TestGenerateAccessText:
    """Test access text generation."""

    def test_tap_layer_access_text(self) -> None:
        """Test TAP layer access text."""
        result = generate_access_text("TAP", {})
        assert result == "→TAP from other layers"

    def test_single_access_key_with_position(self) -> None:
        """Test single access key with position description."""
        access = {
            "NAV": [
                {"position": "left_inner", "key": "TAB", "index": 34},
            ]
        }
        result = generate_access_text("NAV", access)
        assert "TAB" in result
        assert "left inner" in result
        assert "Hold" in result

    def test_single_access_key_no_position(self) -> None:
        """Test single access key without position."""
        access = {
            "NAV": [
                {"position": "left_row0_col0", "key": "Q", "index": 0},
            ]
        }
        result = generate_access_text("NAV", access)
        assert "Q" in result
        assert "Hold" in result

    def test_multiple_access_keys(self) -> None:
        """Test multiple access keys."""
        access = {
            "BUTTON": [
                {"position": "left_row2_col0", "key": "Z", "index": 20},
                {"position": "left_row2_col4", "key": "B", "index": 24},
                {"position": "right_row2_col4", "key": "/", "index": 29},
            ]
        }
        result = generate_access_text("BUTTON", access)
        assert "Hold" in result
        assert "Z" in result
        assert "B" in result
        assert "SLASH" in result  # "/" should be replaced with "SLASH"

    def test_missing_layer_access(self) -> None:
        """Test access text for missing layer."""
        result = generate_access_text("NONEXISTENT", {})
        assert result == "Access unknown"


class TestBuildLayerData:
    """Test layer data building."""

    def test_build_base_layer_data(self, config_full: str, key_map: KeyCodeMap) -> None:
        """Test building layer data for BASE layer."""
        base_def = extract_layer_definition(config_full, "BASE")
        assert base_def is not None
        keys = parse_layer_keys(base_def, key_map)
        layer_access = parse_layer_access_from_base(base_def, key_map)

        layer_data = build_layer_data("BASE", keys, layer_access)

        # Check structure
        assert "left_hand" in layer_data
        assert "right_hand" in layer_data
        assert "left_thumbs" in layer_data
        assert "right_thumbs" in layer_data
        assert "access" in layer_data

    def test_layer_data_left_hand_structure(
        self, config_full: str, key_map: KeyCodeMap
    ) -> None:
        """Test left hand structure in layer data."""
        base_def = extract_layer_definition(config_full, "BASE")
        assert base_def is not None
        keys = parse_layer_keys(base_def, key_map)
        layer_data = build_layer_data("BASE", keys, {})

        left_hand = layer_data["left_hand"]
        assert len(left_hand) == 3  # 3 rows
        assert len(left_hand[0]) == 5  # 5 keys per row

    def test_layer_data_right_hand_structure(
        self, config_full: str, key_map: KeyCodeMap
    ) -> None:
        """Test right hand structure in layer data."""
        base_def = extract_layer_definition(config_full, "BASE")
        assert base_def is not None
        keys = parse_layer_keys(base_def, key_map)
        layer_data = build_layer_data("BASE", keys, {})

        right_hand = layer_data["right_hand"]
        assert len(right_hand) == 3  # 3 rows
        assert len(right_hand[0]) == 5  # 5 keys per row

    def test_layer_data_thumb_keys(self, config_full: str, key_map: KeyCodeMap) -> None:
        """Test thumb keys in layer data."""
        base_def = extract_layer_definition(config_full, "BASE")
        assert base_def is not None
        keys = parse_layer_keys(base_def, key_map)
        layer_data = build_layer_data("BASE", keys, {})

        left_thumbs = layer_data["left_thumbs"]
        assert len(left_thumbs["physical"]) == 2
        assert "combined" in left_thumbs

        right_thumbs = layer_data["right_thumbs"]
        assert len(right_thumbs["physical"]) == 2
        assert "combined" in right_thumbs

    def test_layer_data_integration(
        self, config_minimal: str, key_map: KeyCodeMap
    ) -> None:
        """Integration test building full layer data."""
        content = config_minimal
        layers_to_display = discover_layers(content)
        base_def = extract_layer_definition(content, "BASE")
        assert base_def is not None
        layer_access = parse_layer_access_from_base(base_def, key_map)

        for layer_name in layers_to_display:
            layer_def = extract_layer_definition(content, layer_name)
            if layer_def:
                keys = parse_layer_keys(layer_def, key_map)
                layer_data = build_layer_data(layer_name, keys, layer_access)
                assert "left_hand" in layer_data
                assert "access" in layer_data
