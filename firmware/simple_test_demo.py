"""
Simple test demo to verify graphics library and button functionality
"""

import time
from machine import Pin
from graphics import M5Display, Colors

def main():
    print("Starting simple test demo...")
    
    # Initialize display
    display = M5Display(brightness=True)
    
    # Initialize button
    button_a = Pin(37, Pin.IN, Pin.PULL_UP)
    
    # Clear screen
    display.clear(Colors.BLACK)
    
    # Test basic graphics
    display.rect(0, 0, 135, 30, Colors.GREEN, filled=True)
    display.text(5, 10, "GRAPHICS TEST", Colors.WHITE, Colors.GREEN)
    
    # Test shapes
    display.rect(10, 50, 30, 20, Colors.RED, filled=True)
    display.circle(70, 60, 15, Colors.BLUE, filled=True)
    display.line(10, 90, 125, 90, Colors.YELLOW)
    
    # Button instructions
    display.text(5, 110, "BUTTON TEST:", Colors.WHITE)
    display.text(5, 130, "PRESS A", Colors.CYAN)
    
    # Status area
    display.rect(0, 200, 135, 40, Colors.PURPLE, filled=True)
    display.text(5, 210, "WAITING...", Colors.WHITE, Colors.PURPLE)
    
    display.show()
    
    print("Display initialized, waiting for button...")
    
    button_count = 0
    
    while True:
        # Check button (active low)
        if button_a.value() == 0:
            button_count += 1
            print(f"Button pressed! Count: {button_count}")
            
            # Update display
            display.rect(0, 200, 135, 40, Colors.GREEN, filled=True)
            display.text(5, 210, f"PRESSED {button_count}", Colors.WHITE, Colors.GREEN)
            display.show()
            
            # Wait for button release
            while button_a.value() == 0:
                time.sleep_ms(10)
            
            # Reset display
            display.rect(0, 200, 135, 40, Colors.PURPLE, filled=True)
            display.text(5, 210, "WAITING...", Colors.WHITE, Colors.PURPLE)
            display.show()
            
            # Exit after 3 presses
            if button_count >= 3:
                break
        
        time.sleep_ms(50)
    
    # Success screen
    display.clear(Colors.GREEN)
    display.text(20, 80, "TEST", Colors.WHITE, Colors.GREEN)
    display.text(15, 100, "COMPLETE!", Colors.WHITE, Colors.GREEN)
    display.text(5, 140, "GRAPHICS WORK", Colors.WHITE, Colors.GREEN)
    display.text(5, 160, "BUTTON WORKS", Colors.WHITE, Colors.GREEN)
    display.show()
    
    print("Test completed successfully!")

if __name__ == "__main__":
    main()