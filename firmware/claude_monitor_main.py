# Claude Monitor for M5StickC PLUS - Final Version
import gc
import time
from machine import Pin, I2C

print("M5StickC PLUS - Claude Monitor Starting...")

# Configure AXP192 power management first
def setup_axp192():
    print("Setting up AXP192 power management...")
    try:
        i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
        axp192_addr = 0x34
        
        # Enable display power
        i2c.writeto_mem(axp192_addr, 0x12, bytes([0xFF]))  # Enable LDOs
        i2c.writeto_mem(axp192_addr, 0x96, bytes([0x84]))  # GPIO2 output
        i2c.writeto_mem(axp192_addr, 0x95, bytes([0x02]))  # GPIO2 high
        
        print("AXP192 configured successfully")
        return True
    except Exception as e:
        print(f"AXP192 setup failed: {e}")
        return False

# Import display after AXP192 setup
setup_axp192()
time.sleep_ms(200)  # Give power time to stabilize

try:
    from working_display import WorkingDisplay
    print("Real display driver loaded")
except ImportError:
    print("WARNING: Could not load display driver")
    class WorkingDisplay:
        def __init__(self):
            print("MockDisplay: Initialized")
        def show_startup(self):
            print("DISPLAY: Claude Monitor Startup")
        def show_ready(self, ip):
            print(f"DISPLAY: Ready - IP: {ip}")
        def show_error(self, msg):
            print(f"DISPLAY: ERROR - {msg}")
        def update(self, data):
            status = data.get('status', 'unknown')
            duration = data.get('duration', 0)
            cost = data.get('cost', 0)
            print(f"DISPLAY: {status} | {duration}s | ${cost:.2f}")

class Sensors:
    def __init__(self):
        try:
            self.button_a = Pin(37, Pin.IN)
            self.button_b = Pin(39, Pin.IN)
            self.buttons_available = True
            print("Buttons initialized")
        except:
            self.buttons_available = False
            print("Buttons not available")
    
    def read_buttons(self):
        if self.buttons_available:
            a_pressed = self.button_a.value() == 0
            b_pressed = self.button_b.value() == 0
            return a_pressed, b_pressed
        return False, False

def run_claude_monitor_demo():
    print("\n=== CLAUDE MONITOR DEMO ===")
    
    # Initialize components
    display = WorkingDisplay()
    sensors = Sensors()
    
    # Show startup sequence
    print("Showing startup screen...")
    display.show_startup()
    time.sleep(3)
    
    print("Showing ready screen...")
    display.show_ready("192.168.1.100")
    time.sleep(3)
    
    # Demo session monitoring
    session_data = {
        'status': 'idle',
        'duration': 0,
        'cost': 0.0,
        'alerts_enabled': True,
        'alert_pending': False
    }
    
    print("Starting Claude Monitor demo (30 seconds)...")
    start_time = time.time()
    
    for i in range(30):
        # Simulate session activity
        if i > 5:  # Start "active" after 5 seconds
            session_data['status'] = 'active'
            session_data['duration'] = i - 5
            session_data['cost'] = (i - 5) * 0.01
            
            # Alert every 10 seconds
            if (i - 5) % 10 == 0 and i > 5:
                session_data['alert_pending'] = True
                print(f"ALERT: Command approval needed!")
            else:
                session_data['alert_pending'] = False
        
        # Update display
        display.update(session_data)
        
        # Check buttons
        a_pressed, b_pressed = sensors.read_buttons()
        if a_pressed:
            print("Button A: Toggle alerts")
            session_data['alerts_enabled'] = not session_data['alerts_enabled']
        if b_pressed:
            print("Button B: Acknowledge alert")
            session_data['alert_pending'] = False
        
        time.sleep(1)
    
    print("Demo complete!")
    display.show_ready("Demo Complete")

def main():
    print("Starting Claude Monitor...")
    
    try:
        run_claude_monitor_demo()
    except Exception as e:
        print(f"Error: {e}")
        try:
            display = WorkingDisplay()
            display.show_error(str(e))
        except:
            pass
    
    print("Claude Monitor finished")

if __name__ == "__main__":
    main()