"""Main orchestration for ZMK Layout PDF generation."""

import sys
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from .config import PDFConfig
from .key_code_map import KeyCodeMap
from .layer_processor import build_layer_data, create_page_groupings
from .parser import (
    detect_keyboard_layout,
    discover_layers,
    extract_layer_definition,
    extract_thumb_keys,
    parse_config_file,
    parse_layer_keys,
    parse_layer_access_from_base,
    parse_layer_access_from_all_layers,
)
from .pdf_renderer import PDFRenderer


def generate_pdf(config_file: Path, output_pdf: Path) -> None:
    """Generate PDF visualization from ZMK config file.

    Args:
        config_file: Path to custom_config.h file
        output_pdf: Path for output PDF file

    Raises:
        SystemExit: On configuration or parsing errors
    """
    # Load key codes from YAML
    key_map = KeyCodeMap()

    # Parse config file
    print(f"Reading config from {config_file}")
    content = parse_config_file(config_file)

    # Detect keyboard layout type
    layout = detect_keyboard_layout(content)
    print(f"Detected layout: {layout}")

    # Discover layers from config file
    layers_to_display = discover_layers(content)
    print(f"Discovered layers: {layers_to_display}")

    if not layers_to_display:
        sys.exit("ERROR: No layers found in config")

    # Parse BASE layer for access information
    print("Parsing BASE layer for access information...")
    base_def = extract_layer_definition(content, "BASE")
    if base_def is None:
        sys.exit("ERROR: Could not find MIRYOKU_LAYER_BASE in config")
    layer_access = parse_layer_access_from_base(base_def, key_map, layout)

    # Parse all layers for &u_to_U_* patterns (multi-layer access)
    print("Parsing all layers for multi-layer access information...")
    all_layer_access = parse_layer_access_from_all_layers(
        content, layers_to_display, key_map, layout
    )

    # Parse TAP layer for thumb key labels (fall back to BASE if TAP doesn't exist)
    print("Parsing thumb key labels...")
    tap_def = extract_layer_definition(content, "TAP")
    if tap_def is None:
        print("  TAP layer not found, falling back to BASE layer for thumb keys")
        tap_def = base_def

    tap_keys = parse_layer_keys(tap_def, key_map)
    if len(tap_keys) < 38:
        sys.exit(
            f"ERROR: Layer for thumb keys has {len(tap_keys)} keys, expected at least 38"
        )
    thumb_keys = extract_thumb_keys(tap_keys)

    # Build layer data for each layer
    print("Building layer data...")
    layers = {}
    for layer_name in layers_to_display:
        print(f"  Processing layer: {layer_name}")
        layer_def = extract_layer_definition(content, layer_name)
        if layer_def is None:
            print(f"  WARNING: Skipping {layer_name} - definition not found")
            continue

        keys = parse_layer_keys(layer_def, key_map)
        if len(keys) < 30:  # At least 30 finger keys expected
            print(
                f"  WARNING: Skipping {layer_name} - has {len(keys)} keys, expected at least 30"
            )
            continue

        layers[layer_name] = build_layer_data(
            layer_name, keys, layer_access, all_layer_access
        )

    if not layers:
        sys.exit("ERROR: No valid layers found to display")

    # Generate PDF
    print(f"Generating PDF: {output_pdf}")
    pdf = canvas.Canvas(str(output_pdf), pagesize=letter)
    width, height = letter

    # Create renderer with configuration
    config = PDFConfig()
    renderer = PDFRenderer(config)

    # Dynamically group layers into pages
    page_groupings = create_page_groupings(list(layers.keys()))
    print(f"Page groupings: {page_groupings}")

    total_pages = len(page_groupings)

    # Generate legend text - position-only (layout-agnostic)
    legend = "Legend: Yellow background = Layer access key | Red dashed border = Combined thumb key"

    for page_num, page_layers in enumerate(page_groupings):
        # Title on page
        pdf.setFont("Helvetica-Bold", config.title_font_size)
        pdf.drawString(
            config.margin_left * 72,  # Convert inches to points
            height - config.margin_top * 72,
            "Miryoku Keyboard Layers",
        )

        # Legend for thumb keys
        pdf.setFont("Helvetica", config.legend_font_size)
        pdf.drawString(
            config.margin_left * 72,
            height - (config.margin_top + config.title_to_legend) * 72,
            legend,
        )

        # Page number
        pdf.setFont("Helvetica", config.page_number_font_size)
        pdf.drawString(
            width - config.margin_right * 72,
            height - config.margin_top * 72,
            f"Page {page_num + 1}/{total_pages}",
        )

        y_start = height - (
            (config.margin_top + config.title_to_legend + config.legend_to_keys) * 72
        )

        for section_idx, layer_name in enumerate(page_layers):
            if layer_name in layers:
                layer_data = layers[layer_name]
                section_height_inch = config.section_height * 72
                y_offset = y_start - (section_idx * section_height_inch)
                renderer.draw_layer_section(
                    pdf, layer_name, layer_data, y_offset, width
                )

        pdf.showPage()

    pdf.save()
    print(f"PDF created: {output_pdf}")


def main() -> None:
    """Main entry point for PDF generation."""
    # Check for command line arguments
    if len(sys.argv) < 2:
        sys.exit("Usage: python -m zmk_to_pdf <config_file> [output_pdf]")

    config_path = Path(sys.argv[1])
    if not config_path.exists():
        sys.exit(f"ERROR: Config file not found: {config_path}")

    # Output PDF path - use second argument if provided, otherwise use current directory
    if len(sys.argv) >= 3:
        pdf_path = Path(sys.argv[2])
    else:
        pdf_path = Path.cwd() / "layout.pdf"

    generate_pdf(config_path, pdf_path)


if __name__ == "__main__":
    main()
