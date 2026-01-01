"""Tests for data models and type definitions."""

from zmk_to_pdf.data_models import (
    LayerAccessInfo,
    LayerData,
    ThumbKeysActive,
    ThumbKeysDict,
)


class TestThumbKeysDict:
    """Test ThumbKeysDict TypedDict."""

    def test_create_thumb_keys_dict(self) -> None:
        """Test creating a ThumbKeysDict."""
        thumb_keys: ThumbKeysDict = {
            "physical": ["A", "B"],
            "combined": "C",
        }
        assert thumb_keys["physical"] == ["A", "B"]
        assert thumb_keys["combined"] == "C"

    def test_thumb_keys_dict_with_none(self) -> None:
        """Test ThumbKeysDict with None values."""
        thumb_keys: ThumbKeysDict = {
            "physical": [None, "A"],
            "combined": None,
        }
        assert thumb_keys["physical"][0] is None
        assert thumb_keys["combined"] is None


class TestThumbKeysActive:
    """Test ThumbKeysActive TypedDict."""

    def test_create_thumb_keys_active(self) -> None:
        """Test creating a ThumbKeysActive."""
        thumb_keys: ThumbKeysActive = {
            "physical": ["A", "B"],
            "combined": "C",
            "active": 0,
        }
        assert thumb_keys["active"] == 0

    def test_thumb_keys_active_with_combined(self) -> None:
        """Test ThumbKeysActive with combined as active."""
        thumb_keys: ThumbKeysActive = {
            "physical": ["A", "B"],
            "combined": "C",
            "active": "combined",
        }
        assert thumb_keys["active"] == "combined"

    def test_thumb_keys_active_with_none(self) -> None:
        """Test ThumbKeysActive with None as active."""
        thumb_keys: ThumbKeysActive = {
            "physical": ["A", "B"],
            "combined": "C",
            "active": None,
        }
        assert thumb_keys["active"] is None


class TestLayerAccessInfo:
    """Test LayerAccessInfo TypedDict."""

    def test_create_layer_access_info(self) -> None:
        """Test creating LayerAccessInfo."""
        access: LayerAccessInfo = {
            "position": "left_inner",
            "key": "TAB",
            "index": 34,
            "source_layer": None,
        }
        assert access["position"] == "left_inner"
        assert access["key"] == "TAB"
        assert access["index"] == 34
        assert access["source_layer"] is None


class TestLayerData:
    """Test LayerData TypedDict."""

    def test_create_layer_data(self, sample_layer_data: LayerData) -> None:
        """Test creating LayerData."""
        assert len(sample_layer_data["left_hand"]) == 3
        assert len(sample_layer_data["right_hand"]) == 3
        assert "left_thumbs" in sample_layer_data
        assert "right_thumbs" in sample_layer_data
        assert "access" in sample_layer_data

    def test_layer_data_with_none_keys(self) -> None:
        """Test LayerData with None values."""
        layer_data: LayerData = {
            "left_hand": [[None, "A", None, "B", None]],
            "right_hand": [[None, "C", None, "D", None]],
            "left_thumbs": ThumbKeysActive(
                physical=[None, None],
                combined=None,
                active=None,
            ),
            "right_thumbs": ThumbKeysActive(
                physical=[None, None],
                combined=None,
                active=None,
            ),
            "access": "Hold X / Y",
        }
        assert layer_data["left_hand"][0][0] is None
        assert layer_data["left_hand"][0][1] == "A"
