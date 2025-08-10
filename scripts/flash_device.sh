#!/bin/bash
# flash_device.sh - M5StickC PLUS Deployment Script

set -e

DEVICE_PORT=${1:-/dev/ttyUSB0}  # Default port, override with argument
FIRMWARE_FILE="firmware_downloads/ESP32_GENERIC-20250809-v1.26.0.bin"

echo "=== M5StickC PLUS Deployment Script ==="
echo "Port: $DEVICE_PORT"
echo "Firmware: $FIRMWARE_FILE"

# Check if firmware file exists
if [ ! -f "$FIRMWARE_FILE" ]; then
    echo "Error: Firmware file not found: $FIRMWARE_FILE"
    echo "Please run: curl -k -L -o $FIRMWARE_FILE https://micropython.org/resources/firmware/ESP32_GENERIC-20250809-v1.26.0.bin"
    exit 1
fi

# 1. Erase flash
echo "Erasing flash memory..."
pipenv run esptool.py --port $DEVICE_PORT erase_flash

# 2. Flash MicroPython firmware
echo "Flashing MicroPython firmware..."
pipenv run esptool.py --port $DEVICE_PORT --baud 460800 write_flash 0x1000 $FIRMWARE_FILE

# 3. Wait for device reboot
echo "Waiting for device to reboot..."
sleep 5

# 4. Upload application files (when ready)
echo "Firmware flashed successfully!"
echo "Device ready for application code upload."
echo ""
echo "Next steps:"
echo "1. Test connection: pipenv run ampy --port $DEVICE_PORT ls"
echo "2. Upload application files when ready"

echo "=== Deployment Complete ==="