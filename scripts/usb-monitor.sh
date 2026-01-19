#!/usr/bin/env bash
# Monitor USB device connection states via kernel logs
# Usage: ./scripts/usb-monitor.sh
#
# This script helps validate keyboard device modes by monitoring kernel logs:
#   - Volume mount mode: "sd 0:0:0:0: [sda] Attached SCSI removable disk"
#   - Normal mode: "USB HID v1.11 Keyboard [ZMK Project Aurora Sweep]"
#   - Settings reset mode: "USB HID v1.11 Keyboard [ZMK Project SETTINGS RESET]"
#
# Useful for debugging USB connectivity and verifying the keyboard's current state.

sudo journalctl -kf
