"""
Final Volcano Demo - Image stays visible with proper timing
"""

import time
from machine import Pin
from graphics import M5Display, Colors

def main():
    print("Final Volcano Demo starting...")
    
    display = M5Display(brightness=True, swap_bytes=False)
    button_a = Pin(37, Pin.IN, Pin.PULL_UP)
    
    # Welcome screen
    display.clear(Colors.BLACK)
    display.rect(0, 0, 135, 25, Colors.ORANGE, filled=True)
    display.text(5, 8, "VOLCANO DEMO", Colors.WHITE, Colors.ORANGE)
    
    display.text(5, 35, "SCANLINE STREAM", Colors.CYAN)
    display.text(5, 55, "RGB565 FORMAT", Colors.YELLOW)
    display.text(5, 75, "PROPER ASPECT", Colors.GREEN)
    
    display.text(5, 105, "PRESS BUTTON A", Colors.WHITE)
    display.text(5, 125, "TO LOAD IMAGE", Colors.WHITE)
    
    display.text(5, 155, "IMAGE WILL STAY", Colors.PALE_GREEN)
    display.text(5, 175, "VISIBLE LONGER", Colors.PALE_GREEN)
    
    display.show()
    
    print("Waiting for button press...")
    
    # Wait for button
    while button_a.value() == 1:
        time.sleep_ms(50)
    
    print("Loading volcano image...")
    
    # Show loading message
    display.clear(Colors.BLACK)
    display.rect(0, 100, 135, 40, Colors.BLUE, filled=True)
    display.text(20, 110, "LOADING", Colors.WHITE, Colors.BLUE)
    display.text(10, 125, "VOLCANO IMAGE", Colors.WHITE, Colors.BLUE)
    display.show()
    
    time.sleep(1)  # Show loading message
    
    try:
        # Stream the volcano image
        print("Starting scanline streaming...")
        success = display.draw_rgb565_file('/volcano_scanline.rgb565')
        
        if success:
            print("Image streamed successfully!")
            
            # Let the image display for a moment before adding overlays
            time.sleep(2)
            
            # Add subtle title overlay (small area)
            display.rect(5, 5, 85, 15, Colors.BLACK, filled=True)
            display.text(8, 8, "VOLCANO!", Colors.YELLOW)
            
            # Add small info at bottom corner
            display.rect(80, 225, 55, 15, Colors.BLACK, filled=True)
            display.text(82, 228, "RGB565", Colors.CYAN)
            
            # Update just the overlay areas using framebuffer
            display.show()
            
            print("Overlays added - image should stay visible")
            
            # Keep image visible for much longer
            print("Displaying image for 10 seconds...")
            for i in range(10):
                time.sleep(1)
                print(f"Image visible for {i+1} seconds...")
            
            # Success message
            display.rect(25, 90, 85, 60, Colors.GREEN, filled=True)
            display.text(30, 105, "SUCCESS!", Colors.WHITE, Colors.GREEN)
            display.text(30, 120, "VOLCANO", Colors.WHITE, Colors.GREEN)
            display.text(30, 135, "RENDERED!", Colors.WHITE, Colors.GREEN)
            display.show()
            
        else:
            print("Failed to stream image")
            display.clear(Colors.RED)
            display.text(5, 100, "FAILED TO LOAD", Colors.WHITE, Colors.RED)
            display.text(5, 120, "IMAGE FILE", Colors.WHITE, Colors.RED)
            display.show()
            
    except Exception as e:
        print(f"Error: {e}")
        display.clear(Colors.RED)
        display.text(5, 80, "ERROR:", Colors.WHITE, Colors.RED)
        display.text(5, 100, str(e)[:20], Colors.WHITE, Colors.RED)
        display.text(5, 120, "CHECK CONSOLE", Colors.WHITE, Colors.RED)
        display.show()
    
    print("Demo completed")

if __name__ == "__main__":
    main()