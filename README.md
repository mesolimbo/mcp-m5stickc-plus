# Claude Pro Session Monitor for M5StickC PLUS

A high-performance framebuffer-based session monitor that transforms the M5StickC PLUS into a smart development companion for Claude Pro users. Features instant display updates, power-saving sleep mode, and work-friendly audio alerts.

## Features

### Session Monitoring
- **Real-time Session Tracking**: Live session timer with hours, minutes, and seconds
- **Live Clock Display**: Real-time clock that updates every second  
- **Session Statistics**: Command count, files edited, productivity metrics
- **Token Usage Tracking**: Live token consumption counter
- **Visual Status Indicators**: Color-coded status (active/idle) with styled UI

### High-Performance Display
- **Framebuffer Rendering**: Instant screen updates using 26MHz SPI
- **Stylish UI**: Blue header, gray footer, color-coded status sections
- **Smooth Animations**: Real-time clock ticking, progress bars, status changes
- **Power Management**: 60-second auto-sleep with instant wake

### Audio Alerts
- **Work-Friendly Beeps**: Single quiet tone for new alerts (800Hz, 100ms)
- **Startup Melody**: Pleasant rising tone sequence on boot
- **Office-Appropriate**: Low volume (25% duty cycle) to avoid disturbing coworkers

### Power-Saving Controls
- **Button A**: Wake display and reset 60-second sleep timer
- **Auto-Sleep**: Display automatically turns off after 60 seconds of inactivity
- **Instant Wake**: Press A anytime to immediately wake display and reset timer

## Architecture

### MCP Server (`mcp_server.py`)
- Implements MCP protocol for Claude Code integration
- Provides tools for session management and alert control
- Handles cost calculation and session persistence

### M5StickC PLUS Firmware (`firmware/`)
- **WiFi Communication**: Connects to MCP server via HTTP/WebSocket
- **Display Management**: Shows session stats, time, cost estimates with pale green text and blinking icons
- **Audio System**: Generates very quiet tone alerts with configurable patterns
- **Sensor Integration**: IMU for gesture controls, button handling
- **Power Management**: Battery monitoring and sleep modes

### Session Monitor (`session_monitor.py`)
- Tracks Claude Code process activity
- Monitors token usage and API calls
- Calculates real-time cost estimates
- Detects command approval states

## Hardware Requirements

- M5StickC PLUS controller
- WiFi network connection

## Installation

### MCP Server Setup
```bash
cd mcp-M5StickC-PLUS
pip install -r requirements.txt

# Configure Claude Code to use the MCP server
echo '{
  "mcpServers": {
    "m5stick-session-timer": {
      "command": "python",
      "args": ["mcp_server.py"],
      "env": {
        "M5STICK_IP": "192.168.1.100"
      }
    }
  }
}' > ~/.claude-code/mcp.json
```

### Quick Start

#### 1. Flash MicroPython Firmware
```bash
# Install dependencies
pipenv install

# Erase existing firmware
pipenv run python -m esptool --port COM4 erase_flash

# Flash MicroPython v1.26.0
pipenv run python -m esptool --port COM4 --baud 115200 write_flash 0x1000 firmware_downloads/ESP32_GENERIC-20250809-v1.26.0.bin
```

#### 2. Deploy Claude Pro Monitor
```bash
# Option 1: Use deployment script
python scripts/deploy_firmware.py COM4

# Option 2: Manual deployment
pipenv run ampy --port COM4 put firmware/claude_monitor_main.py main.py
pipenv run python -m esptool --port COM4 run
```

#### 3. What You'll Experience
- **"CLAUDE PRO SESSION MONITOR V2.0"** - Stylish startup with audio
- **Real-time display updates** - Clock ticks every second, smooth UI
- **Power-saving mode** - Display auto-sleeps after 60 seconds
- **Button A control** - Press anytime to wake display and reset timer
- **Work-friendly alerts** - Single quiet beep for new alerts

#### Hardware Specs
- **Device**: ESP32-PICO-D4 (revision v1.1) 
- **Display**: ST7789V2 (135×240 pixels, landscape orientation)
- **Coordinates**: Hardware offsets x+52, y+40 (proven working)
- **Power**: AXP192 chip (critical for display operation)

## Configuration

### `config.py` (M5StickC PLUS)
```python
# WiFi Settings
WIFI_SSID = "your-network"
WIFI_PASSWORD = "your-password"

# MCP Server
SERVER_HOST = "192.168.1.50"
SERVER_PORT = 8080

# Alert Settings
QUIET_TONE_FREQUENCY = 800  # Hz
TONE_DURATION = 100    # ms (very brief)
TONE_VOLUME = 10       # Low volume (0-100)
ALERT_TIMEOUT = 300    # seconds
BLINK_RATE = 2         # Blinks per second

# Display Settings
BRIGHTNESS = 50
SHOW_COST = True
CURRENCY = "USD"
```

### `mcp_config.json` (Server)
```json
{
  "session_tracking": {
    "auto_start": true,
    "cost_tracking": true,
    "model_rates": {
      "claude-3-sonnet": {
        "input": 0.003,
        "output": 0.015
      }
    }
  },
  "alerts": {
    "command_approval": true,
    "session_milestones": [60, 300, 900],
    "cost_thresholds": [1, 5, 10]
  }
}
```

## Usage

### Automatic Mode
1. Start Claude Code - session tracking begins automatically
2. M5StickC PLUS displays current session time and estimated cost
3. When Claude requests command approval, device beeps and shows alert
4. Press Button B to acknowledge (or approve in Claude Code)
5. Session ends when Claude Code closes

### Manual Control
- **Press large button**: Disable audio alerts temporarily (visual alerts remain)

### Display Modes
- **Default**: Current session time and cost (pale green text)
- **Stats**: Total daily usage and cost
- **Alerts**: Command approval status with blinking icon
- **Settings**: Configuration menu

## MCP Tools Provided

### `start_session`
Manually start a new tracking session
```json
{
  "name": "start_session",
  "description": "Start tracking a new Claude session",
  "parameters": {
    "project_name": "Optional project identifier"
  }
}
```

### `get_session_stats`
Retrieve current session statistics
```json
{
  "name": "get_session_stats", 
  "description": "Get current session duration and cost estimates"
}
```

### `set_alert_mode`
Configure alert behavior
```json
{
  "name": "set_alert_mode",
  "parameters": {
    "mode": "enabled|disabled|quiet_hours",
    "quiet_start": "22:00",
    "quiet_end": "08:00"
  }
}
```

## Development

### File Structure
```
mcp-M5StickC-PLUS/
├── README.md                    # Main documentation
├── DISPLAY.md                   # Hardware display specifications  
├── PROJECT_STRUCTURE.md         # Clean architecture overview
├── Pipfile                      # Python dependencies
├── src/
│   └── mcp_server.py           # MCP server for Claude Code integration
├── firmware/                    # M5StickC PLUS MicroPython code
│   ├── claude_monitor.py       # Main application (readable text UI)
│   ├── claude_monitor_wifi.py  # WiFi-enabled version
│   ├── display.py              # Display driver
│   ├── wifi_manager.py         # WiFi management
│   ├── sensors.py              # Button handling
│   ├── alerts.py               # Alert system
│   └── boot.py                 # Device boot config
├── config/
│   ├── device_config.py        # M5StickC PLUS settings
│   └── credentials.sample.txt  # WiFi credentials template
├── scripts/
│   ├── flash_device.sh         # Device flashing
│   └── test_connection.py      # Connection testing
└── firmware_downloads/
    └── ESP32_GENERIC-*.bin     # MicroPython firmware binaries
```

### Testing
```bash
# Test MCP server
python -m pytest tests/test_mcp_server.py

# Test with Claude Code
claude-code --mcp-server m5stick-session-timer test_session.py

# M5StickC PLUS firmware testing
cd firmware && python test_display.py
```

## Customization

### Alert Patterns
Add custom visual and quiet audio patterns for different events:
```python
ALERT_PATTERNS = {
    'command_approval': {
        'tone': [800, 100],  # [frequency, duration]
        'blink': [2, 'pale_green'],  # [rate, color]
        'icon': '⏳'
    },
    'cost_threshold': {
        'tone': [600, 50, 800, 50],  # Brief double tone
        'blink': [3, 'yellow'],
        'icon': '💰'
    },
    'session_milestone': {
        'tone': [1000, 150],
        'blink': [1, 'blue'],
        'icon': '🕐'
    }
}
```

### Display Themes
Create custom display layouts and color schemes for different development contexts.

### Integration Examples
- Slack notifications for long sessions
- GitHub commit correlation with session data
- Team productivity dashboards
- Integration with existing time tracking tools

## Troubleshooting

### Common Issues
1. **M5StickC PLUS not connecting**: Check WiFi credentials and server IP
2. **No session detection**: Ensure Claude Code MCP configuration is correct
3. **Inaccurate cost estimates**: Update model pricing in configuration
4. **Audio not working**: Verify buzzer connections and volume settings

### Debug Mode
Enable detailed logging:
```bash
export DEBUG_M5STICK=1
python mcp_server.py --verbose
```

## Future Enhancements

- Multi-device support for team environments
- Integration with project management tools
- Advanced analytics and reporting
- Voice commands via built-in microphone
- Integration with other development tools (VS Code, terminal multiplexers)
- Cloud sync for session data across machines

## License

MIT License - feel free to modify and extend for your development workflow needs.
