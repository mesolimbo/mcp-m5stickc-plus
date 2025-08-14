"""
Endian Test Demo - Test both byte orders with portrait volcano
"""

import time
from machine import Pin
from graphics import M5Display, Colors

def main():
    print("Endian Test Demo - Portrait Volcano")
    
    display = M5Display(brightness=True, swap_bytes=False)
    button_a = Pin(37, Pin.IN, Pin.PULL_UP)
    
    # Test 1: Big-endian version
    display.clear(Colors.BLACK)
    display.rect(0, 0, 135, 25, Colors.RED, filled=True)
    display.text(5, 8, "BIG-ENDIAN TEST", Colors.WHITE, Colors.RED)
    
    display.text(5, 35, "PORTRAIT VOLCANO", Colors.WHITE)
    display.text(5, 55, "BIG-ENDIAN FMT", Colors.CYAN)
    display.text(5, 75, "PRESS A TO TEST", Colors.YELLOW)
    display.show()
    
    # Wait for button
    while button_a.value() == 1:
        time.sleep_ms(50)
    
    print("Testing big-endian version...")
    
    try:
        success = display.draw_rgb565_file('/volcano-portrait-be.rgb565')
        if success:
            display.rect(5, 5, 85, 15, Colors.BLACK, filled=True)
            display.text(8, 8, "BIG-ENDIAN", Colors.YELLOW)
        else:
            display.text(5, 200, "BE: FAILED", Colors.RED)
    except Exception as e:
        print(f"Big-endian error: {e}")
        display.text(5, 200, "BE: ERROR", Colors.RED)
    
    display.show()
    time.sleep(5)
    
    # Test 2: Little-endian version
    display.clear(Colors.BLACK)
    display.rect(0, 0, 135, 25, Colors.GREEN, filled=True)
    display.text(5, 8, "LITTLE-ENDIAN", Colors.WHITE, Colors.GREEN)
    
    display.text(5, 35, "PORTRAIT VOLCANO", Colors.WHITE)
    display.text(5, 55, "LITTLE-ENDIAN", Colors.CYAN)
    display.text(5, 75, "PRESS A TO TEST", Colors.YELLOW)
    display.show()
    
    # Wait for button
    while button_a.value() == 1:
        time.sleep_ms(50)
    
    print("Testing little-endian version...")
    
    try:
        success = display.draw_rgb565_file('/volcano-portrait-le.rgb565')
        if success:
            display.rect(5, 5, 95, 15, Colors.BLACK, filled=True)
            display.text(8, 8, "LITTLE-ENDIAN", Colors.YELLOW)
        else:
            display.text(5, 200, "LE: FAILED", Colors.RED)
    except Exception as e:
        print(f"Little-endian error: {e}")
        display.text(5, 200, "LE: ERROR", Colors.RED)
    
    display.show()
    time.sleep(5)
    
    # Instructions
    display.clear(Colors.BLUE)
    display.text(5, 80, "COMPARE RESULTS", Colors.WHITE, Colors.BLUE)
    display.text(5, 100, "WHICH VERSION", Colors.WHITE, Colors.BLUE)
    display.text(5, 120, "HAD CORRECT", Colors.WHITE, Colors.BLUE)
    display.text(5, 140, "COLORS?", Colors.WHITE, Colors.BLUE)
    display.show()
    
    print("Test completed - compare the two versions")

if __name__ == "__main__":
    main()