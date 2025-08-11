# Final working M5StickC PLUS Claude Monitor
import gc
import time
from machine import Pin
from working_display import WorkingDisplay

print("M5StickC PLUS Claude Monitor - Final Version")
print("============================================")

class ButtonHandler:
    def __init__(self):
        try:
            self.button_a = Pin(37, Pin.IN)
            self.button_b = Pin(39, Pin.IN)
            self.available = True
            self.last_a = True
            self.last_b = True
            print("Buttons initialized")
        except:
            self.available = False
            print("Buttons not available")
    
    def read(self):
        """Read button presses (returns pressed states)"""
        if not self.available:
            return False, False
        
        current_a = self.button_a.value()
        current_b = self.button_b.value()
        
        # Detect press (falling edge from 1 to 0)
        a_pressed = self.last_a and not current_a
        b_pressed = self.last_b and not current_b
        
        self.last_a = current_a
        self.last_b = current_b
        
        return a_pressed, b_pressed

def run_monitor():
    """Run the Claude monitor application"""
    try:
        # Initialize components
        display = WorkingDisplay()
        buttons = ButtonHandler()
        
        print("Components initialized successfully!")
        
        # Show startup sequence
        display.show_startup()
        time.sleep(2)
        
        display.show_ready("TEST.MODE")
        time.sleep(2)
        
        # Mock session data
        session = {
            'status': 'active',
            'duration': 0,
            'cost': 0.0,
            'alerts_enabled': True,
            'alert_pending': False,
            'project_name': 'claude-monitor'
        }
        
        print("\nClaude Monitor running!")
        print("Button A: Toggle audio alerts")
        print("Button B: Acknowledge alert")
        print("Both buttons: Exit")
        
        loop_count = 0
        
        while True:
            loop_count += 1
            
            # Update session data (simulate activity)
            session['duration'] += 1
            session['cost'] += 0.005
            
            # Trigger alert every 15 seconds
            if loop_count % 15 == 0:
                session['alert_pending'] = True
                print("ALERT: Command approval needed!")
            
            # Check buttons
            button_a, button_b = buttons.read()
            
            if button_a:
                session['alerts_enabled'] = not session['alerts_enabled']
                status = "ON" if session['alerts_enabled'] else "OFF"
                print(f"Audio alerts: {status}")
                display.show_message(f"Audio {status}", 1)
            
            if button_b:
                if session['alert_pending']:
                    session['alert_pending'] = False
                    print("Alert acknowledged")
                    display.show_message("Acknowledged", 1)
            
            # Check for exit (both buttons held)
            if buttons.available:
                if not buttons.button_a.value() and not buttons.button_b.value():
                    print("\nExiting...")
                    break
            
            # Update display every few loops
            if loop_count % 3 == 0:
                display.update(session)
            
            # Change status occasionally for demo
            if loop_count % 30 == 0:
                statuses = ['active', 'idle', 'server_offline']
                session['status'] = statuses[loop_count // 30 % 3]
            
            time.sleep(1)
            gc.collect()
            
            # Auto-exit after 5 minutes for demo
            if loop_count >= 300:
                print("\nDemo complete (5 minutes)")
                break
        
        # Show completion
        display.fill(display.BLACK)
        display.fill_rect(20, 100, 95, 40, display.GREEN)
        print("Monitor stopped.")
        
    except Exception as e:
        print(f"Monitor error: {e}")
        import sys
        sys.print_exception(e)
        
        # Show error on display if possible
        try:
            display.show_error("System Error")
        except:
            pass
        
        time.sleep(5)

def main():
    """Main entry point"""
    print("Starting Claude Monitor...")
    
    try:
        run_monitor()
    except KeyboardInterrupt:
        print("\nStopped by user")
    except Exception as e:
        print(f"Main error: {e}")
        import sys
        sys.print_exception(e)
    
    print("Program ended.")

if __name__ == "__main__":
    main()
else:
    print("Claude Monitor module loaded")
