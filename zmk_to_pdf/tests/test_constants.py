"""Tests for constants module."""

from zmk_to_pdf.constants import (
    LAYOUT_34_MAX_KEYS,
    LAYOUT_36_MAX_KEYS,
    LAYOUT_40_MAX_KEYS,
    MIN_FINGER_KEYS,
    MIN_KEYS_FOR_THUMBS,
)


def test_min_finger_keys_is_positive() -> None:
    """Verify MIN_FINGER_KEYS is a positive integer."""
    assert MIN_FINGER_KEYS > 0
    assert isinstance(MIN_FINGER_KEYS, int)


def test_min_keys_for_thumbs_is_positive() -> None:
    """Verify MIN_KEYS_FOR_THUMBS is a positive integer."""
    assert MIN_KEYS_FOR_THUMBS > 0
    assert isinstance(MIN_KEYS_FOR_THUMBS, int)


def test_min_keys_for_thumbs_greater_than_finger_keys() -> None:
    """Verify MIN_KEYS_FOR_THUMBS includes all finger keys plus thumbs."""
    assert MIN_KEYS_FOR_THUMBS > MIN_FINGER_KEYS


def test_layout_max_keys_are_positive() -> None:
    """Verify all layout max keys are positive integers."""
    assert LAYOUT_34_MAX_KEYS > 0
    assert LAYOUT_36_MAX_KEYS > 0
    assert LAYOUT_40_MAX_KEYS > 0
    assert isinstance(LAYOUT_34_MAX_KEYS, int)
    assert isinstance(LAYOUT_36_MAX_KEYS, int)
    assert isinstance(LAYOUT_40_MAX_KEYS, int)


def test_layout_max_keys_are_ordered() -> None:
    """Verify layout max keys are in ascending order."""
    assert LAYOUT_34_MAX_KEYS < LAYOUT_36_MAX_KEYS
    assert LAYOUT_36_MAX_KEYS < LAYOUT_40_MAX_KEYS


def test_min_keys_for_thumbs_fits_in_40key_layout() -> None:
    """Verify MIN_KEYS_FOR_THUMBS fits within the largest layout."""
    assert MIN_KEYS_FOR_THUMBS <= LAYOUT_40_MAX_KEYS
