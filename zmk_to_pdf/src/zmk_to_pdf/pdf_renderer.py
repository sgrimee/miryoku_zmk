"""PDF rendering and drawing operations."""

from reportlab.lib.colors import HexColor, black
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

from .config import PDFConfig
from .data_models import LayerData
from .key_code_map import KeyColorizer


class PDFRenderer:
    """Handles all PDF rendering operations."""

    def __init__(self, config: PDFConfig) -> None:
        """Initialize renderer with configuration.

        Args:
            config: PDFConfig instance
        """
        self.config = config
        self.colorizer = KeyColorizer(config)

    def draw_key(
        self,
        pdf: canvas.Canvas,
        x: float,
        y: float,
        text: str | None,
        is_combined: bool = False,
        is_inactive: bool = False,
        is_access_key: bool = False,
    ) -> None:
        """Draw a single key.

        Args:
            pdf: Canvas to draw on
            x: X coordinate
            y: Y coordinate
            text: Key label text
            is_combined: True for combined thumb keys (red dashed border)
            is_inactive: True for grayed out keys (not relevant for current layer)
            is_access_key: True if this key is used to access the current layer
        """
        # Normalize None to dash
        if text is None:
            text = "-"

        # Get colors - if it's an access key, override with system color (yellow)
        if is_access_key and not is_inactive:
            bg_color = HexColor(self.config.color_system)
            text_color = black
        else:
            bg_color, text_color = self.colorizer.get_colors(text, is_inactive)

        # Draw key background
        pdf.setFillColor(bg_color)
        border_color = black if not is_inactive else HexColor("#CCCCCC")
        pdf.setStrokeColor(border_color)
        pdf.setLineWidth(0.5)
        # Convert dimensions to inches
        key_width_inch = self.config.key_width * inch
        key_height_inch = self.config.key_height * inch
        pdf.rect(x, y, key_width_inch, key_height_inch, fill=1)

        # Add red dashed border for combined thumb keys (active ones)
        if is_combined and not is_inactive:
            pdf.setLineWidth(1)
            pdf.setStrokeColor(HexColor(self.config.color_combined_border))
            pdf.setDash(2, 2)
            pdf.rect(x, y, key_width_inch, key_height_inch, fill=0)
            pdf.setDash()

        # Draw text
        pdf.setFont("Helvetica-Bold", self.config.key_font_size)
        pdf.setFillColor(text_color)

        # Center text
        text_width = pdf.stringWidth(text, "Helvetica-Bold", self.config.key_font_size)
        text_x = x + (key_width_inch - text_width) / 2
        text_y = y + (key_height_inch - self.config.key_font_size) / 2
        pdf.drawString(text_x, text_y, text)

    def draw_layer_section(
        self,
        pdf: canvas.Canvas,
        layer_name: str,
        layer_data: LayerData,
        y_offset: float,
        page_width: float,
    ) -> None:
        """Draw a single layer section on a page.

        Args:
            pdf: Canvas to draw on
            layer_name: Name of the layer
            layer_data: Layer data structure
            y_offset: Y coordinate for section start
            page_width: Total page width
        """
        # Calculate positions
        left_hand = layer_data["left_hand"]
        right_hand = layer_data["right_hand"]

        # Convert dimensions to inches
        key_width_inch = self.config.key_width * inch
        key_height_inch = self.config.key_height * inch
        key_spacing_inch = self.config.key_spacing * inch
        hand_gap_inch = self.config.hand_gap * inch
        thumb_spacing_inch = self.config.thumb_spacing * inch

        # Total width needed for one hand (5 keys + 4 spacings)
        hand_width = 5 * key_width_inch + 4 * key_spacing_inch
        # Total width for both hands with proper gap
        total_width = 2 * hand_width + hand_gap_inch

        # Center the keyboard layout horizontally on the page
        page_center = page_width / 2
        left_hand_x = page_center - total_width / 2
        right_hand_x = left_hand_x + hand_width + hand_gap_inch

        # Reset fill color to black for text
        pdf.setFillColor(black)

        # Title above left hand keyboard
        pdf.setFont("Helvetica-Bold", self.config.layer_name_font_size)
        pdf.drawString(left_hand_x, y_offset, layer_name)

        # Access info above right hand keyboard (right-aligned)
        pdf.setFont("Helvetica-Bold", self.config.access_font_size)
        pdf.setFillColor(HexColor(self.config.color_access_text))
        access_text = f"Access: {layer_data['access']}"
        # Truncate access text if too long for right hand area
        max_access_width = hand_width - 0.1 * inch
        while (
            pdf.stringWidth(access_text, "Helvetica-Bold", self.config.access_font_size)
            > max_access_width
            and len(access_text) > 15
        ):
            access_text = access_text[:-4] + "..."
        access_width = pdf.stringWidth(
            access_text, "Helvetica-Bold", self.config.access_font_size
        )
        pdf.drawString(right_hand_x + hand_width - access_width, y_offset, access_text)
        pdf.setFillColor(black)

        # Content area y positions - start keys below the title
        keys_start_y = y_offset - 0.45 * inch
        first_row_y = keys_start_y

        # Draw left hand regular keys (3 rows of 5 keys)
        for row_idx, row in enumerate(left_hand):
            y = first_row_y - (row_idx * (key_height_inch + key_spacing_inch))
            for col_idx, key in enumerate(row):
                x = left_hand_x + col_idx * (key_width_inch + key_spacing_inch)
                self.draw_key(pdf, x, y, key)

        # Calculate thumb row y positions (below finger keys)
        physical_thumb_y = (
            first_row_y
            - (3 * (key_height_inch + key_spacing_inch))
            - thumb_spacing_inch
        )
        combined_thumb_y = physical_thumb_y - (key_height_inch + thumb_spacing_inch)

        # Draw left hand thumb keys
        left_thumbs = layer_data["left_thumbs"]
        left_active = left_thumbs.get("active")

        # Draw physical thumb keys (aligned to interior = columns 3-4)
        for idx, key in enumerate(left_thumbs["physical"]):
            col_offset = 3 + idx  # Columns 3 and 4
            x = left_hand_x + col_offset * (key_width_inch + key_spacing_inch)
            # A key is inactive only if it has no keycode (dash or None)
            is_inactive = key is None or key == "-"
            is_access_key = (
                left_active == idx
            )  # This is an access key if it's the active one
            self.draw_key(
                pdf,
                x,
                physical_thumb_y,
                key,
                is_inactive=is_inactive,
                is_access_key=is_access_key,
            )

        # Draw combined thumb key (centered under physical thumbs)
        x = (
            left_hand_x
            + 3 * (key_width_inch + key_spacing_inch)
            + (key_width_inch + key_spacing_inch) / 2
        )
        combined_key = left_thumbs["combined"]
        # A key is inactive only if it has no keycode (dash or None)
        is_inactive = combined_key is None or combined_key == "-"
        is_access_key = (
            left_active == "combined"
        )  # This is an access key if it's the active one
        self.draw_key(
            pdf,
            x,
            combined_thumb_y,
            combined_key,
            is_combined=True,
            is_inactive=is_inactive,
            is_access_key=is_access_key,
        )

        # Draw right hand regular keys (3 rows of 5 keys)
        for row_idx, row in enumerate(right_hand):
            y = first_row_y - (row_idx * (key_height_inch + key_spacing_inch))
            for col_idx, key in enumerate(row):
                x = right_hand_x + col_idx * (key_width_inch + key_spacing_inch)
                self.draw_key(pdf, x, y, key)

        # Draw right hand thumb keys
        right_thumbs = layer_data["right_thumbs"]
        right_active = right_thumbs.get("active")

        # Draw physical thumb keys (aligned to interior = columns 0-1)
        for idx, key in enumerate(right_thumbs["physical"]):
            col_offset = idx  # Columns 0 and 1
            x = right_hand_x + col_offset * (key_width_inch + key_spacing_inch)
            # A key is inactive only if it has no keycode (dash or None)
            is_inactive = key is None or key == "-"
            is_access_key = (
                right_active == idx
            )  # This is an access key if it's the active one
            self.draw_key(
                pdf,
                x,
                physical_thumb_y,
                key,
                is_inactive=is_inactive,
                is_access_key=is_access_key,
            )

        # Draw combined thumb key (centered under physical thumbs)
        x = right_hand_x + (key_width_inch + key_spacing_inch) / 2
        combined_key = right_thumbs["combined"]
        # A key is inactive only if it has no keycode (dash or None)
        is_inactive = combined_key is None or combined_key == "-"
        is_access_key = (
            right_active == "combined"
        )  # This is an access key if it's the active one
        self.draw_key(
            pdf,
            x,
            combined_thumb_y,
            combined_key,
            is_combined=True,
            is_inactive=is_inactive,
            is_access_key=is_access_key,
        )
