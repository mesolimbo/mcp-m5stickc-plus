#!/usr/bin/env python3
"""
Deploy and test optimized Claude Monitor to M5StickC PLUS
"""
import os
import sys
import time
import subprocess

def deploy_to_device(port="COM3"):
    """Deploy optimized version to M5StickC PLUS"""
    print("Deploying optimized Claude Monitor...")
    
    firmware_files = [
        "claude_monitor_optimized.py"
    ]
    
    for file in firmware_files:
        filepath = f"firmware/{file}"
        if os.path.exists(filepath):
            print(f"Deploying {file}...")
            # Using ampy or mpremote to copy files
            try:
                # Try mpremote first (newer tool)
                cmd = f'mpremote connect {port} cp "{filepath}" :{file}'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode != 0:
                    # Fallback to ampy
                    cmd = f'ampy -p {port} put "{filepath}" {file}'
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"✓ {file} deployed successfully")
                else:
                    print(f"✗ Failed to deploy {file}: {result.stderr}")
                    
            except FileNotFoundError:
                print("Error: Neither mpremote nor ampy found. Please install:")
                print("pip install mpremote")
                print("or")
                print("pip install adafruit-ampy")
                return False
        else:
            print(f"✗ File not found: {filepath}")
            return False
    
    return True

def run_test(port="COM3"):
    """Run the optimized version on device"""
    print("\nRunning optimized version...")
    try:
        cmd = f'mpremote connect {port} exec "import claude_monitor_optimized; claude_monitor_optimized.run_optimized_monitor()"'
        subprocess.run(cmd, shell=True)
    except KeyboardInterrupt:
        print("\nTest stopped by user")
    except Exception as e:
        print(f"Error running test: {e}")

def performance_comparison():
    """Show performance improvements"""
    print("\n" + "="*50)
    print("PERFORMANCE IMPROVEMENTS")
    print("="*50)
    print("Original version bottlenecks:")
    print("• 1ms delay per SPI write (35ms+ per character)")
    print("• 8MHz SPI speed")
    print("• Individual pixel draws")
    print("• Full screen clears on every update")
    print()
    print("Optimized version improvements:")
    print("• No unnecessary delays")
    print("• 40MHz SPI speed (5x faster)")
    print("• Bulk pixel writes")
    print("• Partial screen updates")
    print("• Chunked data for large areas")
    print()
    print("Expected performance gain: 10-20x faster refresh")
    print("="*50)

if __name__ == "__main__":
    port = sys.argv[1] if len(sys.argv) > 1 else "COM3"
    
    performance_comparison()
    
    print(f"\nUsing port: {port}")
    print("Press Ctrl+C to stop at any time")
    
    # Deploy
    if deploy_to_device(port):
        print("\n✓ Deployment successful!")
        
        # Ask user if they want to run test
        response = input("\nRun optimized version now? (y/n): ")
        if response.lower().startswith('y'):
            run_test(port)
    else:
        print("\n✗ Deployment failed")
        sys.exit(1)