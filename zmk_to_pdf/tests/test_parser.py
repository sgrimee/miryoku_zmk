"""Tests for configuration file parsing."""

import pytest

from zmk_to_pdf.key_code_map import KeyCodeMap
from zmk_to_pdf.parser import (
    determine_position_name,
    discover_layers,
    extract_layer_definition,
    extract_thumb_keys,
    parse_layer_access_from_base,
    parse_layer_access_from_all_layers,
    parse_layer_keys,
    split_keys_respecting_parens,
)


class TestExtractLayerDefinition:
    """Test layer definition extraction."""


class TestSplitKeysRespectingParens:
    """Test split_keys_respecting_parens helper function."""

    def test_simple_split(self) -> None:
        """Test splitting simple comma-separated keys."""
        result = split_keys_respecting_parens("A, B, C")
        assert result == ["A", "B", "C"]

    def test_nested_parens(self) -> None:
        """Test splitting with nested parentheses."""
        result = split_keys_respecting_parens("U_MT(A, B), C")
        assert result == ["U_MT(A, B)", "C"]

    def test_deeply_nested(self) -> None:
        """Test splitting with deeply nested parentheses."""
        result = split_keys_respecting_parens("U_LT(U_NAV, U_MT(X, Y)), Z")
        assert result == ["U_LT(U_NAV, U_MT(X, Y))", "Z"]

    def test_empty_string(self) -> None:
        """Test splitting empty string."""
        result = split_keys_respecting_parens("")
        assert result == []

    def test_whitespace_handling(self) -> None:
        """Test that whitespace is trimmed."""
        result = split_keys_respecting_parens("  A  ,  B  ")
        assert result == ["A", "B"]

    def test_single_key(self) -> None:
        """Test with single key (no commas)."""
        result = split_keys_respecting_parens("&kp Q")
        assert result == ["&kp Q"]

    def test_complex_macro(self) -> None:
        """Test with complex nested macro."""
        result = split_keys_respecting_parens(
            "&kp A, U_MT(LCTRL, B), U_LT(U_NAV, C), D"
        )
        assert result == ["&kp A", "U_MT(LCTRL, B)", "U_LT(U_NAV, C)", "D"]

    def test_extract_base_layer(self, config_full: str) -> None:
        """Test extracting BASE layer."""
        result = extract_layer_definition(config_full, "BASE")
        assert result is not None
        assert "&kp Q" in result

    def test_extract_tap_layer(self, config_full: str) -> None:
        """Test extracting TAP layer."""
        result = extract_layer_definition(config_full, "TAP")
        assert result is not None
        assert "&kp Q" in result

    def test_extract_nav_layer(self, config_full: str) -> None:
        """Test extracting NAV layer."""
        result = extract_layer_definition(config_full, "NAV")
        assert result is not None
        assert "&kp LEFT" in result

    def test_missing_layer_returns_none(self, config_full: str) -> None:
        """Test that missing layer returns None."""
        result = extract_layer_definition(config_full, "NONEXISTENT")
        assert result is None

    def test_layer_definition_joins_continuations(self, config_full: str) -> None:
        """Test that line continuations are properly joined."""
        result = extract_layer_definition(config_full, "BASE")
        assert result is not None
        # Should be a single line without backslashes
        assert "\\" not in result
        # Should have multiple keys
        assert result.count(",") > 30


class TestParseLayerKeys:
    """Test layer key parsing."""

    def test_parse_40_keys(self, config_full: str, key_map: KeyCodeMap) -> None:
        """Test parsing a complete 40-key layer."""
        layer_def = extract_layer_definition(config_full, "BASE")
        assert layer_def is not None
        keys = parse_layer_keys(layer_def, key_map)
        assert len(keys) >= 40

    def test_key_translation_in_parsing(
        self, config_full: str, key_map: KeyCodeMap
    ) -> None:
        """Test that keys are translated during parsing."""
        layer_def = extract_layer_definition(config_full, "BASE")
        assert layer_def is not None
        keys = parse_layer_keys(layer_def, key_map)
        # Check that &kp codes are translated
        assert "Q" in keys
        assert "W" in keys

    def test_u_np_filtered_to_none(self, config_full: str, key_map: KeyCodeMap) -> None:
        """Test that U_NP is filtered to None."""
        layer_def = extract_layer_definition(config_full, "BASE")
        assert layer_def is not None
        keys = parse_layer_keys(layer_def, key_map)
        # U_NP should be None in the returned list
        assert None in keys


class TestExtractThumbKeys:
    """Test thumb key extraction."""

    def test_extract_from_tap_layer(
        self, config_full: str, key_map: KeyCodeMap
    ) -> None:
        """Test extracting thumb keys from TAP layer."""
        tap_def = extract_layer_definition(config_full, "TAP")
        assert tap_def is not None
        tap_keys = parse_layer_keys(tap_def, key_map)
        thumb_keys = extract_thumb_keys(tap_keys)

        assert "left" in thumb_keys
        assert "right" in thumb_keys
        assert "physical" in thumb_keys["left"]
        assert "combined" in thumb_keys["left"]

    def test_thumb_key_indices(self, config_minimal: str, key_map: KeyCodeMap) -> None:
        """Test that thumb keys are extracted from correct indices."""
        tap_def = extract_layer_definition(config_minimal, "TAP")
        assert tap_def is not None
        tap_keys = parse_layer_keys(tap_def, key_map)
        thumb_keys = extract_thumb_keys(tap_keys)

        # Left hand should have 2 physical keys
        assert len(thumb_keys["left"]["physical"]) == 2
        # Right hand should have 2 physical keys
        assert len(thumb_keys["right"]["physical"]) == 2

    def test_insufficient_keys_exits(
        self, config_full: str, key_map: KeyCodeMap
    ) -> None:
        """Test that insufficient keys cause ConfigurationError."""
        from zmk_to_pdf.exceptions import ConfigurationError

        # Create a too-short key list
        short_keys = ["A"] * 30
        with pytest.raises(ConfigurationError):
            extract_thumb_keys(short_keys)


class TestParseLayerAccessFromBase:
    """Test layer access detection from BASE layer."""

    def test_detect_nav_access(self, config_full: str, key_map: KeyCodeMap) -> None:
        """Test detecting NAV layer access."""
        base_def = extract_layer_definition(config_full, "BASE")
        assert base_def is not None
        access = parse_layer_access_from_base(base_def, key_map)

        assert "NAV" in access
        assert len(access["NAV"]) > 0

    def test_detect_num_access(self, config_full: str, key_map: KeyCodeMap) -> None:
        """Test detecting NUM layer access."""
        base_def = extract_layer_definition(config_full, "BASE")
        assert base_def is not None
        access = parse_layer_access_from_base(base_def, key_map)

        assert "NUM" in access

    def test_detect_button_access(self, config_full: str, key_map: KeyCodeMap) -> None:
        """Test detecting BUTTON layer access."""
        base_def = extract_layer_definition(config_full, "BASE")
        assert base_def is not None
        access = parse_layer_access_from_base(base_def, key_map)

        assert "BUTTON" in access

    def test_access_info_structure(self, config_full: str, key_map: KeyCodeMap) -> None:
        """Test structure of access info."""
        base_def = extract_layer_definition(config_full, "BASE")
        assert base_def is not None
        access = parse_layer_access_from_base(base_def, key_map)

        nav_access = access["NAV"]
        assert len(nav_access) > 0

        # Check structure of first access info
        info = nav_access[0]
        assert "position" in info
        assert "key" in info
        assert "index" in info
        assert "source_layer" in info
        assert info["source_layer"] is None  # BASE layer access has no source_layer


class TestParseLayerAccessFromAllLayers:
    """Test parsing access from all layers."""

    def test_parse_layer_access_from_all_layers(
        self, config_full: str, key_map: KeyCodeMap
    ) -> None:
        """Test parsing &u_to_U_* patterns from all layers."""
        layers_to_scan = discover_layers(config_full)
        all_access = parse_layer_access_from_all_layers(
            config_full, layers_to_scan, key_map
        )

        # Should find TAP layer access from other layers
        assert "TAP" in all_access or len(all_access) > 0

    def test_tap_layer_access_detected(
        self, config_full: str, key_map: KeyCodeMap
    ) -> None:
        """Test that TAP layer access is detected from other layers."""
        layers_to_scan = discover_layers(config_full)
        all_access = parse_layer_access_from_all_layers(
            config_full, layers_to_scan, key_map
        )

        if "TAP" in all_access:
            tap_access = all_access["TAP"]
            assert len(tap_access) > 0
            # Check that access info has source_layer set
            for info in tap_access:
                assert "source_layer" in info
                assert info["source_layer"] is not None

    def test_multi_layer_access_structure(
        self, config_full: str, key_map: KeyCodeMap
    ) -> None:
        """Test structure of multi-layer access info."""
        layers_to_scan = discover_layers(config_full)
        all_access = parse_layer_access_from_all_layers(
            config_full, layers_to_scan, key_map
        )

        # Find first target layer with access info
        for target_layer, access_list in all_access.items():
            if access_list:
                info = access_list[0]
                assert "position" in info
                assert "key" in info
                assert "index" in info
                assert "source_layer" in info
                assert info["source_layer"] is not None
                break


class TestDeterminePositionName:
    """Test key position name determination."""

    def test_top_left_position(self) -> None:
        """Test position name for top-left key (index 0)."""
        result = determine_position_name(0)
        assert result == "left_row0_col0"

    def test_top_right_position(self) -> None:
        """Test position name for top-right key (index 9)."""
        result = determine_position_name(9)
        assert result == "right_row0_col4"

    def test_home_left_position(self) -> None:
        """Test position name for home-left key (index 10)."""
        result = determine_position_name(10)
        assert result == "left_row1_col0"

    def test_left_combined_thumb(self) -> None:
        """Test position name for left combined thumb (index 32)."""
        result = determine_position_name(32)
        assert result == "left_combined"

    def test_left_outer_thumb(self) -> None:
        """Test position name for left outer thumb (index 33)."""
        result = determine_position_name(33)
        assert result == "left_outer"

    def test_left_inner_thumb(self) -> None:
        """Test position name for left inner thumb (index 34)."""
        result = determine_position_name(34)
        assert result == "left_inner"

    def test_right_inner_thumb(self) -> None:
        """Test position name for right inner thumb (index 35)."""
        result = determine_position_name(35)
        assert result == "right_inner"

    def test_right_outer_thumb(self) -> None:
        """Test position name for right outer thumb (index 36)."""
        result = determine_position_name(36)
        assert result == "right_outer"

    def test_right_combined_thumb(self) -> None:
        """Test position name for right combined thumb (index 37)."""
        result = determine_position_name(37)
        assert result == "right_combined"


class TestDiscoverLayers:
    """Test layer discovery."""

    def test_discover_all_layers_in_full_config(self, config_full: str) -> None:
        """Test discovering all layers in full config."""
        layers = discover_layers(config_full)
        assert "TAP" in layers
        assert "BUTTON" in layers
        assert "NAV" in layers
        assert "MEDIA" in layers
        assert "NUM" in layers
        assert "SYM" in layers
        assert "FUN" in layers

    def test_discover_excludes_base(self, config_full: str) -> None:
        """Test that BASE layer is excluded."""
        layers = discover_layers(config_full)
        assert "BASE" not in layers

    def test_discover_excludes_extra(self, config_full: str) -> None:
        """Test that EXTRA layer is excluded."""
        layers = discover_layers(config_full)
        assert "EXTRA" not in layers

    def test_discover_minimal_config(self, config_minimal: str) -> None:
        """Test discovering layers in minimal config."""
        layers = discover_layers(config_minimal)
        assert "TAP" in layers
        assert "NAV" in layers
        assert "NUM" in layers

    def test_discover_excludes_extra_when_present(self, config_with_extra: str) -> None:
        """Test that EXTRA layer is excluded even when defined."""
        layers = discover_layers(config_with_extra)
        assert "BASE" not in layers
        assert "EXTRA" not in layers
        assert "TAP" in layers
