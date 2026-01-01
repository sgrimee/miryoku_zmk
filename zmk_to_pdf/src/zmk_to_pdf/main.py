"""Main orchestration for ZMK Layout PDF generation."""

import sys
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from .config import PDFConfig
from .constants import MIN_FINGER_KEYS
from .data_models import ParsedLayout
from .exceptions import (
    ConfigurationError,
    LayerError,
    FileNotFoundError,
    InvalidArgumentError,
)
from .key_code_map import KeyCodeMap
from .layer_processor import build_layer_data, create_page_groupings
from .parser import (
    detect_keyboard_layout,
    discover_layers,
    extract_layer_definition,
    parse_config_file,
    parse_layer_keys,
    parse_layer_access_from_base,
    parse_layer_access_from_all_layers,
)
from .pdf_renderer import PDFRenderer


def build_all_layers(
    content: str,
    layers_to_display: list[str],
    layer_access: dict,
    all_layer_access: dict,
) -> dict:
    """Build layer data for all layers to display.

    Extracts layer definitions from config content, parses keys, validates
    layer has sufficient keys, and builds complete layer data structure for
    each layer.

    Args:
        content: Raw config file content
        layers_to_display: List of layer names to process
        layer_access: Access information from BASE layer
        all_layer_access: Multi-layer access patterns

    Returns:
        Dictionary mapping layer names to LayerData objects

    Raises:
        SystemExit: If no valid layers can be built
    """
    key_map = KeyCodeMap()
    layers = {}

    print("Building layer data...")
    for layer_name in layers_to_display:
        print(f"  Processing layer: {layer_name}")
        layer_def = extract_layer_definition(content, layer_name)
        if layer_def is None:
            print(f"  WARNING: Skipping {layer_name} - definition not found")
            continue

        keys = parse_layer_keys(layer_def, key_map)
        if len(keys) < MIN_FINGER_KEYS:
            print(
                f"  WARNING: Skipping {layer_name} - has {len(keys)} keys, expected at least {MIN_FINGER_KEYS}"
            )
            continue

        layers[layer_name] = build_layer_data(
            layer_name, keys, layer_access, all_layer_access
        )

    if not layers:
        raise LayerError("No valid layers found to display")

    return layers


def parse_layout_config(config_file: Path) -> ParsedLayout:
    """Parse keyboard layout configuration from a config file.

    Reads the config file, detects layout type, discovers layers, and parses
    all layer definitions to build complete layer data for rendering.

    Args:
        config_file: Path to custom_config.h file

    Returns:
        ParsedLayout object containing all parsed configuration data

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
        raise ConfigurationError("No layers found in config")

    # Parse BASE layer for access information
    print("Parsing BASE layer for access information...")
    base_def = extract_layer_definition(content, "BASE")
    if base_def is None:
        raise ConfigurationError("Could not find MIRYOKU_LAYER_BASE in config")
    layer_access = parse_layer_access_from_base(base_def, key_map, layout)

    # Parse all layers for &u_to_U_* patterns (multi-layer access)
    print("Parsing all layers for multi-layer access information...")
    all_layer_access = parse_layer_access_from_all_layers(
        content, layers_to_display, key_map, layout
    )

    # Build layer data for each layer
    layers = build_all_layers(
        content, layers_to_display, layer_access, all_layer_access
    )

    return ParsedLayout(
        content=content,
        layout=layout,
        layers_to_display=layers_to_display,
        layer_access=layer_access,
        all_layer_access=all_layer_access,
        layers=layers,
    )


def generate_pdf(config_file: Path, output_pdf: Path) -> None:
    """Generate PDF visualization from ZMK config file.

    Args:
        config_file: Path to custom_config.h file
        output_pdf: Path for output PDF file

    Raises:
        SystemExit: On configuration or parsing errors
    """
    # Parse layout configuration
    parsed = parse_layout_config(config_file)

    # Generate PDF
    print(f"Generating PDF: {output_pdf}")
    pdf = canvas.Canvas(str(output_pdf), pagesize=letter)
    width, height = letter

    # Create renderer with configuration
    config = PDFConfig()
    renderer = PDFRenderer(config)

    # Dynamically group layers into pages
    page_groupings = create_page_groupings(list(parsed.layers.keys()))
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
            if layer_name in parsed.layers:
                layer_data = parsed.layers[layer_name]
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
    try:
        # Check for command line arguments
        if len(sys.argv) < 2:
            raise InvalidArgumentError(
                "Usage: python -m zmk_to_pdf <config_file> [output_pdf]"
            )

        config_path = Path(sys.argv[1])
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        # Output PDF path - use second argument if provided, otherwise use current directory
        if len(sys.argv) >= 3:
            pdf_path = Path(sys.argv[2])
        else:
            pdf_path = Path.cwd() / "layout.pdf"

        generate_pdf(config_path, pdf_path)
    except (
        ConfigurationError,
        LayerError,
        FileNotFoundError,
        InvalidArgumentError,
    ) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"UNEXPECTED ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
