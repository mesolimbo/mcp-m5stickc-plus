# Claude Session Timer & Alert MCP Server

An MCP server that transforms the M5StickC PLUS into a smart development companion that tracks Claude Code session duration, estimates costs, and provides audio alerts for command approvals.

## Features

### Session Tracking
- **Real-time Duration Tracking**: Automatically tracks active Claude Code session time
- **Cost Estimation**: Calculates approximate session costs based on token usage and model pricing
- **Visual Display**: Shows current session stats on the M5StickC PLUS LCD (135x240)
- **Session History**: Maintains log of previous sessions with duration and cost data
- **Battery Level**: Charge remaining on device

### Command Approval Alerts
- **Visual Notifications**: Pale green text display with blinking icon when Claude is waiting for user approval to run commands
- **Quiet Audio Alerts**: Very quiet tone notifications to avoid disturbing coworkers
- **Customizable Alerts**: Different visual patterns and quiet tones for different command types (bash, file operations, etc.)
- **Timeout Warnings**: Escalating visual alerts if approval is pending too long

### Physical Controls
- **Press large button**: Disable audio alerts temporarily (visual alerts remain)
- **Auto-detection**: Automatically starts/stops based on Claude Code activity

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

### M5StickC PLUS Firmware
```bash
# Flash MicroPython firmware
esptool.py --port /dev/ttyUSB0 write_flash -z 0x1000 m5stick-micropython.bin

# Upload application files
ampy --port /dev/ttyUSB0 put main.py
ampy --port /dev/ttyUSB0 put config.py
ampy --port /dev/ttyUSB0 put wifi_config.py
```

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
├── README.md
├── TOOLS.md
├── Pipfile               # Dependencies and dev tools
├── src/                  # Python MCP server code
│   ├── __init__.py
│   ├── mcp_server.py     # Main MCP server
│   ├── session_monitor.py # Claude Code activity monitor  
│   ├── cost_calculator.py # Token usage and cost tracking
│   └── utils/
│       ├── __init__.py
│       ├── logging.py    # Logging utilities
│       └── config.py     # Configuration management
├── scripts/              # Deployment and utility scripts
│   ├── flash_device.sh   # Device flashing script
│   ├── deploy.py         # Deployment automation
│   └── test_connection.py # Connection testing
├── firmware/             # M5StickC PLUS MicroPython code
│   ├── boot.py          # Device boot configuration
│   ├── main.py          # M5StickC PLUS main application
│   ├── wifi_manager.py  # WiFi connection handling
│   ├── display.py       # LCD display management
│   ├── alerts.py        # Audio/visual alert system
│   └── sensors.py       # Button and IMU handling
├── config/               # Configuration files
│   ├── mcp_config.json  # Server configuration
│   └── device_config.py # M5StickC PLUS settings
└── tests/                # Test files
    ├── __init__.py
    ├── test_mcp_server.py
    ├── test_session_monitor.py
    └── firmware_test.py
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
