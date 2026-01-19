#!/usr/bin/env bash
# Auto-reconnect serial monitor for ZMK USB logging
# Usage: ./scripts/serial-monitor.sh [device] [baud]
#
# This script monitors a serial device and automatically connects picocom
# when the device appears. Useful for watching keyboard logs during boot/reset.
#
# In picocom, press Ctrl+A then Ctrl+X to exit cleanly.
#
# Example:
#   ./scripts/serial-monitor.sh /dev/ttyACM0 115200

set -u

DEVICE="${1:-/dev/ttyACM0}"
BAUD="${2:-115200}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}Monitoring ${YELLOW}${DEVICE}${GREEN} at ${YELLOW}${BAUD}${GREEN} baud...${NC}"
echo -e "${BLUE}To exit picocom: press ${YELLOW}Ctrl+A${BLUE}, then ${YELLOW}Ctrl+X${BLUE}, then ${YELLOW}Ctrl+C${BLUE} to exit the loop${NC}"
echo -e "${YELLOW}Waiting for device...${NC}"

# Cleanup function
cleanup() {
    echo -e "\n${RED}Exiting monitor...${NC}"
    exit 0
}

trap cleanup INT TERM

while true; do
    if [ -e "$DEVICE" ]; then
        echo -e "${GREEN}Device found! Connecting...${NC}"
        # Run picocom; if it exits cleanly (user pressed Ctrl+A Ctrl+X), we continue
        # If device disconnects, picocom will exit with an error, which we handle gracefully
        if picocom "$DEVICE" -b "$BAUD" 2>/dev/null; then
            # picocom exited cleanly, wait a moment then try again
            sleep 1
        else
            # picocom exited (device may have disconnected)
            sleep 1
        fi
        echo -e "${YELLOW}Waiting for device...${NC}"
    else
        sleep 1
    fi
done
