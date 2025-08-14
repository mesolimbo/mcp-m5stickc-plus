"""
Fixed Volcano Demo - Corrected offsets and byte order
"""

import time
from machine import Pin
from graphics import M5Display, Colors

def main():
    print("Fixed Volcano Demo starting...")
    
    # Initialize without byte swapping
    display = M5Display(brightness=True, swap_bytes=False)
    button_a = Pin(37, Pin.IN, Pin.PULL_UP)
    
    display.clear(Colors.BLACK)
    display.rect(0, 0, 135, 25, Colors.ORANGE, filled=True)
    display.text(5, 8, "FIXED VOLCANO", Colors.WHITE, Colors.ORANGE)
    
    display.text(5, 35, "NO OFFSETS", Colors.CYAN)
    display.text(5, 55, "LITTLE ENDIAN", Colors.YELLOW)
    display.text(5, 75, "PROPER ASPECT", Colors.GREEN)
    
    display.text(5, 105, "PRESS A TO", Colors.WHITE)
    display.text(5, 125, "LOAD IMAGE", Colors.WHITE)
    
    display.show()
    
    # Wait for button
    while button_a.value() == 1:
        time.sleep_ms(50)
    
    print("Loading volcano image...")
    
    display.clear(Colors.BLACK)
    display.text(30, 110, "LOADING...", Colors.YELLOW)
    display.show()
    
    try:
        # Stream the volcano image
        success = display.draw_rgb565_file('/volcano_scanline.rgb565')
        
        if success:
            print("Image loaded successfully!")
            
            # Add title overlay
            display.rect(0, 0, 135, 20, Colors.BLACK, filled=True)
            display.text(5, 5, "FIXED VOLCANO!", Colors.YELLOW)
            
            # Add info at bottom
            display.rect(0, 220, 135, 20, Colors.BLACK, filled=True)
            display.text(5, 225, "NO OFFSETS", Colors.CYAN)
            
            # Update overlays using framebuffer method
            display.show()
        else:
            print("Failed to load image")
            display.clear(Colors.RED)
            display.text(5, 100, "LOAD FAILED", Colors.WHITE, Colors.RED)
            display.show()
            
    except Exception as e:
        print(f"Error: {e}")
        display.clear(Colors.RED)
        display.text(5, 80, "ERROR:", Colors.WHITE, Colors.RED)
        display.text(5, 100, str(e)[:15], Colors.WHITE, Colors.RED)
        display.show()

if __name__ == "__main__":
    main()