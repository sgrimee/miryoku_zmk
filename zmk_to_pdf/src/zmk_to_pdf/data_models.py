"""Data structures and type definitions for ZMK Layout PDF Generator."""

from typing import TypedDict


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
