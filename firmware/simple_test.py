# Simple test to verify basic functionality
import time
try:
    from machine import Pin
    print("Machine module loaded successfully")
    
    # Test basic pin setup (buttons)
    button_a = Pin(37, Pin.IN)
    button_b = Pin(39, Pin.IN)
    print("Button pins configured")
    
    print("M5StickC PLUS Simple Test Running...")
    print("Press Ctrl+C to stop")
    
    counter = 0
    while True:
        counter += 1
        print(f"Test loop {counter} - Button A: {button_a.value()}, Button B: {button_b.value()}")
        time.sleep(1)
        
except ImportError as e:
    print(f"Import error: {e}")
except Exception as e:
    print(f"Error: {e}")
    raise
