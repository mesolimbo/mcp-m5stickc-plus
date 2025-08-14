"""
Simple Debug Demo - Safe diagnostics
"""

import time
from machine import Pin
from graphics import M5Display, Colors

def main():
    print("Simple Debug Demo starting...")
    
    # Initialize
    display = M5Display(brightness=True, swap_bytes=True)
    button_a = Pin(37, Pin.IN, Pin.PULL_UP)
    
    display.clear(Colors.BLACK)
    display.text(5, 50, "SIMPLE DEBUG", Colors.WHITE)
    display.text(5, 70, "PRESS A", Colors.CYAN)
    display.show()
    
    # Wait for button
    while button_a.value() == 1:
        time.sleep_ms(50)
    
    print("Checking file...")
    
    # Step 1: Just check if file exists
    try:
        f = open('/volcano_scanline.rgb565', 'rb')
        f.close()
        print("File exists")
        
        display.clear(Colors.GREEN)
        display.text(5, 100, "FILE: EXISTS", Colors.WHITE, Colors.GREEN)
        display.show()
        
    except:
        print("File missing")
        
        display.clear(Colors.RED)
        display.text(5, 100, "FILE: MISSING", Colors.WHITE, Colors.RED)
        display.show()
        time.sleep(3)
        return
    
    time.sleep(2)
    
    # Step 2: Try to draw a simple test pattern instead
    print("Drawing test pattern...")
    
    display.clear(Colors.BLACK)
    display.text(5, 100, "TEST PATTERN", Colors.YELLOW)
    display.show()
    
    # Create simple red/blue pattern
    test_data = bytearray(135 * 2)  # One scanline
    for x in range(135):
        if x < 67:
            color = Colors.RED
        else:
            color = Colors.BLUE
        test_data[x*2] = color & 0xFF
        test_data[x*2 + 1] = (color >> 8) & 0xFF
    
    # Draw test pattern lines
    for y in range(50, 150, 10):  # Every 10th line
        try:
            display.set_window(0, y, 135, 1)
            display.write(test_data)
            print(f"Drew line {y}")
        except Exception as e:
            print(f"Error at line {y}: {e}")
            break
    
    display.text(5, 200, "PATTERN DONE", Colors.GREEN)
    print("Test pattern complete")
    
    time.sleep(3)
    
    # Step 3: Try reading just first line of actual file
    print("Reading first line of image...")
    
    try:
        with open('/volcano_scanline.rgb565', 'rb') as f:
            first_line = f.read(135 * 2)
            print(f"Read {len(first_line)} bytes")
            
            if len(first_line) == 135 * 2:
                # Draw first line of image at y=100
                display.set_window(0, 100, 135, 1)
                display.write(first_line)
                print("Drew first image line")
                
                display.text(5, 220, "IMG LINE: OK", Colors.GREEN)
            else:
                print(f"Wrong size: {len(first_line)}")
                display.text(5, 220, "IMG: WRONG SIZE", Colors.RED)
                
    except Exception as e:
        print(f"File read error: {e}")
        display.text(5, 220, "IMG: READ ERROR", Colors.RED)
    
    print("Simple debug complete")

if __name__ == "__main__":
    main()