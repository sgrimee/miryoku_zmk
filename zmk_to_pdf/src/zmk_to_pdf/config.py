"""PDF rendering configuration and constants."""

from dataclasses import dataclass


@dataclass
class PDFConfig:
    """PDF rendering configuration and constants."""

    # Key dimensions (in inches)
    key_width: float = 0.60
    key_height: float = 0.34
    key_spacing: float = 0.03

    # Layout dimensions
    hand_gap: float = 0.40
    section_height: float = 2.25
    thumb_spacing: float = 0.04

    # Page layout
    title_font_size: int = 14
    layer_name_font_size: int = 16
    key_font_size: int = 9
    access_font_size: int = 8
    legend_font_size: int = 8
    page_number_font_size: int = 9

    # Margins
    margin_top: float = 0.35
    margin_left: float = 0.5
    margin_right: float = 1.0
    title_to_legend: float = 0.20
    legend_to_keys: float = 0.30

    # Key colors (hex codes)
    color_empty: str = "#CCCCCC"
    color_empty_text: str = "#999999"
    color_navigation: str = "#90EE90"
    color_modifier: str = "#FFB6C1"
    color_mouse_clipboard: str = "#87CEEB"
    color_system: str = "#F0E68C"
    color_regular: str = "#FFFFFF"
    color_layer_access: str = "#DDA0DD"
    color_inactive_bg: str = "#E8E8E8"
    color_inactive_text: str = "#AAAAAA"

    # Special colors
    color_text: str = "#000000"
    color_combined_border: str = "#FF0000"
    color_access_text: str = "#0066CC"
