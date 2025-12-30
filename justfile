# Miryoku ZMK firmware build commands

# List all available recipes
default:
    @just --list --justfile {{justfile()}}

# Build main firmware (left + right halves with ZMK Studio)
build:
    nix build

# Build settings reset firmware (for Bluetooth bond issues)
build-reset:
    nix build .#settings-reset

# Flash main firmware interactively
flash:
    nix run .#flash

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
