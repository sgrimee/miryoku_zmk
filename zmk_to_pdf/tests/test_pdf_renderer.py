"""Tests for PDF rendering."""

import pytest
from pathlib import Path
from reportlab.pdfgen import canvas

from zmk_to_pdf.config import PDFConfig
from zmk_to_pdf.pdf_renderer import PDFRenderer


class TestPDFRenderer:
    """Test PDF rendering functionality."""

    def test_renderer_initialization(self, pdf_config: PDFConfig) -> None:
        """Test creating a PDFRenderer."""
        renderer = PDFRenderer(pdf_config)
        assert renderer.config == pdf_config
        assert renderer.colorizer is not None

    def test_draw_key_creates_canvas_calls(
        self, pdf_config: PDFConfig, tmp_path: Path
    ) -> None:
        """Test drawing a key (integration test)."""
        renderer = PDFRenderer(pdf_config)
        pdf_path = tmp_path / "test_draw.pdf"
        pdf = canvas.Canvas(str(pdf_path))

        # Draw a simple key
        renderer.draw_key(pdf, 0, 0, "A")

        # Key should have been drawn (canvas has methods called)
        # We can't easily verify drawing without parsing PDF, so we just check it doesn't crash
        pdf.showPage()
        pdf.save()

        # Verify PDF was created
        assert pdf_path.exists()

    def test_draw_key_with_combined_flag(
        self, pdf_config: PDFConfig, tmp_path: Path
    ) -> None:
        """Test drawing a combined thumb key."""
        renderer = PDFRenderer(pdf_config)
        pdf_path = tmp_path / "test_combined.pdf"
        pdf = canvas.Canvas(str(pdf_path))

        # Draw a combined thumb key
        renderer.draw_key(pdf, 0, 0, "A", is_combined=True)

        pdf.showPage()
        pdf.save()

        assert pdf_path.exists()

    def test_draw_key_with_inactive_flag(
        self, pdf_config: PDFConfig, tmp_path: Path
    ) -> None:
        """Test drawing an inactive key."""
        renderer = PDFRenderer(pdf_config)
        pdf_path = tmp_path / "test_inactive.pdf"
        pdf = canvas.Canvas(str(pdf_path))

        # Draw an inactive key
        renderer.draw_key(pdf, 0, 0, "A", is_inactive=True)

        pdf.showPage()
        pdf.save()

        assert pdf_path.exists()

    def test_draw_key_with_access_flag(
        self, pdf_config: PDFConfig, tmp_path: Path
    ) -> None:
        """Test drawing an access key."""
        renderer = PDFRenderer(pdf_config)
        pdf_path = tmp_path / "test_access.pdf"
        pdf = canvas.Canvas(str(pdf_path))

        # Draw an access key
        renderer.draw_key(pdf, 0, 0, "A", is_access_key=True)

        pdf.showPage()
        pdf.save()

        assert pdf_path.exists()

    def test_draw_none_key(self, pdf_config: PDFConfig, tmp_path: Path) -> None:
        """Test drawing a None/empty key."""
        renderer = PDFRenderer(pdf_config)
        pdf_path = tmp_path / "test_none.pdf"
        pdf = canvas.Canvas(str(pdf_path))

        # Draw a None key (should show as dash)
        renderer.draw_key(pdf, 0, 0, None)

        pdf.showPage()
        pdf.save()

        assert pdf_path.exists()

    def test_draw_layer_section(
        self, pdf_config: PDFConfig, sample_layer_data, tmp_path: Path
    ) -> None:
        """Test drawing a complete layer section."""
        from reportlab.lib.pagesizes import letter

        renderer = PDFRenderer(pdf_config)
        pdf_path = tmp_path / "test_layer.pdf"
        pdf = canvas.Canvas(str(pdf_path), pagesize=letter)
        width, height = letter

        # Draw a layer section
        renderer.draw_layer_section(pdf, "BASE", sample_layer_data, height / 2, width)

        pdf.showPage()
        pdf.save()

        assert pdf_path.exists()

    def test_draw_layer_section_with_multiple_sections(
        self, pdf_config: PDFConfig, sample_layer_data, tmp_path: Path
    ) -> None:
        """Test drawing multiple layer sections on one page."""
        from reportlab.lib.pagesizes import letter

        renderer = PDFRenderer(pdf_config)
        pdf_path = tmp_path / "test_multi_layer.pdf"
        pdf = canvas.Canvas(str(pdf_path), pagesize=letter)
        width, height = letter

        # Draw multiple layer sections
        for i in range(3):
            y_offset = height - (i * 300)
            renderer.draw_layer_section(
                pdf, f"LAYER_{i}", sample_layer_data, y_offset, width
            )

        pdf.showPage()
        pdf.save()

        assert pdf_path.exists()


class TestPDFRendererIntegration:
    """Integration tests for PDF rendering."""

    def test_full_pdf_generation(
        self, config_full: str, pdf_config: PDFConfig, tmp_path: Path
    ) -> None:
        """Integration test: generate full PDF from config."""
        from zmk_to_pdf.key_code_map import KeyCodeMap
        from zmk_to_pdf.layer_processor import build_layer_data, create_page_groupings
        from zmk_to_pdf.parser import (
            discover_layers,
            extract_layer_definition,
            extract_thumb_keys,
            parse_layer_access_from_base,
            parse_layer_keys,
        )
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas as pdf_canvas

        key_map = KeyCodeMap()
        content = config_full
        layers_to_display = discover_layers(content)

        if not layers_to_display:
            pytest.skip("No layers found in test config")

        base_def = extract_layer_definition(content, "BASE")
        assert base_def is not None
        layer_access = parse_layer_access_from_base(base_def, key_map)

        tap_def = extract_layer_definition(content, "TAP")
        if tap_def is None:
            tap_def = base_def

        tap_keys = parse_layer_keys(tap_def, key_map)
        extract_thumb_keys(tap_keys)  # Verify thumb keys can be extracted

        # Build layer data
        layers = {}
        for layer_name in layers_to_display:
            layer_def = extract_layer_definition(content, layer_name)
            if layer_def:
                keys = parse_layer_keys(layer_def, key_map)
                if len(keys) >= 30:
                    layers[layer_name] = build_layer_data(
                        layer_name, keys, layer_access
                    )

        if not layers:
            pytest.skip("No valid layers could be built")

        # Generate PDF
        pdf_path = tmp_path / "test_full.pdf"
        pdf = pdf_canvas.Canvas(str(pdf_path), pagesize=letter)
        width, height = letter

        renderer = PDFRenderer(pdf_config)
        page_groupings = create_page_groupings(list(layers.keys()))

        for page_num, page_layers in enumerate(page_groupings):
            pdf.setFont("Helvetica-Bold", pdf_config.title_font_size)
            pdf.drawString(
                pdf_config.margin_left * 72,
                height - pdf_config.margin_top * 72,
                "Test Layers",
            )

            y_start = (
                height
                - (
                    pdf_config.margin_top
                    + pdf_config.title_to_legend
                    + pdf_config.legend_to_keys
                )
                * 72
            )

            for section_idx, layer_name in enumerate(page_layers):
                if layer_name in layers:
                    layer_data = layers[layer_name]
                    y_offset = y_start - (section_idx * pdf_config.section_height * 72)
                    renderer.draw_layer_section(
                        pdf, layer_name, layer_data, y_offset, width
                    )

            pdf.showPage()

        pdf.save()

        # Verify PDF was created
        assert pdf_path.exists()
        assert pdf_path.stat().st_size > 0
