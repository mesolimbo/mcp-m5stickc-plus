"""
Button Test Demo - Check if button is working
"""

import time
from machine import Pin
from graphics import M5Display, Colors

def main():
    print("Button Test Demo starting...")
    
    display = M5Display(brightness=True, swap_bytes=False)
    button_a = Pin(37, Pin.IN, Pin.PULL_UP)
    
    display.clear(Colors.BLACK)
    display.text(5, 50, "BUTTON TEST", Colors.WHITE)
    display.text(5, 70, "PRESS A", Colors.CYAN)
    display.text(5, 90, "WAITING...", Colors.YELLOW)
    display.show()
    
    print("Waiting for button press...")
    
    button_count = 0
    
    while button_count < 5:  # Exit after 5 presses
        if button_a.value() == 0:  # Button pressed (active low)
            button_count += 1
            print(f"Button pressed! Count: {button_count}")
            
            # Update display
            display.rect(5, 90, 125, 40, Colors.BLACK, filled=True)
            display.text(5, 90, f"PRESSED: {button_count}", Colors.GREEN)
            display.text(5, 110, "WORKING!", Colors.GREEN)
            display.show()
            
            # Wait for button release
            while button_a.value() == 0:
                time.sleep_ms(10)
            
            # Reset display
            display.rect(5, 90, 125, 40, Colors.BLACK, filled=True)
            display.text(5, 90, "WAITING...", Colors.YELLOW)
            display.text(5, 110, f"COUNT: {button_count}", Colors.WHITE)
            display.show()
            
            time.sleep_ms(100)  # Debounce
    
    # Test scanline streaming
    print("Testing scanline streaming...")
    
    display.clear(Colors.BLACK)
    display.text(5, 50, "TESTING", Colors.WHITE)
    display.text(5, 70, "SCANLINE...", Colors.CYAN)
    display.show()
    
    try:
        # Create test scanline data
        test_line = bytearray(135 * 2)
        for x in range(135):
            # Red gradient
            red_intensity = int((x / 135) * 31)  # 5-bit red
            color = (red_intensity << 11)  # Red in RGB565
            test_line[x*2] = (color >> 8) & 0xFF    # High byte
            test_line[x*2 + 1] = color & 0xFF       # Low byte
        
        # Draw test lines using set_window
        for y in range(100, 120):
            display.set_window(0, y, 135, 1)
            display.write(test_line)
        
        print("Scanline test completed")
        display.text(5, 130, "SCANLINE: OK", Colors.GREEN)
        display.show()
        
    except Exception as e:
        print(f"Scanline error: {e}")
        display.text(5, 130, f"ERROR: {e}", Colors.RED)
        display.show()
    
    print("Tests completed")

if __name__ == "__main__":
    main()