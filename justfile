# Miryoku ZMK firmware build commands

set shell := ["bash", "-c"]

# List all available recipes
default:
    @just --list --justfile {{justfile()}}

# Build main firmware (left + right halves with ZMK Studio)
build:
    nix build

# Build settings reset firmware (for Bluetooth bond issues)
build-reset:
    nix build .#settings-reset

# Flash main firmware via DFU serial (macOS) or USB drive (Linux)
flash:
    @if [[ "$(uname)" == "Darwin" ]]; then \
        echo "Flashing Aurora Sweep firmware via DFU serial (macOS)..."; \
        echo ""; \
        TMPDIR=$(mktemp -d); \
        echo "Creating DFU packages in $TMPDIR..."; \
        uv tool run adafruit-nrfutil dfu genpkg --dev-type 0x0052 --application result/zmk_left.hex "$TMPDIR/dfu_left.zip" && \
        uv tool run adafruit-nrfutil dfu genpkg --dev-type 0x0052 --application result/zmk_right.hex "$TMPDIR/dfu_right.zip" || { \
            echo "ERROR: Failed to create DFU packages"; \
            rm -rf "$TMPDIR"; \
            exit 1; \
        }; \
        echo ""; \
        echo "=== LEFT HALF ==="; \
        echo "1. Double-click the RESET button on the left half to enter DFU bootloader"; \
        read -p "2. Press Enter when ready to flash... " _; \
        LEFT_PORT=$(ls -t /dev/cu.usb* 2>/dev/null | head -1); \
        if [ -z "$LEFT_PORT" ]; then \
            echo "ERROR: No USB serial port found. Make sure left half is in bootloader mode."; \
            echo "Available ports: $(ls /dev/cu.usb* 2>/dev/null || echo 'none')"; \
            rm -rf "$TMPDIR"; \
            exit 1; \
        fi; \
        echo "Flashing to $LEFT_PORT..."; \
        uv tool run adafruit-nrfutil dfu serial --package "$TMPDIR/dfu_left.zip" -p "$LEFT_PORT" -b 115200 && \
        echo "✓ Left half flashed successfully"; \
        echo ""; \
        echo "=== RIGHT HALF ==="; \
        echo "1. Disconnect left half"; \
        echo "2. Connect right half to USB"; \
        echo "3. Double-click the RESET button on the right half to enter DFU bootloader"; \
        read -p "4. Press Enter when ready to flash... " _; \
        RIGHT_PORT=$(ls -t /dev/cu.usb* 2>/dev/null | head -1); \
        if [ -z "$RIGHT_PORT" ]; then \
            echo "ERROR: No USB serial port found. Make sure right half is in bootloader mode."; \
            echo "Available ports: $(ls /dev/cu.usb* 2>/dev/null || echo 'none')"; \
            rm -rf "$TMPDIR"; \
            exit 1; \
        fi; \
        echo "Flashing to $RIGHT_PORT..."; \
        uv tool run adafruit-nrfutil dfu serial --package "$TMPDIR/dfu_right.zip" -p "$RIGHT_PORT" -b 115200 && \
        echo "✓ Right half flashed successfully"; \
        echo ""; \
        rm -rf "$TMPDIR"; \
        echo "✓ Both halves flashed successfully!"; \
        echo "Your Aurora Sweep is ready to use."; \
    else \
        nix run .#flash; \
    fi

# Update ZMK/Zephyr versions and zephyrDepsHash
update:
    nix run .#update

# Enter development shell with west, cmake, ARM toolchain
shell:
    nix develop

# Open ZMK Studio in the default browser
studio:
    @echo "Opening ZMK Studio at https://zmk.studio"
    @echo ""
    @echo "Instructions:"
    @echo "1. Connect left half via USB"
    @echo "2. Click 'Connect' and select your keyboard"
    @echo "3. Edit your keymap live"
    @echo ""
    @open https://zmk.studio || xdg-open https://zmk.studio || echo "Please open https://zmk.studio manually"

# Show build output location
show:
    @echo "Firmware files in ./result/"
    @ls -la result/ 2>/dev/null || echo "No build output yet. Run 'just build' first."

# Clean build artifacts
clean:
	rm -f result result-*

# Regenerate layer visualization PDF
pdf:
	@echo "Generating layer visualization PDF..."
	cd zmk_to_pdf && uv run python -m zmk_to_pdf ../miryoku/custom_config.h ../layout.pdf
	@echo "✓ PDF generated: layout.pdf"
