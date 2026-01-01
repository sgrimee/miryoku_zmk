"""Pytest configuration and shared fixtures."""

from pathlib import Path

import pytest

from zmk_to_pdf.config import PDFConfig
from zmk_to_pdf.data_models import LayerData, ThumbKeysActive
from zmk_to_pdf.key_code_map import KeyCodeMap


@pytest.fixture
def key_map() -> KeyCodeMap:
    """Load key code mapping from YAML."""
    return KeyCodeMap()


@pytest.fixture
def pdf_config() -> PDFConfig:
    """Create a default PDF configuration."""
    return PDFConfig()


@pytest.fixture
def config_full() -> str:
    """Load full test configuration with all 8 layers."""
    config_path = Path(__file__).parent / "fixtures" / "custom_config_full.h"
    return config_path.read_text(encoding="utf-8")


@pytest.fixture
def config_minimal() -> str:
    """Load minimal test configuration with 4 layers."""
    config_path = Path(__file__).parent / "fixtures" / "custom_config_minimal.h"
    return config_path.read_text(encoding="utf-8")


@pytest.fixture
def config_edge_cases() -> str:
    """Load edge case test configuration."""
    config_path = Path(__file__).parent / "fixtures" / "custom_config_edge_cases.h"
    return config_path.read_text(encoding="utf-8")


@pytest.fixture
def config_with_extra() -> str:
    """Load test configuration with EXTRA layer."""
    config_path = Path(__file__).parent / "fixtures" / "custom_config_with_extra.h"
    return config_path.read_text(encoding="utf-8")


@pytest.fixture
def sample_layer_data() -> LayerData:
    """Create sample layer data for rendering tests."""
    return LayerData(
        left_hand=[
            ["Q", "W", "E", "R", "T"],
            ["A", "S", "D", "F", "G"],
            ["Z", "X", "C", "V", "B"],
        ],
        right_hand=[
            ["Y", "U", "I", "O", "P"],
            ["H", "J", "K", "L", "'"],
            ["N", "M", ",", ".", "/"],
        ],
        left_thumbs=ThumbKeysActive(
            physical=["Z", "X"],
            combined="C",
            active=None,
        ),
        right_thumbs=ThumbKeysActive(
            physical=["V", "B"],
            combined="N",
            active=None,
        ),
        access="Hold ESC (left inner)",
    )


@pytest.fixture
def temp_pdf_path(tmp_path: Path) -> Path:
    """Create a temporary path for PDF output."""
    return tmp_path / "test_output.pdf"
