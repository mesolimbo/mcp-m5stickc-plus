# Development Tools & Installation Guide

This document outlines all the tools, dependencies, and installation steps needed to develop, build, test, and deploy the Claude Session Timer & Alert MCP Server for M5StickC PLUS.

## Prerequisites

### Hardware Requirements
- **M5StickC PLUS** controller
- **USB-C cable** for programming and power
- **Computer** with USB port (Windows, macOS, or Linux)
- **WiFi network** for device connectivity

### Operating System Support
- Windows 10/11
- macOS 10.15+
- Linux (Ubuntu 18.04+, Debian, Fedora, Arch)

## Essential Non-Python Tools

### MicroPython Firmware
Pre-compiled firmware binaries required for M5StickC PLUS to run Python code.

**Download Sources:**
- MicroPython.org (Recommended): https://micropython.org/download/esp32/
- M5Stack Official UIFlow: https://github.com/m5stack/uiflow-micropython/releases

**M5StickC PLUS Hardware Specs:**
- **Chip**: ESP32-PICO-D4 (standard version) or ESP32-PICO-V3-02 (PLUS2)
- **Flash**: 4MB (PLUS) / 8MB (PLUS2) 
- **PSRAM**: None (PLUS) / 2MB (PLUS2)
- **Recommended Firmware**: Generic ESP32 (no SPIRAM for standard PLUS)

**Installation:**
```bash
# Create firmware directory
mkdir firmware_downloads
cd firmware_downloads

# Option 1: Latest MicroPython (Recommended for custom development)
# M5StickC PLUS (4MB flash, no PSRAM) - use generic ESP32
wget https://micropython.org/resources/firmware/ESP32_GENERIC-20250809-v1.26.0.bin

# Option 2: If you have M5StickC PLUS2 (8MB flash, 2MB PSRAM)
wget https://micropython.org/resources/firmware/ESP32_GENERIC_S3-SPIRAM_OCT-20250809-v1.26.0.bin

# Option 3: M5Stack UIFlow firmware (if you need M5 ecosystem integration)
wget https://github.com/m5stack/uiflow-micropython/releases/download/v1.13.0/M5StickCPlus_GENERIC-20231227-v1.22.0-m5f.bin
```

**Firmware Selection Guide:**
- **For our MCP project**: Use MicroPython v1.26.0 Generic ESP32 (latest, best compatibility)
- **For M5 ecosystem**: Use UIFlow firmware (M5-specific libraries included)
- **If you have PLUS2**: Use SPIRAM variant for enhanced performance

### USB-Serial Communication Drivers
Required for computer-to-device communication via USB-C cable.

**Driver Type:** CP210x Universal Windows Driver (Silicon Labs)

**Installation by Platform:**

**Windows:**
```bash
# Option 1: Automatic via Windows Update (recommended)
# Connect device and let Windows install drivers

# Option 2: Manual installation
# Download from: https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers
# Run installer as administrator
```

**macOS:**
```bash
# Option 1: Via Homebrew (recommended)
brew install --cask cp210x-vcp-driver

# Option 2: Manual download
# Download from Silicon Labs website and install .pkg file
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install linux-modules-extra-$(uname -r)

# Fedora/CentOS/RHEL
sudo dnf install kernel-modules-extra

# Add user to dialout group for USB access
sudo usermod -a -G dialout $USER
# Logout and login again for group changes to take effect
```

### Hardware Detection Tools
Built-in system tools for identifying connected devices.

**Windows:**
- Device Manager (`devmgmt.msc`)
- PowerShell: `Get-PnpDevice -Class Ports`

**macOS:**
- System Information (Apple Menu → About This Mac → System Report)
- Terminal: `ls /dev/tty.*`

**Linux:**
- `lsusb` - List USB devices
- `dmesg | grep tty` - Check kernel messages for serial devices
- `ls /dev/ttyUSB* /dev/ttyACM*` - List serial ports

## Python Environment Setup

### Python Version
- **Python 3.8+** (recommended: Python 3.10 or 3.11)
- **pipenv** for dependency and virtual environment management

### Installation
```bash
# Check Python version
python --version  # Should be 3.8+

# Install pipenv if not present
pip install pipenv

# Navigate to project directory
cd mcp-M5StickC-PLUS

# Install dependencies and create virtual environment
pipenv install

# Install development dependencies
pipenv install --dev

# Activate virtual environment
pipenv shell

# Or run commands in the environment without activating
pipenv run python mcp_server.py
```

## M5StickC PLUS Development Tools

### 1. ESP32 Toolchain

#### esptool.py (Essential)
Tool for flashing ESP32 devices and managing firmware.

```bash
# Install via pipenv (included in dev-packages)
pipenv install --dev

# Verify installation
pipenv run esptool.py version

# Test connection (replace COM3 with your port)
# Windows:
pipenv run esptool.py --port COM3 chip_id
# macOS:
pipenv run esptool.py --port /dev/tty.usbserial-* chip_id  
# Linux:
pipenv run esptool.py --port /dev/ttyUSB0 chip_id
```

#### USB-Serial Drivers
Required for computer-to-device communication.

**Windows:**
- Download and install [CP210x Universal Windows Driver](https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers)
- Or use Windows Update (usually automatic)

**macOS:**
```bash
# Install via Homebrew
brew install --cask cp210x-vcp-driver

# Or download from Silicon Labs website
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt-get install cp210x-dkms

# Fedora
sudo dnf install cp210x-dkms

# Add user to dialout group
sudo usermod -a -G dialout $USER
# Logout and login again
```

### 2. Optional Development Tools

#### Terminal/Serial Monitors
For debugging device output and direct communication.

**PuTTY (Windows)**
- Download from: https://www.putty.org/
- Free SSH and serial client
- Configure for COM port at 115200 baud

**Built-in Terminal Tools**
```bash
# macOS/Linux: screen
screen /dev/ttyUSB0 115200

# Alternative: minicom (Linux)
sudo apt-get install minicom
minicom -D /dev/ttyUSB0 -b 115200

# Windows: Use PuTTY or Windows Terminal with serial profile
```

#### Network Debugging Tools
Usually pre-installed on most systems.

```bash
# Test device connectivity
ping 192.168.1.100

# Test MCP server port
nmap -p 8080 192.168.1.100

# Test HTTP endpoints  
curl http://192.168.1.100:8080/health

# Monitor network traffic (optional)
wireshark  # GUI tool for packet analysis
```

#### File Transfer Tools

**ampy (Adafruit MicroPython Tool)**
```bash
# Install ampy (included in dev-packages)
pipenv install --dev

# Test connection
pipenv run ampy --port COM3 ls  # Windows
pipenv run ampy --port /dev/ttyUSB0 ls  # Linux
```

**rshell (Alternative)**
```bash
# Install rshell (included in dev-packages)
pipenv install --dev

# Connect to device
pipenv run rshell --port COM3  # Windows
pipenv run rshell --port /dev/ttyUSB0  # Linux
```

**Thonny IDE (GUI Option)**
```bash
# Install Thonny separately (not in pipenv)
pip install thonny

# Or download installer from: https://thonny.org/
```

### 3. Development IDE Options

#### VS Code (Recommended)
Extensions to install for enhanced development experience:

```bash
# Essential Extensions:
# - Python (Microsoft) - Python language support
# - MicroPython (by paulober) - MicroPython syntax and upload
# - ESP32/ESP8266 Support - ESP32 development tools

# Optional Extensions:
# - Serial Monitor - View device output in VS Code
# - REST Client - Test MCP HTTP endpoints
# - GitLens - Enhanced Git integration
```

**VS Code MicroPython Setup:**
1. Install MicroPython extension
2. Configure device connection (COM port/IP)
3. Set project as MicroPython project type
4. Use Ctrl+Shift+P → "MicroPython: Upload files to device"

#### PyCharm
Professional Python IDE with MicroPython support.

```bash
# Setup Steps:
# 1. Install MicroPython plugin from JetBrains marketplace
# 2. Configure Python interpreter for MicroPython
# 3. Set up device connection parameters
# 4. Configure ESP32 support for syntax highlighting
```

#### Thonny (Beginner-Friendly)
Simple IDE specifically designed for Python and MicroPython.

```bash
# Install Thonny separately (not in pipenv)
pip install thonny

# Or download installer from: https://thonny.org/

# Thonny Features:
# - Built-in MicroPython support
# - Simple file transfer interface
# - Interactive REPL for device testing
# - Beginner-friendly debugger
```

#### Command Line (Advanced)
For developers who prefer terminal-based workflows.

```bash
# Vim/Neovim with MicroPython support
# Install vim-micropython plugin for syntax highlighting

# Emacs with Python mode
# Configure for MicroPython development

# Command line file transfer and monitoring
pipenv run ampy --help    # File operations
pipenv run rshell         # Interactive shell
```

## MCP Development Tools

### Claude Code CLI
```bash
# Install Claude Code (if not already installed)
# Follow installation instructions at: https://docs.anthropic.com/claude/docs/claude-code

# Verify installation
claude-code --version

# Configure MCP server
mkdir -p ~/.claude-code
```

### MCP SDK and Testing
```bash
# Install MCP development dependencies (included in Pipfile)
pipenv install

# Install development/testing dependencies
pipenv install --dev

# All testing tools are now available via pipenv
```

## Build Tools

### Python Package Building
```bash
# Install build tools (included in dev-packages)
pipenv install --dev

# Build package
pipenv run python -m build

# For creating distributions
pipenv run twine upload dist/*
```

### Documentation
```bash
# Install documentation tools (included in dev-packages)
pipenv install --dev

# Generate documentation
pipenv run sphinx-build docs docs/_build
```

## Flashing & Deployment Scripts

### Automated Flash Script
Create a deployment script for easy device programming:

```bash
#!/bin/bash
# flash_device.sh

set -e

DEVICE_PORT=${1:-/dev/ttyUSB0}  # Default port, override with argument

echo "=== M5StickC PLUS Deployment Script ==="
echo "Port: $DEVICE_PORT"

# 1. Erase flash
echo "Erasing flash memory..."
pipenv run esptool.py --port $DEVICE_PORT erase_flash

# 2. Flash MicroPython firmware
echo "Flashing MicroPython firmware..."
# For standard M5StickC PLUS (ESP32-PICO-D4)
pipenv run esptool.py --port $DEVICE_PORT --baud 460800 write_flash 0x1000 firmware_downloads/ESP32_GENERIC-20250809-v1.26.0.bin

# Alternative: For UIFlow firmware
# pipenv run esptool.py --port $DEVICE_PORT write_flash -z 0x1000 firmware_downloads/M5StickCPlus_GENERIC-*.bin

# 3. Wait for device reboot
echo "Waiting for device to reboot..."
sleep 5

# 4. Upload application files
echo "Uploading application files..."
pipenv run ampy --port $DEVICE_PORT put firmware/boot.py
pipenv run ampy --port $DEVICE_PORT put firmware/main.py
pipenv run ampy --port $DEVICE_PORT put firmware/wifi_manager.py
pipenv run ampy --port $DEVICE_PORT put firmware/display.py
pipenv run ampy --port $DEVICE_PORT put firmware/alerts.py
pipenv run ampy --port $DEVICE_PORT put firmware/sensors.py

# 5. Upload configuration
echo "Uploading configuration..."
pipenv run ampy --port $DEVICE_PORT put config/device_config.py config.py

echo "=== Deployment Complete ==="
echo "Device ready! Press reset button on M5StickC PLUS to start."
```

### Windows PowerShell Version
```powershell
# flash_device.ps1
param(
    [string]$DevicePort = "COM3"
)

Write-Host "=== M5StickC PLUS Deployment Script ===" -ForegroundColor Green
Write-Host "Port: $DevicePort"

# Erase and flash firmware
pipenv run esptool.py --port $DevicePort erase_flash
# For standard M5StickC PLUS (ESP32-PICO-D4)
pipenv run esptool.py --port $DevicePort --baud 460800 write_flash 0x1000 firmware_downloads\ESP32_GENERIC-20250809-v1.26.0.bin

Start-Sleep -Seconds 5

# Upload files
pipenv run ampy --port $DevicePort put firmware\boot.py
pipenv run ampy --port $DevicePort put firmware\main.py
# ... (rest of files)

Write-Host "=== Deployment Complete ===" -ForegroundColor Green
```

## Testing Tools

### Unit Testing
```bash
# Install testing framework (included in dev-packages)
pipenv install --dev

# Run tests
pipenv run pytest tests/
pipenv run pytest --cov=src tests/  # With coverage
```

### Hardware-in-the-Loop Testing
```bash
# Install serial testing tools
pip install pyserial
pip install pytest-timeout

# For mocking hardware during development - unittest.mock is built-in
```

### MCP Server Testing
```bash
# Test MCP server locally
pipenv run python mcp_server.py --test-mode

# Test with Claude Code
claude-code --mcp-server file://$(pwd)/mcp_server.py test_commands.py

# M5StickC PLUS firmware testing
cd firmware && pipenv run python test_display.py
```

## Troubleshooting Tools

### Serial Monitor
```bash
# Monitor device output
# Using screen (macOS/Linux)
screen /dev/ttyUSB0 115200

# Using PuTTY (Windows)
# Download from: https://www.putty.org/

# Using ampy
pipenv run ampy --port COM3 run --no-output firmware/debug.py
```

### Device Detection
```bash
# List available serial ports
# Windows:
mode

# macOS:
ls /dev/tty.*

# Linux:
ls /dev/ttyUSB* /dev/ttyACM*
dmesg | grep tty
```

### WiFi Debugging
```bash
# Network tools for testing device connectivity
ping 192.168.1.100  # Test device IP
nmap -p 8080 192.168.1.100  # Test MCP server port
curl http://192.168.1.100:8080/health  # Test HTTP endpoint
```

## Installation Verification

Run this verification script to ensure all tools are properly installed:

```bash
#!/bin/bash
# verify_installation.sh

echo "=== Tool Verification Script ==="

# Check Python
python --version || echo "❌ Python not found"

# Check pipenv packages
pipenv run pip show esptool > /dev/null && echo "✅ esptool installed" || echo "❌ esptool missing"
pipenv run pip show adafruit-ampy > /dev/null && echo "✅ ampy installed" || echo "❌ ampy missing"
pipenv run pip show mcp > /dev/null && echo "✅ mcp installed" || echo "❌ mcp missing"

# Check Claude Code
claude-code --version > /dev/null && echo "✅ Claude Code installed" || echo "❌ Claude Code missing"

# Check serial ports
echo "Available serial ports:"
ls /dev/tty* 2>/dev/null | grep -E "(USB|ACM)" || echo "No USB serial ports found"

echo "=== Verification Complete ==="
```

## Quick Start Checklist

### Essential Requirements
- [ ] **Python 3.8+** installed
- [ ] **pipenv** installed (`pip install pipenv`)
- [ ] **USB-Serial drivers** installed (CP210x)
- [ ] **MicroPython firmware** downloaded (.bin file)
- [ ] **M5StickC PLUS** connected via USB-C cable
- [ ] **Device detected** by computer (check Device Manager/System Info/lsusb)

### Python Environment
- [ ] **Project dependencies** installed (`pipenv install`)
- [ ] **Development tools** installed (`pipenv install --dev`)
- [ ] **esptool.py** working (`pipenv run esptool.py version`)
- [ ] **ampy** working (`pipenv run ampy --help`)

### Claude Code Integration
- [ ] **Claude Code CLI** installed and configured
- [ ] **MCP server configuration** created
- [ ] **Network connectivity** confirmed (ping, curl tests)

### Optional Development Tools
- [ ] **IDE configured** (VS Code with MicroPython extension recommended)
- [ ] **Serial monitor** available (PuTTY, screen, or IDE built-in)
- [ ] **Network debugging tools** available (nmap, curl)

### Verification Tests
- [ ] **Device communication** test (`pipenv run esptool.py --port [PORT] chip_id`)
- [ ] **File transfer** test (`pipenv run ampy --port [PORT] ls`)
- [ ] **Firmware ready** for flashing
- [ ] **WiFi credentials** configured for device

## Getting Help

### Documentation Links
- [M5StickC PLUS Docs](https://docs.m5stack.com/en/core/M5StickC_PLUS)
- [MicroPython ESP32 Guide](https://docs.micropython.org/en/latest/esp32/quickref.html)
- [Claude Code MCP Documentation](https://docs.anthropic.com/claude/docs/claude-code/mcp)
- [ESP32 esptool Guide](https://docs.espressif.com/projects/esptool/en/latest/)

### Common Issues
- **Device not detected**: Check USB cable, try different port, install drivers
- **Permission denied**: Add user to dialout group (Linux), run as administrator (Windows)
- **Flash failed**: Hold BOOT button while connecting, use --before default_reset
- **Import errors**: Activate virtual environment, check requirements.txt

### Support Channels
- M5Stack Community Forum
- MicroPython Forum
- ESP32 Arduino Community
- Claude Code GitHub Issues