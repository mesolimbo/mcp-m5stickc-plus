# Claude Monitor M5StickC PLUS - Clean Project Structure

## Core Files

### Firmware (MicroPython for M5StickC PLUS)
- `firmware/claude_monitor_main.py` - **Main framebuffer-based Claude Monitor application**
- `firmware/claude_monitor.py` - Original character-based version (legacy)  
- `firmware/claude_monitor_wifi.py` - WiFi-enabled version for real server connection
- `firmware/display.py` - Display driver and graphics functions
- `firmware/st7789_driver.py` - Optimized ST7789 display driver
- `firmware/wifi_manager.py` - WiFi connection management
- `firmware/sensors.py` - Button and sensor handling
- `firmware/alerts.py` - Alert system for command approvals
- `firmware/boot.py` - Device boot configuration
- `firmware/main.py` - Current firmware running on device

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

✅ **Working**: High-performance framebuffer-based Claude Monitor  
✅ **Working**: Real-time clock and session tracking with smooth updates
✅ **Working**: Stylish UI with header/footer design
✅ **Working**: Interactive button controls (A: acknowledge, B: refresh)
✅ **Working**: 26MHz SPI with instant display updates

🚧 **Next**: WiFi integration for real Claude Code session tracking

## Usage

1. **Production**: `claude_monitor_main.py` - Fast framebuffer version with stylish UI
2. **Legacy**: `claude_monitor.py` - Original slower character-based version
3. **Future**: WiFi integration with MCP server for live session data

## Clean Architecture

- **Firmware**: Production-ready MicroPython applications (test files removed)
- **Server**: MCP integration for Claude Code session data
- **Config**: Environment-specific settings  
- **Clean**: All experimental and debug code removed