"""Tests for main module."""

from pathlib import Path

import pytest

from zmk_to_pdf.main import parse_layout_config, build_all_layers


class TestParseLayoutConfig:
    """Test parse_layout_config() function."""

    def test_parse_layout_config_minimal(
        self, config_minimal: str, tmp_path: Path
    ) -> None:
        """Test parsing a minimal config file."""
        # Write config to temp file
        config_file = tmp_path / "custom_config.h"
        config_file.write_text(config_minimal)

        # Parse the config
        parsed = parse_layout_config(config_file)

        # Verify parsed layout
        assert parsed.layout in ["34key", "36key", "40key", "unknown"]
        assert len(parsed.layers_to_display) > 0
        assert len(parsed.layers) > 0
        # Minimal config has TAP, NAV, NUM layers
        assert "TAP" in parsed.layers_to_display or "BASE" in parsed.layers_to_display

    def test_parse_layout_config_full(self, config_full: str, tmp_path: Path) -> None:
        """Test parsing a full config file with multiple layers."""
        # Write config to temp file
        config_file = tmp_path / "custom_config.h"
        config_file.write_text(config_full)

        # Parse the config
        parsed = parse_layout_config(config_file)

        # Verify parsed layout
        assert parsed.layout in ["34key", "36key", "40key", "unknown"]
        assert len(parsed.layers_to_display) > 0
        assert len(parsed.layers) > 0
        assert parsed.content == config_full

    def test_parse_layout_config_returns_parsed_layout_dataclass(
        self, config_minimal: str, tmp_path: Path
    ) -> None:
        """Test that parse_layout_config returns a ParsedLayout dataclass."""
        from zmk_to_pdf.data_models import ParsedLayout

        # Write config to temp file
        config_file = tmp_path / "custom_config.h"
        config_file.write_text(config_minimal)

        # Parse the config
        parsed = parse_layout_config(config_file)

        # Verify it's a ParsedLayout instance
        assert isinstance(parsed, ParsedLayout)
        assert hasattr(parsed, "content")
        assert hasattr(parsed, "layout")
        assert hasattr(parsed, "layers_to_display")
        assert hasattr(parsed, "layer_access")
        assert hasattr(parsed, "all_layer_access")
        assert hasattr(parsed, "layers")


class TestBuildAllLayers:
    """Test build_all_layers() function."""

    def test_build_all_layers_basic(self, config_full: str) -> None:
        """Test building all layers from config content."""
        from zmk_to_pdf.parser import (
            detect_keyboard_layout,
            discover_layers,
            extract_layer_definition,
            parse_config_file,
            parse_layer_access_from_base,
            parse_layer_access_from_all_layers,
        )
        from zmk_to_pdf.key_code_map import KeyCodeMap

        # Parse the config
        key_map = KeyCodeMap()
        content = config_full
        layout = detect_keyboard_layout(content)
        layers_to_display = discover_layers(content)

        # Get access info
        base_def = extract_layer_definition(content, "BASE")
        layer_access = parse_layer_access_from_base(base_def, key_map, layout)
        all_layer_access = parse_layer_access_from_all_layers(
            content, layers_to_display, key_map, layout
        )

        # Build layers
        layers = build_all_layers(
            content, layers_to_display, layer_access, all_layer_access
        )

        # Verify layers were built
        assert len(layers) > 0
        for layer_name in layers:
            assert layer_name in layers_to_display

    def test_build_all_layers_returns_dict(self, config_minimal: str) -> None:
        """Test that build_all_layers returns a dictionary of LayerData."""
        from zmk_to_pdf.parser import (
            detect_keyboard_layout,
            discover_layers,
            extract_layer_definition,
            parse_config_file,
            parse_layer_access_from_base,
            parse_layer_access_from_all_layers,
        )
        from zmk_to_pdf.key_code_map import KeyCodeMap

        # Parse the config
        key_map = KeyCodeMap()
        content = config_minimal
        layout = detect_keyboard_layout(content)
        layers_to_display = discover_layers(content)

        # Get access info
        base_def = extract_layer_definition(content, "BASE")
        layer_access = parse_layer_access_from_base(base_def, key_map, layout)
        all_layer_access = parse_layer_access_from_all_layers(
            content, layers_to_display, key_map, layout
        )

        # Build layers
        layers = build_all_layers(
            content, layers_to_display, layer_access, all_layer_access
        )

        # Verify return type
        assert isinstance(layers, dict)
        # Each layer should have LayerData structure
        for layer_name, layer_data in layers.items():
            assert "left_hand" in layer_data
            assert "right_hand" in layer_data
            assert "left_thumbs" in layer_data
            assert "right_thumbs" in layer_data
            assert "access" in layer_data
