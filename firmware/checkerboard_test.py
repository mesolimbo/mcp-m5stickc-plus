# Checkerboard pattern test to check display orientation
import time
from machine import Pin, SPI

print("M5StickC PLUS Checkerboard Test")
print("===============================")

def test_checkerboard():
    """Create a green and white checkerboard pattern"""
    try:
        # Initialize SPI and pins
        spi = SPI(1, baudrate=10000000, sck=Pin(13), mosi=Pin(15))
        reset = Pin(18, Pin.OUT)
        cs = Pin(5, Pin.OUT)
        dc = Pin(23, Pin.OUT)
        backlight = Pin(12, Pin.OUT)
        
        # Turn on backlight
        backlight.value(1)
        
        # Reset display
        reset.value(0)
        time.sleep_ms(10)
        reset.value(1)
        time.sleep_ms(120)
        
        # Helper functions
        def send_cmd(cmd):
            cs.value(0)
            dc.value(0)
            spi.write(bytearray([cmd]))
            cs.value(1)
            
        def send_data(data):
            cs.value(0)
            dc.value(1)
            if isinstance(data, int):
                spi.write(bytearray([data]))
            else:
                spi.write(data)
            cs.value(1)
        
        def set_window(x0, y0, x1, y1):
            send_cmd(0x2A)  # Column set
            send_data(x0 >> 8)
            send_data(x0 & 0xFF)
            send_data(x1 >> 8)
            send_data(x1 & 0xFF)
            
            send_cmd(0x2B)  # Row set
            send_data(y0 >> 8)
            send_data(y0 & 0xFF)
            send_data(y1 >> 8)
            send_data(y1 & 0xFF)
            
            send_cmd(0x2C)  # Memory write
        
        print("Initializing display...")
        send_cmd(0x11)  # Sleep out
        time.sleep_ms(120)
        
        send_cmd(0x3A)  # Color mode
        send_data(0x05)  # 16-bit RGB565
        
        send_cmd(0x36)  # Memory access control
        send_data(0xA0)  # Current rotation
        
        send_cmd(0x21)  # Inversion on
        send_cmd(0x13)  # Normal display mode
        send_cmd(0x29)  # Display on
        
        # Colors (RGB565)
        GREEN = 0x07E0
        WHITE = 0xFFFF
        
        print("Creating checkerboard pattern...")
        
        # Test different dimensions to see what works
        width = 135
        height = 240
        
        # Try the full screen first
        set_window(0, 0, width - 1, height - 1)
        
        cs.value(0)
        dc.value(1)
        
        # Create 8x8 checkerboard squares
        square_size = 16
        
        for y in range(height):
            for x in range(width):
                # Determine if this pixel should be green or white
                square_x = x // square_size
                square_y = y // square_size
                
                if (square_x + square_y) % 2 == 0:
                    color = GREEN
                else:
                    color = WHITE
                
                # Send pixel color
                spi.write(bytearray([color >> 8, color & 0xFF]))
        
        cs.value(1)
        
        print("Checkerboard complete!")
        print(f"Pattern: {width}x{height} with {square_size}x{square_size} squares")
        
        # Wait and then try different rotation
        time.sleep(3)
        
        print("Trying different rotation...")
        send_cmd(0x36)  # Memory access control
        send_data(0x60)  # Different rotation
        
        # Fill with solid red to show the change
        set_window(0, 0, width - 1, height - 1)
        red_bytes = bytearray([0xF8, 0x00])  # Red
        cs.value(0)
        dc.value(1)
        for _ in range(width * height):
            spi.write(red_bytes)
        cs.value(1)
        
        time.sleep(2)
        
        # Try another rotation
        print("Trying landscape mode...")
        send_cmd(0x36)  # Memory access control
        send_data(0xC0)  # Landscape rotation
        
        # Now try 240x135 (swapped dimensions)
        width = 240
        height = 135
        
        set_window(0, 0, width - 1, height - 1)
        
        cs.value(0)
        dc.value(1)
        
        # Blue checkerboard in landscape
        BLUE = 0x001F
        YELLOW = 0xFFE0
        
        for y in range(height):
            for x in range(width):
                square_x = x // square_size
                square_y = y // square_size
                
                if (square_x + square_y) % 2 == 0:
                    color = BLUE
                else:
                    color = YELLOW
                
                spi.write(bytearray([color >> 8, color & 0xFF]))
        
        cs.value(1)
        
        print("Landscape checkerboard complete!")
        print(f"Pattern: {width}x{height} landscape mode")
        
        return True
        
    except Exception as e:
        print(f"Checkerboard test failed: {e}")
        import sys
        sys.print_exception(e)
        return False

def main():
    print("Testing different display orientations with checkerboard...")
    test_checkerboard()
    print("\nTest complete! Check the patterns on your display.")

if __name__ == "__main__":
    main()