"""
Color Test Demo - Test byte swapping for correct colors
"""

import time
from machine import Pin
from graphics import M5Display, Colors

def main():
    print("Color Test Demo - Testing byte order")
    
    # Initialize button
    button_a = Pin(37, Pin.IN, Pin.PULL_UP)
    
    # Test without byte swapping first
    display = M5Display(brightness=True, swap_bytes=False)
    
    display.clear(Colors.BLACK)
    display.rect(0, 0, 135, 25, Colors.RED, filled=True)
    display.text(5, 8, "NO SWAP BYTES", Colors.WHITE, Colors.RED)
    
    display.text(5, 35, "PRESS A TO TEST", Colors.WHITE)
    display.text(5, 55, "IMAGE WITHOUT", Colors.CYAN)
    display.text(5, 75, "BYTE SWAPPING", Colors.CYAN)
    
    display.show()
    
    # Wait for button press
    while button_a.value() == 1:
        time.sleep_ms(50)
    
    # Test image without byte swapping
    try:
        success = display.draw_rgb565_file('/volcano_scanline.rgb565')
        if success:
            display.text(5, 5, "NO SWAP - LOADED", Colors.YELLOW)
        else:
            display.text(5, 5, "NO SWAP - FAILED", Colors.RED)
    except:
        display.text(5, 5, "NO SWAP - ERROR", Colors.RED)
    
    time.sleep(3)
    
    # Now test WITH byte swapping
    display2 = M5Display(brightness=True, swap_bytes=True)
    
    display2.clear(Colors.BLACK)
    display2.rect(0, 0, 135, 25, Colors.GREEN, filled=True)
    display2.text(5, 8, "WITH SWAP BYTES", Colors.WHITE, Colors.GREEN)
    
    display2.text(5, 35, "PRESS A TO TEST", Colors.WHITE)
    display2.text(5, 55, "IMAGE WITH", Colors.CYAN)
    display2.text(5, 75, "BYTE SWAPPING", Colors.CYAN)
    
    display2.show()
    
    # Wait for button press
    while button_a.value() == 1:
        time.sleep_ms(50)
    
    # Test image with byte swapping
    try:
        success = display2.draw_rgb565_file('/volcano_scanline.rgb565')
        if success:
            display2.text(5, 5, "SWAP - LOADED", Colors.YELLOW)
        else:
            display2.text(5, 5, "SWAP - FAILED", Colors.RED)
    except:
        display2.text(5, 5, "SWAP - ERROR", Colors.RED)
    
    print("Color test completed - check which version looks correct")

if __name__ == "__main__":
    main()