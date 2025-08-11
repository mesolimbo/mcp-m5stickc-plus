# Main application with real display for M5StickC PLUS
import gc
import time
from machine import Pin
from real_display import RealDisplayManager

print("M5StickC PLUS - Real Display Test")
print("==================================")

class MockSensors:
    def __init__(self):
        try:
            self.button_a = Pin(37, Pin.IN)
            self.button_b = Pin(39, Pin.IN)
            self.buttons_available = True
            print("Real buttons initialized")
        except:
            self.buttons_available = False
            print("Buttons not available")
    
    def read_buttons(self):
        if self.buttons_available:
            # Buttons are active low
            a_pressed = self.button_a.value() == 0
            b_pressed = self.button_b.value() == 0
            if a_pressed or b_pressed:
                print(f"BUTTON: A={a_pressed}, B={b_pressed}")
            return a_pressed, b_pressed
        return False, False

def run_display_test():
    """Test the real display with various screens"""
    print("Starting display test...")
    
    try:
        # Initialize display
        display = RealDisplayManager(brightness=80)
        sensors = MockSensors()
        
        print("Display initialized successfully!")
        
        # Test 1: Startup screen
        print("\nTest 1: Startup screen")
        display.show_startup()
        time.sleep(3)
        
        # Test 2: Ready screen
        print("\nTest 2: Ready screen")
        display.show_ready("192.168.1.123")
        time.sleep(3)
        
        # Test 3: Error screen
        print("\nTest 3: Error screen")
        display.show_error("WiFi Connection Failed")
        time.sleep(3)
        
        # Test 4: Message screen
        print("\nTest 4: Message screen")
        display.show_message("Audio OFF", 2)
        
        # Test 5: Session display loop
        print("\nTest 5: Session display (30 seconds)")
        
        session_data = {
            'status': 'active',
            'duration': 0,
            'cost': 0.0,
            'alerts_enabled': True,
            'alert_pending': False,
            'project_name': 'display-test'
        }
        
        for i in range(30):
            # Update session data
            session_data['duration'] += 1
            session_data['cost'] += 0.01
            
            # Trigger alert every 10 seconds
            if i % 10 == 0 and i > 0:
                session_data['alert_pending'] = True
                session_data['alert_type'] = 'command_approval'
                print("ALERT TRIGGERED")
            
            # Check buttons
            button_a, button_b = sensors.read_buttons()
            
            if button_a:
                session_data['alerts_enabled'] = not session_data['alerts_enabled']
                status = "ON" if session_data['alerts_enabled'] else "OFF"
                print(f"Audio toggled: {status}")
                display.show_message(f"Audio {status}", 1)
            
            if button_b and session_data['alert_pending']:
                session_data['alert_pending'] = False
                print("Alert acknowledged")
            
            # Update display
            display.update(session_data)
            
            time.sleep(1)
            gc.collect()
        
        print("\nDisplay test complete!")
        
        # Final screen
        display.clear()
        display.show_text("TEST", 40, 80, display.colors['green'], 2)
        display.show_text("COMPLETE", 20, 110, display.colors['green'], 2)
        
    except Exception as e:
        print(f"Display test failed: {e}")
        import sys
        sys.print_exception(e)
        time.sleep(5)

def main():
    """Main entry point"""
    try:
        run_display_test()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Main error: {e}")
        import sys
        sys.print_exception(e)
        time.sleep(5)

if __name__ == "__main__":
    main()
else:
    print("Display test module loaded")
