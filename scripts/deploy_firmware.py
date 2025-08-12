#!/usr/bin/env python3
"""
Deploy Claude Monitor firmware to M5StickC PLUS
Clean production deployment script
"""
import os
import sys
import subprocess

def deploy_firmware(port="COM4", firmware_file="claude_monitor_main.py"):
    """Deploy specified firmware to M5StickC PLUS"""
    print(f"Deploying Claude Monitor to M5StickC PLUS on {port}...")
    
    firmware_path = f"firmware/{firmware_file}"
    if not os.path.exists(firmware_path):
        print(f"Error: {firmware_path} not found")
        return False
    
    try:
        # Deploy main firmware
        print(f"Uploading {firmware_file} as main.py...")
        cmd = f'pipenv run ampy --port {port} put "{firmware_path}" main.py'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error deploying firmware: {result.stderr}")
            return False
        
        print("✓ Firmware deployed successfully")
        
        # Reset device
        print("Resetting device...")
        cmd = f'pipenv run python -m esptool --port {port} run'
        subprocess.run(cmd, shell=True, capture_output=True)
        
        print("✓ Device reset complete")
        return True
        
    except Exception as e:
        print(f"Deployment error: {e}")
        return False

if __name__ == "__main__":
    port = sys.argv[1] if len(sys.argv) > 1 else "COM4"
    firmware = sys.argv[2] if len(sys.argv) > 2 else "claude_monitor_main.py"
    
    print("Claude Monitor - Clean Deployment")
    print("=" * 35)
    print(f"Port: {port}")
    print(f"Firmware: {firmware}")
    print()
    
    if deploy_firmware(port, firmware):
        print("✓ Deployment successful!")
        print("\nYour M5StickC PLUS is now running the Claude Monitor")
        print("- Real-time clock updates every second")
        print("- Stylish UI with header/footer")
        print("- Button A: Acknowledge alerts")  
        print("- Button B: Manual refresh")
    else:
        print("✗ Deployment failed")
        sys.exit(1)