# Working main.py for M5StickC PLUS without external dependencies
import gc
import time
from machine import Pin

print("M5StickC PLUS - Claude Monitor Starting...")
print("==== DEBUG MODE ====")

class MockDisplay:
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

class MockSensors:
    def __init__(self):
        try:
            self.button_a = Pin(37, Pin.IN)
            self.button_b = Pin(39, Pin.IN)
            self.buttons_available = True
            print("MockSensors: Real buttons initialized")
        except:
            self.buttons_available = False
            print("MockSensors: Buttons not available, using mock")
    
    def read_buttons(self):
        if self.buttons_available:
            # Buttons are active low
            a_pressed = self.button_a.value() == 0
            b_pressed = self.button_b.value() == 0
            if a_pressed or b_pressed:
                print(f"BUTTON: A={a_pressed}, B={b_pressed}")
            return a_pressed, b_pressed
        return False, False

def run_test_mode():
    print("\n=== TEST MODE ===")
    
    display = MockDisplay()
    wifi = MockWiFi("test-network", "test-pass")
    alerts = MockAlerts()
    sensors = MockSensors()
    
    display.show_startup()
    time.sleep(2)
    
    display.show_ready(wifi.get_ip())
    time.sleep(2)
    
    # Mock session data
    session_data = {
        'status': 'active',
        'duration': 0,
        'cost': 0.0,
        'alerts_enabled': True,
        'alert_pending': False
    }
    
    print("Test mode running... Press buttons to test (will run for 30 seconds)")
    
    for i in range(30):
        # Update mock data
        session_data['duration'] += 1
        session_data['cost'] += 0.01
        
        # Trigger alert every 10 seconds
        if i % 10 == 0 and i > 0:
            session_data['alert_pending'] = True
            alerts.trigger_alert('command_approval')
        
        # Check buttons
        button_a, button_b = sensors.read_buttons()
        
        if button_a:
            session_data['alerts_enabled'] = not session_data['alerts_enabled']
            alerts.set_enabled(session_data['alerts_enabled'])
        
        if button_b and session_data['alert_pending']:
            session_data['alert_pending'] = False
            print("Alert acknowledged")
        
        # Update display every 5 seconds
        if i % 5 == 0:
            display.update(session_data)
        
        alerts.update()
        time.sleep(1)
        gc.collect()
    
    print("Test mode complete!")

def main():
    try:
        print("Starting main application...")
        run_test_mode()
        print("Main application finished")
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"ERROR: {e}")
        import sys
        sys.print_exception(e)
        time.sleep(5)

if __name__ == "__main__":
    main()
else:
    print("Module imported successfully")
