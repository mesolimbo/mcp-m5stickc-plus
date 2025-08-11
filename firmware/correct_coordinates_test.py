# M5StickC PLUS - Correct coordinate mapping based on ST7789 driver research
import time
from machine import Pin, SPI, I2C

print("M5StickC PLUS - Correct Coordinate Mapping Test")

def correct_coordinates_test():
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
        
        print(f"Window: ({x_start},{y_start})-({x_end},{y_end}) -> ({col_start},{row_start})-({col_end},{row_end})")
        
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
    
    # Initialize display
    print("Initializing ST7789...")
    reset.value(0); time.sleep_ms(50)
    reset.value(1); time.sleep_ms(200)
    
    cmd(0x01); time.sleep_ms(150)  # Software reset
    cmd(0x11); time.sleep_ms(120)  # Sleep out
    cmd(0x36); data(0x00)          # Memory access control (Correct landscape rotation)
    cmd(0x3A); data(0x05)          # RGB565 pixel format
    cmd(0x21)                      # Display inversion on
    cmd(0x13)                      # Normal display mode
    cmd(0x29); time.sleep_ms(50)   # Display on
    
    print("Display initialized")
    
    # Test correct coordinate mapping
    print("Testing correct M5StickC PLUS coordinate mapping...")
    
    # Test 1: Full screen red (should cover entire visible area)
    print("Test 1: Full screen red")
    fill_area(0, 0, 135, 240, 0xF800)  # Red - full 135x240 area
    time.sleep(3)
    
    # Test 2: Half screen green (should be exactly half)
    print("Test 2: Left half green")
    fill_area(0, 0, 67, 240, 0x07E0)  # Green - left half
    time.sleep(3)
    
    # Test 3: Right half blue
    print("Test 3: Right half blue") 
    fill_area(68, 0, 67, 240, 0x001F)  # Blue - right half
    time.sleep(3)
    
    # Test 4: Quadrants test
    print("Test 4: Four quadrants")
    fill_area(0, 0, 67, 120, 0xF800)    # Top-left: Red
    fill_area(68, 0, 67, 120, 0x07E0)   # Top-right: Green
    fill_area(0, 120, 67, 120, 0x001F)  # Bottom-left: Blue
    fill_area(68, 120, 67, 120, 0xFFE0) # Bottom-right: Yellow
    time.sleep(5)
    
    # Test 5: Border test (should show exact screen edges)
    print("Test 5: Border test")
    fill_area(0, 0, 135, 240, 0x0000)     # Black background
    fill_area(0, 0, 135, 5, 0xF800)       # Top border: Red
    fill_area(0, 235, 135, 5, 0xF800)     # Bottom border: Red
    fill_area(0, 0, 5, 240, 0x07E0)       # Left border: Green
    fill_area(130, 0, 5, 240, 0x07E0)     # Right border: Green
    
    print("Coordinate mapping tests complete!")
    print("If borders touch screen edges exactly, coordinates are correct!")

correct_coordinates_test()