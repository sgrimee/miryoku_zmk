"""Data structures and type definitions for ZMK Layout PDF Generator."""

from dataclasses import dataclass
from typing import TypedDict


@dataclass
class LayoutDimensions:
    """Calculated dimensions for keyboard layout rendering.

    All dimensions are in inches. This dataclass encapsulates all the
    geometric calculations needed to position keys on the PDF.
    """

    key_width: float
    key_height: float
    key_spacing: float
    hand_gap: float
    thumb_spacing: float
    hand_width: float
    total_width: float
    left_hand_x: float
    right_hand_x: float
    keys_start_y: float
    first_row_y: float
    physical_thumb_y: float
    combined_thumb_y: float


class ThumbKeysDict(TypedDict):
    """Physical and combined thumb key structure."""

    physical: list[str | None]
    combined: str | None


class ThumbKeysActive(TypedDict):
    """Active thumb keys for a layer."""

    physical: list[str | None]
    combined: str | None
    active: str | int | None


class LayerAccessInfo(TypedDict):
    """Information about how a layer is accessed."""

    position: str
    key: str
    index: int
    source_layer: str | None  # None for BASE access, layer name for other layers


class LayerData(TypedDict):
    """Complete layer structure for rendering."""

    left_hand: list[list[str | None]]
    right_hand: list[list[str | None]]
    left_thumbs: ThumbKeysActive
    right_thumbs: ThumbKeysActive
    access: str


class ThumbKeyLabelDict(TypedDict):
    """Thumb key labels from a layer."""

    physical: list[str | None]
    combined: str | None
