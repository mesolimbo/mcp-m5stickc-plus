# M5StickC PLUS - Display Rotation Test
import time
from machine import Pin, SPI, I2C

print("M5StickC PLUS - Display Rotation Test")

def rotation_test():
    # AXP192 setup (required for display power)
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    i2c.writeto_mem(0x34, 0x12, bytes([0xFF]))  # Enable LDOs
    i2c.writeto_mem(0x34, 0x96, bytes([0x84]))  # GPIO2 as output
    i2c.writeto_mem(0x34, 0x95, bytes([0x02]))  # GPIO2 high (backlight)
    time.sleep_ms(200)
    print("AXP192 configured")
    
    # SPI setup
    spi = SPI(1, baudrate=8000000, sck=Pin(13), mosi=Pin(15))
    reset = Pin(18, Pin.OUT, value=1)
    cs = Pin(5, Pin.OUT, value=1)
    dc = Pin(23, Pin.OUT, value=0)
    
    def cmd(c):
        cs.value(0); dc.value(0)
        spi.write(bytearray([c]))
        cs.value(1); time.sleep_ms(1)
    
    def data(d):
        cs.value(0); dc.value(1)
        spi.write(bytearray([d]))
        cs.value(1); time.sleep_ms(1)
    
    def set_window_correct(x_start, y_start, x_end, y_end):
        """Set display window with correct M5StickC PLUS offsets"""
        # M5StickC PLUS ST7789 offsets: x_start=52, y_start=40 for rotation 0
        x_offset = 52
        y_offset = 40
        
        # Apply offsets to coordinates
        col_start = x_start + x_offset
        col_end = x_end + x_offset
        row_start = y_start + y_offset  
        row_end = y_end + y_offset
        
        cmd(0x2A)  # Column Address Set
        data(col_start >> 8); data(col_start & 0xFF)
        data(col_end >> 8); data(col_end & 0xFF)
        
        cmd(0x2B)  # Row Address Set  
        data(row_start >> 8); data(row_start & 0xFF)
        data(row_end >> 8); data(row_end & 0xFF)
        
        cmd(0x2C)  # Memory Write
    
    def fill_area(x, y, w, h, color):
        """Fill rectangular area with color using correct coordinates"""
        set_window_correct(x, y, x + w - 1, y + h - 1)
        
        cs.value(0); dc.value(1)
        color_bytes = bytearray([color >> 8, color & 0xFF])
        for _ in range(w * h):
            spi.write(color_bytes)
        cs.value(1)
    
    def test_rotation_pattern():
        """Draw a pattern to test rotation - arrow pointing right"""
        # Clear screen to black
        fill_area(0, 0, 135, 240, 0x0000)
        
        # Draw arrow pattern pointing RIGHT (correct orientation)
        # Arrow shaft (horizontal line in middle)
        fill_area(20, 110, 80, 20, 0xF800)  # Red horizontal bar
        
        # Arrow head (triangle pointing right)
        for i in range(20):
            fill_area(100 + i, 120 - i, 2, 2 * i, 0x07E0)  # Green triangle
        
        # Text indicators (if this appears correctly, rotation is right)
        # Top indicator
        fill_area(0, 0, 135, 10, 0x001F)   # Blue bar at top
        # Left indicator  
        fill_area(0, 0, 10, 240, 0xFFE0)   # Yellow bar at left
    
    # Initialize display with basic settings
    print("Initializing ST7789...")
    reset.value(0); time.sleep_ms(50)
    reset.value(1); time.sleep_ms(200)
    
    cmd(0x01); time.sleep_ms(150)  # Software reset
    cmd(0x11); time.sleep_ms(120)  # Sleep out
    cmd(0x3A); data(0x05)          # RGB565 pixel format
    cmd(0x21)                      # Display inversion on
    cmd(0x13)                      # Normal display mode
    
    # Test different rotation values
    rotations = [
        (0x00, "0x00 - Portrait"),
        (0x60, "0x60 - Landscape 1"), 
        (0xC0, "0xC0 - Portrait flipped"),
        (0xA0, "0xA0 - Landscape 2"),
        (0x70, "0x70 - Current setting"),
        (0x80, "0x80 - Alternative 1"),
        (0x40, "0x40 - Alternative 2"),
        (0x20, "0x20 - Alternative 3")
    ]
    
    for rotation_val, description in rotations:
        print(f"Testing {description}")
        
        # Set rotation
        cmd(0x36); data(rotation_val)  # Memory access control
        cmd(0x29); time.sleep_ms(50)   # Display on
        
        # Draw test pattern
        test_rotation_pattern()
        
        print(f"Current rotation: {description}")
        print("Arrow should point RIGHT, blue bar at TOP, yellow at LEFT")
        print("Press reset when you see correct orientation...")
        time.sleep(8)  # 8 seconds to observe each rotation

rotation_test()