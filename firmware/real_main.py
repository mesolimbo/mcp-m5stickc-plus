# Real display main.py for M5StickC PLUS Claude Monitor
import gc
import time
from machine import Pin

print("M5StickC PLUS - Claude Monitor Starting...")

# Import real display
try:
    from working_display import WorkingDisplay
    print("Real display driver loaded")
except ImportError:
    print("WARNING: Could not load real display driver, using mock")
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

class MockWiFi:
    def __init__(self, ssid, password):
        self.ssid = ssid
        print(f"MockWiFi: Configured for {ssid}")
    
    def connect(self):
        print("MockWiFi: Connecting...")
        return True
    
    def get_ip(self):
        return "192.168.1.123"

class MockAlerts:
    def __init__(self):
        print("MockAlerts: Initialized")
        self.enabled = True
    
    def set_enabled(self, enabled):
        self.enabled = enabled
        print(f"MockAlerts: {'Enabled' if enabled else 'Disabled'}")
    
    def trigger_alert(self, alert_type):
        if self.enabled:
            print(f"ALERT: {alert_type}")
    
    def update(self):
        pass

class RealSensors:
    def __init__(self):
        try:
            self.button_a = Pin(37, Pin.IN)
            self.button_b = Pin(39, Pin.IN)
            self.buttons_available = True
            print("RealSensors: Buttons initialized")
        except:
            self.buttons_available = False
            print("RealSensors: Buttons not available")
    
    def read_buttons(self):
        if self.buttons_available:
            # Buttons are active low
            a_pressed = self.button_a.value() == 0
            b_pressed = self.button_b.value() == 0
            if a_pressed or b_pressed:
                print(f"BUTTON: A={a_pressed}, B={b_pressed}")
            return a_pressed, b_pressed
        return False, False

def run_real_display_test():
    print("\n=== REAL DISPLAY TEST MODE ===")
    
    # Initialize with real display
    display = WorkingDisplay()
    wifi = MockWiFi("test-network", "test-pass")
    alerts = MockAlerts()
    sensors = RealSensors()
    
    print("Showing startup screen...")
    display.show_startup()
    time.sleep(3)
    
    print("Showing ready screen...")
    display.show_ready(wifi.get_ip())
    time.sleep(3)
    
    # Test session display
    session_data = {
        'status': 'active',
        'duration': 0,
        'cost': 0.0,
        'alerts_enabled': True,
        'alert_pending': False
    }
    
    print("Starting session display test (30 seconds)...")
    start_time = time.time()
    
    for i in range(30):
        # Update session data
        session_data['duration'] = i + 1
        session_data['cost'] = (i + 1) * 0.01
        
        # Trigger alert every 5 seconds
        if (i + 1) % 5 == 0:
            session_data['alert_pending'] = True
            alerts.trigger_alert("command_approval")
        else:
            session_data['alert_pending'] = False
        
        # Update display
        display.update(session_data)
        
        # Check buttons
        a_pressed, b_pressed = sensors.read_buttons()
        if a_pressed:
            alerts.set_enabled(not alerts.enabled)
            session_data['alerts_enabled'] = alerts.enabled
        if b_pressed:
            display.show_message("Button B pressed!", 1)
        
        time.sleep(1)
    
    print("Display test complete!")
    display.show_ready("Test Complete")

def main():
    print("Starting main application...")
    
    try:
        run_real_display_test()
    except Exception as e:
        print(f"Error in main: {e}")
        # Try to show error on display
        try:
            display = WorkingDisplay()
            display.show_error(str(e))
        except:
            pass
    
    print("Main application finished")

if __name__ == "__main__":
    main()