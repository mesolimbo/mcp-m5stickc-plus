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

✅ **Production Ready**: High-performance framebuffer-based Claude Pro Session Monitor
✅ **Working**: Real-time clock updating every second with smooth animations
✅ **Working**: Stylish UI with blue header, gray footer, and color-coded sections
✅ **Working**: Power-saving 60-second auto-sleep with Button A wake functionality
✅ **Working**: Work-friendly audio alerts (single quiet beep per alert)
✅ **Working**: 26MHz SPI with instant display updates and optimized rendering
✅ **Working**: Session tracking with statistics (time, commands, files, tokens, productivity)

🚧 **Future Enhancement**: WiFi integration for real Claude Code session tracking

## Usage

1. **Production**: `claude_monitor_main.py` - High-performance framebuffer version with power management
2. **Legacy**: `claude_monitor.py` - Original character-based version (for reference)
3. **Deployment**: `scripts/deploy_firmware.py` - Clean deployment script
4. **Future**: WiFi version for live MCP server integration

## Device Behavior

### Display Management
- **Auto-sleep**: Display turns off after 60 seconds of inactivity
- **Button A**: Press anytime to wake display and reset 60-second timer  
- **Timer reset**: Each Button A press resets countdown (press at 45s = sleep at 105s)
- **Visual feedback**: Stylish UI with real-time clock, session stats, progress bars

### Audio Alerts
- **Startup**: Pleasant rising tone melody on boot
- **New alerts**: Single quiet beep (800Hz, 100ms) - work-friendly
- **No repetition**: Each alert beeps only once when it first appears

### Session Simulation
- **Real-time tracking**: Session timer, command count, file edits, productivity
- **Token counter**: Live token usage simulation
- **Status indicators**: Color-coded active/idle status

## Clean Architecture

- **Firmware**: Production-ready MicroPython applications (test files removed)
- **Server**: MCP integration for Claude Code session data (future)
- **Config**: Environment-specific settings  
- **Clean**: All experimental and debug code removed