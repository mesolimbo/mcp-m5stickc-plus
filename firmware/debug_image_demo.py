"""
Debug Image Demo - Check what's going wrong
"""

import time
import gc
from machine import Pin
from graphics import M5Display, Colors

def main():
    print("Debug Image Demo - Checking file and streaming")
    
    # Initialize
    display = M5Display(brightness=True, swap_bytes=True)
    button_a = Pin(37, Pin.IN, Pin.PULL_UP)
    
    display.clear(Colors.BLACK)
    display.rect(0, 0, 135, 25, Colors.BLUE, filled=True)
    display.text(5, 8, "DEBUG DEMO", Colors.WHITE, Colors.BLUE)
    
    display.text(5, 35, "CHECKING FILES", Colors.WHITE)
    display.text(5, 55, "AND STREAMING", Colors.WHITE)
    display.text(5, 75, "PRESS BUTTON A", Colors.CYAN)
    
    display.show()
    
    # Wait for button
    while button_a.value() == 1:
        time.sleep_ms(50)
    
    print("Button pressed - starting diagnostics...")
    
    # Check if file exists
    try:
        with open('/volcano_scanline.rgb565', 'rb') as f:
            # Check file size
            f.seek(0, 2)  # Seek to end
            size = f.tell()
            f.seek(0)     # Back to start
            
            print(f"File exists, size: {size} bytes")
            
            # Read first few bytes to check format
            first_bytes = f.read(10)
            print(f"First bytes: {[hex(b) for b in first_bytes]}")
            
        display.clear(Colors.BLACK)
        display.text(5, 50, "FILE FOUND!", Colors.GREEN)
        display.text(5, 70, f"SIZE: {size}", Colors.YELLOW)
        display.text(5, 90, "BYTES: OK", Colors.YELLOW)
        display.show()
        
    except Exception as e:
        print(f"File error: {e}")
        display.clear(Colors.RED)
        display.text(5, 50, "FILE ERROR:", Colors.WHITE, Colors.RED)
        display.text(5, 70, str(e)[:20], Colors.WHITE, Colors.RED)
        display.show()
        time.sleep(3)
        return
    
    time.sleep(2)
    
    # Test basic scanline streaming
    print("Testing scanline streaming...")
    
    try:
        display.clear(Colors.BLACK)
        display.text(5, 100, "STREAMING...", Colors.CYAN)
        display.show()
        
        # Try to draw the image
        success = display.draw_rgb565_file('/volcano_scanline.rgb565')
        
        if success:
            print("Scanline streaming reported success!")
            display.rect(0, 0, 135, 20, Colors.GREEN, filled=True)
            display.text(5, 5, "STREAM SUCCESS", Colors.WHITE, Colors.GREEN)
            
            # Try to update just the title overlay
            display.set_window(0, 0, 135, 20) 
            line_data = display.framebuffer[0:135*20*2]
            display.write(line_data)
        else:
            print("Scanline streaming reported failure!")
            display.clear(Colors.RED)
            display.text(5, 100, "STREAM FAILED", Colors.WHITE, Colors.RED)
            display.show()
            
    except Exception as e:
        print(f"Streaming error: {e}")
        display.clear(Colors.RED)
        display.text(5, 80, "STREAM ERROR:", Colors.WHITE, Colors.RED)
        display.text(5, 100, str(e)[:15], Colors.WHITE, Colors.RED)
        display.show()
        
    # Memory check
    gc.collect()
    free_mem = gc.mem_free()
    print(f"Free memory: {free_mem} bytes")
    
    time.sleep(5)
    
    # Manual scanline test
    print("Testing manual scanline...")
    
    try:
        display.clear(Colors.BLACK)
        display.text(5, 100, "MANUAL TEST...", Colors.YELLOW)
        display.show()
        
        with open('/volcano_scanline.rgb565', 'rb') as f:
            # Draw just first 10 lines manually
            for row in range(10):
                line_data = f.read(135 * 2)  # One scanline
                if len(line_data) < 135 * 2:
                    print(f"Short read at line {row}: {len(line_data)} bytes")
                    break
                
                print(f"Drawing line {row}")
                display.set_window(0, row + 50, 135, 1)
                display.write(line_data)
                
                if row % 5 == 0:  # Update every 5 lines
                    time.sleep_ms(100)
        
        print("Manual scanline test completed")
        display.text(5, 200, "MANUAL: DONE", Colors.GREEN)
        
    except Exception as e:
        print(f"Manual test error: {e}")
        display.text(5, 200, f"MANUAL: {e}", Colors.RED)
    
    print("Debug demo completed")

if __name__ == "__main__":
    main()