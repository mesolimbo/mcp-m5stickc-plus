# Claude Monitor M5StickC PLUS - Project Structure

## Core Files

### Firmware (MicroPython for M5StickC PLUS)
- `firmware/claude_monitor.py` - **Main Claude Monitor application** (currently running on device)
- `firmware/claude_monitor_wifi.py` - WiFi-enabled version for real server connection
- `firmware/display.py` - Display driver and graphics functions
- `firmware/wifi_manager.py` - WiFi connection management
- `firmware/sensors.py` - Button and sensor handling
- `firmware/alerts.py` - Alert system for command approvals
- `firmware/boot.py` - Device boot configuration
- `firmware/main.py` - Current firmware loaded on device

### MCP Server (Python for PC)
- `src/mcp_server.py` - MCP server for Claude Code integration

### Configuration
- `config/device_config.py` - M5StickC PLUS configuration settings
- `config/credentials.sample.txt` - Template for WiFi credentials

### Documentation
- `README.md` - Main project documentation
- `DISPLAY.md` - Hardware display specifications and working coordinates
- `TOOLS.md` - Development tools and utilities

### Build & Deploy
- `scripts/flash_device.sh` - Device flashing script
- `scripts/test_connection.py` - Connection testing
- `Pipfile` / `Pipfile.lock` - Python dependencies

### Hardware Resources
- `firmware_downloads/` - MicroPython firmware binaries

## Current Status

✅ **Working**: Claude Monitor with readable text display
✅ **Working**: Correct display rotation (0x00) and coordinates (135×240 with offsets)
✅ **Working**: Real-time session simulation with cost tracking
✅ **Working**: Interactive button controls (A: acknowledge, B: refresh)

🚧 **Next**: WiFi integration for real Claude Code session tracking

## Usage

1. **Current Demo**: Device runs standalone simulation showing session time, cost, alerts
2. **Future**: Connect to MCP server for real Claude Code session monitoring

## Clean Architecture

- **Firmware**: Self-contained MicroPython applications
- **Server**: Optional MCP integration for real session data
- **Config**: Environment-specific settings
- **No test files**: All debugging/test code removed for clean deployment