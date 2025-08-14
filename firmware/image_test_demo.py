"""
Image Test Demo - Prove RGB565 rendering works
"""

import time
from machine import Pin
from graphics import M5Display, Colors

def main():
    print("Starting Image Test Demo!")
    
    # Initialize
    display = M5Display(brightness=True)
    button_a = Pin(37, Pin.IN, Pin.PULL_UP)
    
    # Welcome
    display.clear(Colors.BLACK)
    display.rect(0, 0, 135, 25, Colors.GREEN, filled=True)
    display.text(5, 8, "IMAGE TEST", Colors.WHITE, Colors.GREEN)
    
    display.text(5, 35, "RGB565 BITMAP", Colors.CYAN)
    display.text(5, 55, "RENDERING TEST", Colors.YELLOW)
    
    display.text(5, 85, "PRESS BUTTON A", Colors.WHITE)
    display.text(5, 105, "TO TEST IMAGE", Colors.WHITE)
    
    display.show()
    
    # Wait for button
    while button_a.value() == 1:
        time.sleep_ms(50)
    
    print("Loading test image...")
    
    try:
        # Import tiny test image
        from tiny_test_image import TEST_DATA, WIDTH, HEIGHT
        
        display.clear(Colors.BLACK)
        display.text(30, 110, "LOADING...", Colors.YELLOW)
        display.show()
        
        print(f"Image data: {len(TEST_DATA)} bytes, {WIDTH}x{HEIGHT}")
        
        # Test the draw_bitmap function
        display.clear(Colors.BLACK)
        
        # Draw test image multiple times at different positions
        display.draw_bitmap(10, 20, WIDTH, HEIGHT, TEST_DATA)   # Top left
        display.draw_bitmap(80, 20, WIDTH, HEIGHT, TEST_DATA)   # Top right  
        display.draw_bitmap(10, 120, WIDTH, HEIGHT, TEST_DATA)  # Bottom left
        display.draw_bitmap(80, 120, WIDTH, HEIGHT, TEST_DATA)  # Bottom right
        
        # Add labels
        display.text(5, 5, "RGB565 TEST", Colors.WHITE)
        display.text(5, 200, "32X32 IMAGES", Colors.CYAN)
        display.text(5, 215, "GRADIENT TEST", Colors.YELLOW)
        
        display.show()
        
        print("Image rendering test successful!")
        
        # Success message
        time.sleep(2)
        display.rect(0, 80, 135, 60, Colors.GREEN, filled=True)
        display.text(15, 95, "SUCCESS!", Colors.WHITE, Colors.GREEN)
        display.text(5, 115, "RGB565 BITMAP", Colors.WHITE, Colors.GREEN)
        display.text(5, 130, "RENDERING WORKS!", Colors.WHITE, Colors.GREEN)
        display.show()
        
    except ImportError as e:
        print(f"Import error: {e}")
        display.clear(Colors.RED)
        display.text(5, 100, "IMAGE FILE", Colors.WHITE, Colors.RED)
        display.text(5, 120, "NOT FOUND", Colors.WHITE, Colors.RED)
        display.show()
        
    except Exception as e:
        print(f"Error: {e}")
        display.clear(Colors.RED) 
        display.text(5, 100, "ERROR:", Colors.WHITE, Colors.RED)
        display.text(5, 120, str(e)[:15], Colors.WHITE, Colors.RED)
        display.show()

if __name__ == "__main__":
    main()