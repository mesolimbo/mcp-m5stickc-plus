#!/usr/bin/env python3
"""Test script to validate M5StickC PLUS connection and basic functionality"""

from pathlib import Path
import serial
import subprocess
import sys
import time


def find_device_port():
    """Try to find the M5StickC PLUS serial port"""
    import serial.tools.list_ports
    
    # Common patterns for M5StickC PLUS
    patterns = ['CP210', 'Silicon Labs', 'USB']
    
    ports = serial.tools.list_ports.comports()
    
    for port in ports:
        for pattern in patterns:
            if pattern.lower() in port.description.lower():
                print(f"Found potential device: {port.device} - {port.description}")
                return port.device
    
    if ports:
        print("Available ports:")
        for port in ports:
            print(f"  {port.device} - {port.description}")
    else:
        print("No serial ports found")
    
    return None

def test_serial_connection(port, baudrate=115200):
    """Test basic serial connection to device"""
    try:
        print(f"Connecting to {port} at {baudrate} baud...")
        
        with serial.Serial(port, baudrate, timeout=2) as ser:
            print("Connected! Sending test command...")
            
            # Send a simple Python command
            ser.write(b'\r\nprint("Hello from M5StickC PLUS!")\r\n')
            time.sleep(0.5)
            
            # Read response
            response = ser.read(ser.in_waiting)
            if response:
                print(f"Device response: {response.decode('utf-8', errors='ignore')}")
                return True
            else:
                print("No response from device")
                return False
                
    except serial.SerialException as e:
        print(f"Serial connection failed: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def test_firmware_upload(port):
    """Test if we can upload a simple test file"""
    test_file = None
    try:

        
        # Create a simple test file
        test_code = '''
print("Firmware test successful!")
print("M5StickC PLUS is ready for Claude Monitor")
'''
        
        test_file = Path("test_upload.py")
        test_file.write_text(test_code)
        
        print(f"Uploading test file to {port}...")
        
        # Use ampy to upload
        cmd = ['pipenv', 'run', 'ampy', '--port', port, 'put', str(test_file)]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("Upload successful!")
            
            # Try to run the file
            cmd = ['pipenv', 'run', 'ampy', '--port', port, 'run', str(test_file)]
            ampy_result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if ampy_result.returncode == 0:
                print(f"Execution successful!\nOutput: {ampy_result.stdout}")
                return True
            else:
                print(f"Execution failed: {ampy_result.stderr}")
                return False
        else:
            print(f"Upload failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("Upload/execution timed out")
        return False
    except Exception as e:
        print(f"Upload test failed: {e}")
        return False
    finally:
        # Cleanup test file
        if test_file and test_file.exists():
            test_file.unlink()

def test_wifi_config():
    """Test if WiFi configuration is set up"""
    config_file = Path("config/credentials.txt")
    
    if not config_file.exists():
        print("❌ credentials.txt not found")
        print("Please copy config/credentials.sample.txt to config/credentials.txt")
        return False
    
    try:
        content = config_file.read_text()
        has_ssid = 'WIFI_SSID=' in content and 'your-network-name' not in content
        has_password = 'WIFI_PASSWORD=' in content and 'your-wifi-password' not in content
        has_host = 'SERVER_HOST=' in content and '192.168.1.100' not in content
        
        if has_ssid and has_password and has_host:
            print("✅ WiFi configuration looks good")
            return True
        else:
            print("⚠️  WiFi configuration needs updating:")
            if not has_ssid: print("  - WIFI_SSID needs to be set")
            if not has_password: print("  - WIFI_PASSWORD needs to be set")
            if not has_host: print("  - SERVER_HOST needs to be set to your computer's IP")
            return False
            
    except Exception as e:
        print(f"❌ Error reading config: {e}")
        return False

def run_device_tests(port):
    """Run comprehensive device tests"""
    print("\n=== M5StickC PLUS Device Tests ===")
    
    tests = [
        ("Serial Connection", lambda: test_serial_connection(port)),
        ("Firmware Upload", lambda: test_firmware_upload(port)),
        ("WiFi Configuration", test_wifi_config)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"Test failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n=== Test Results ===")
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! M5StickC PLUS is ready for Claude Monitor firmware.")
    else:
        print("\n⚠️  Some tests failed. Please check the issues above before proceeding.")
    
    return all_passed

def main():
    if len(sys.argv) > 1:
        port = sys.argv[1]
        print(f"Using specified port: {port}")
    else:
        port = find_device_port()
        if not port:
            print("No device found. Please specify port manually:")
            print(f"Usage: {sys.argv[0]} <port>")
            print("Example: python test_connection.py COM3  (Windows)")
            print("Example: python test_connection.py /dev/ttyUSB0  (Linux)")
            sys.exit(1)
    
    success = run_device_tests(port)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
