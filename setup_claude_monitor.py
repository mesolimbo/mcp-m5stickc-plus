#!/usr/bin/env python3
"""
Setup script for Claude Monitor M5StickC PLUS
"""

import os
import sys
import subprocess
import json

def get_wifi_credentials():
    """Get WiFi credentials from user"""
    print("=== WiFi Configuration ===")
    ssid = input("Enter your WiFi network name (SSID): ").strip()
    password = input("Enter your WiFi password: ").strip()
    
    if not ssid or not password:
        print("ERROR: Both SSID and password are required")
        return None, None
    
    return ssid, password

def get_pc_ip():
    """Detect PC IP address"""
    try:
        # Try to get IP from ipconfig on Windows
        result = subprocess.run(['ipconfig'], capture_output=True, text=True, shell=True)
        lines = result.stdout.split('\n')
        
        for line in lines:
            if 'IPv4 Address' in line and '192.168.1.' in line:
                ip = line.split(':')[-1].strip()
                return ip
        
        # Fallback - ask user
        print("Could not auto-detect IP address")
        ip = input("Enter your PC's IP address (e.g., 192.168.1.8): ").strip()
        return ip if ip else "192.168.1.8"
        
    except:
        return "192.168.1.8"

def create_firmware_config(ssid, password, server_ip):
    """Create configured firmware file"""
    firmware_template = "firmware/claude_monitor_wifi.py"
    firmware_output = "firmware/claude_monitor_configured.py"
    
    if not os.path.exists(firmware_template):
        print(f"ERROR: Template file {firmware_template} not found")
        return False
    
    try:
        with open(firmware_template, 'r') as f:
            content = f.read()
        
        # Replace configuration placeholders
        content = content.replace('WIFI_SSID = "YOUR_WIFI_SSID"', f'WIFI_SSID = "{ssid}"')
        content = content.replace('WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"', f'WIFI_PASSWORD = "{password}"')
        content = content.replace('SERVER_URL = "http://192.168.1.100:8080"', f'SERVER_URL = "http://{server_ip}:8080"')
        
        with open(firmware_output, 'w') as f:
            f.write(content)
        
        print(f"Configured firmware saved to: {firmware_output}")
        return True
        
    except Exception as e:
        print(f"ERROR creating configured firmware: {e}")
        return False

def create_mcp_config(server_ip):
    """Create MCP configuration for Claude Code"""
    mcp_config = {
        "mcpServers": {
            "claude-session-monitor": {
                "command": "python",
                "args": ["src/mcp_server.py"],
                "env": {
                    "SERVER_HOST": server_ip,
                    "SERVER_PORT": "8080"
                }
            }
        }
    }
    
    # Create Claude Code MCP config directory
    claude_config_dir = os.path.expanduser("~/.claude-code")
    os.makedirs(claude_config_dir, exist_ok=True)
    
    config_file = os.path.join(claude_config_dir, "mcp_servers.json")
    
    try:
        # Load existing config if it exists
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                existing_config = json.load(f)
                existing_config["mcpServers"].update(mcp_config["mcpServers"])
                mcp_config = existing_config
        
        with open(config_file, 'w') as f:
            json.dump(mcp_config, f, indent=2)
        
        print(f"MCP configuration saved to: {config_file}")
        return True
        
    except Exception as e:
        print(f"ERROR creating MCP config: {e}")
        return False

def main():
    """Main setup process"""
    print("Claude Monitor M5StickC PLUS Setup")
    print("=====================================")
    
    # Step 1: WiFi credentials
    ssid, password = get_wifi_credentials()
    if not ssid:
        print("Setup cancelled")
        return
    
    # Step 2: PC IP address
    print(f"\n=== Server Configuration ===")
    server_ip = get_pc_ip()
    print(f"Using server IP: {server_ip}")
    
    # Step 3: Create configured firmware
    print(f"\n=== Creating Firmware ===")
    if not create_firmware_config(ssid, password, server_ip):
        print("Setup failed")
        return
    
    # Step 4: Create MCP config
    print(f"\n=== Configuring Claude Code MCP ===")
    create_mcp_config(server_ip)
    
    # Step 5: Instructions
    print(f"\nSetup Complete!")
    print(f"\nNext steps:")
    print(f"1. Upload firmware to M5StickC PLUS:")
    print(f"   pipenv run ampy --port COM4 put firmware/claude_monitor_configured.py main.py")
    print(f"")
    print(f"2. Start the MCP server:")
    print(f"   pipenv run python src/mcp_server.py")
    print(f"")
    print(f"3. Start Claude Code with MCP support")
    print(f"")
    print(f"4. Use Claude Code - the M5StickC will show:")
    print(f"   - Session duration")
    print(f"   - Cost estimates")  
    print(f"   - Command approval alerts")
    print(f"   - Daily statistics")
    print(f"")
    print(f"Controls:")
    print(f"   - Button A (large): Acknowledge alerts")
    print(f"   - Button B (small): Manual refresh")

if __name__ == "__main__":
    main()