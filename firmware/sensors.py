import time
from machine import Pin

class SensorManager:
    def __init__(self):
        # M5StickC PLUS button pins (active low)
        try:
            self.button_a = Pin(37, Pin.IN)  # Main button
            self.button_b = Pin(39, Pin.IN)  # Side button  
            self.buttons_available = True
        except Exception as e:
            print(f"Buttons not available: {e}")
            self.buttons_available = False
            self.button_a = None
            self.button_b = None
        
        # Button state tracking for debouncing
        self.button_states = {
            'a': {'last': True, 'pressed': False, 'last_change': 0},
            'b': {'last': True, 'pressed': False, 'last_change': 0}
        }
        
        # Debounce time in milliseconds
        self.debounce_ms = 50
        
        # Optional: IMU for future gesture controls
        self.imu_available = False
        try:
            # M5StickC PLUS has MPU6886 IMU
            # This would require additional drivers
            pass
        except:
            pass
    
    def read_buttons(self):
        """Read button states with debouncing"""
        if not self.buttons_available:
            return False, False
            
        current_time = time.ticks_ms()
        button_a_pressed = False
        button_b_pressed = False
        
        # Read button A
        current_a = self.button_a.value()  # 0 = pressed, 1 = released
        if current_a != self.button_states['a']['last']:
            if time.ticks_diff(current_time, self.button_states['a']['last_change']) > self.debounce_ms:
                self.button_states['a']['last'] = current_a
                self.button_states['a']['last_change'] = current_time
                
                # Button press detected (falling edge)
                if current_a == 0:  # Button pressed (active low)
                    button_a_pressed = True
                    self.button_states['a']['pressed'] = True
                else:  # Button released
                    self.button_states['a']['pressed'] = False
        
        # Read button B
        current_b = self.button_b.value()
        if current_b != self.button_states['b']['last']:
            if time.ticks_diff(current_time, self.button_states['b']['last_change']) > self.debounce_ms:
                self.button_states['b']['last'] = current_b
                self.button_states['b']['last_change'] = current_time
                
                # Button press detected (falling edge)
                if current_b == 0:  # Button pressed (active low)
                    button_b_pressed = True
                    self.button_states['b']['pressed'] = True
                else:  # Button released
                    self.button_states['b']['pressed'] = False
        
        return button_a_pressed, button_b_pressed
    
    def is_button_held(self, button='a'):
        """Check if button is currently being held down"""
        if not self.buttons_available:
            return False
            
        if button == 'a':
            return self.button_a.value() == 0
        elif button == 'b':
            return self.button_b.value() == 0
        return False
    
    def wait_for_button_press(self, timeout_ms=5000):
        """Wait for any button press with timeout"""
        start_time = time.ticks_ms()
        
        while time.ticks_diff(time.ticks_ms(), start_time) < timeout_ms:
            button_a, button_b = self.read_buttons()
            if button_a or button_b:
                return 'a' if button_a else 'b'
            time.sleep_ms(10)
        
        return None  # Timeout
    
    def test_buttons(self):
        """Test button functionality - prints when buttons are pressed"""
        print("Button test mode - press buttons A and B (Ctrl+C to exit)")
        print("Button A = main button, Button B = side button")
        
        try:
            while True:
                button_a, button_b = self.read_buttons()
                
                if button_a:
                    print("Button A pressed!")
                    
                if button_b:
                    print("Button B pressed!")
                    
                # Show held state
                held_a = self.is_button_held('a')
                held_b = self.is_button_held('b')
                
                if held_a or held_b:
                    status = []
                    if held_a:
                        status.append("A-held")
                    if held_b:
                        status.append("B-held")
                    print(f"Status: {', '.join(status)}")
                    
                time.sleep_ms(100)
                
        except KeyboardInterrupt:
            print("\nButton test ended")
    
    def get_startup_mode(self):
        """Check if special startup mode requested (hold button during boot)"""
        if not self.buttons_available:
            return 'normal'
            
        # Check if button A held during startup (test mode)
        if self.button_a.value() == 0:
            return 'test'
        
        # Check if button B held during startup (config mode)
        if self.button_b.value() == 0:
            return 'config'
            
        return 'normal'
