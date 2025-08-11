# M5StickC PLUS - Simple Color-Coded Rotation Test
import time
from machine import Pin, SPI, I2C

print("M5StickC PLUS - Color-Coded Rotation Test")

def simple_rotation_test():
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
        x_offset = 52
        y_offset = 40
        
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
    
    def fill_screen(color):
        """Fill entire screen with one color"""
        set_window_correct(0, 0, 134, 239)
        
        cs.value(0); dc.value(1)
        color_bytes = bytearray([color >> 8, color & 0xFF])
        for _ in range(135 * 240):
            spi.write(color_bytes)
        cs.value(1)
    
    def draw_orientation_indicator(color):
        """Draw fat exclamation mark for landscape reading orientation"""
        # Fill screen with color first
        fill_screen(color)
        
        # Draw white exclamation mark in center, oriented for landscape reading
        # Main body (horizontal rectangle for landscape)
        set_window_correct(30, 110, 90, 125)  # Fat horizontal bar (60 pixels wide, 15 pixels tall)
        cs.value(0); dc.value(1)
        white = bytearray([0xFF, 0xFF])
        
        # Fill the main exclamation body (horizontal)
        for _ in range(61 * 16):  # 61 pixels wide, 16 pixels tall
            spi.write(white)
        cs.value(1)
        
        # Draw the dot at right side (for landscape reading)
        set_window_correct(100, 110, 115, 125)  # Fat dot to the right
        cs.value(0); dc.value(1)
        for _ in range(16 * 16):  # 16x16 pixel dot
            spi.write(white)
        cs.value(1)
    
    # Initialize display with basic settings
    print("Initializing ST7789...")
    reset.value(0); time.sleep_ms(50)
    reset.value(1); time.sleep_ms(200)
    
    cmd(0x01); time.sleep_ms(150)  # Software reset
    cmd(0x11); time.sleep_ms(120)  # Sleep out
    cmd(0x3A); data(0x05)          # RGB565 pixel format
    cmd(0x21)                      # Display inversion on
    cmd(0x13)                      # Normal display mode
    
    # Test different rotations with unique colors
    rotations = [
        (0x00, "RED", 0xF800),      # Bright Red
        (0x60, "GREEN", 0x07E0),    # Bright Green  
        (0xC0, "BLUE", 0x001F),     # Bright Blue
        (0xA0, "YELLOW", 0xFFE0),   # Yellow
        (0x70, "MAGENTA", 0xF81F),  # Magenta (current setting)
        (0x80, "CYAN", 0x07FF),     # Cyan
        (0x40, "ORANGE", 0xFD20),   # Orange
        (0x20, "PURPLE", 0x8010)    # Purple
    ]
    
    print("\nLook for WHITE EXCLAMATION MARK (!) READABLE IN LANDSCAPE on colored background")
    print("Tell me which COLOR shows the exclamation mark readable when device is sideways!\n")
    
    for rotation_val, color_name, color_code in rotations:
        print(f"Showing {color_name} (0x{rotation_val:02X})")
        
        # Set rotation
        cmd(0x36); data(rotation_val)  # Memory access control
        cmd(0x29); time.sleep_ms(50)   # Display on
        
        # Draw colored screen with white exclamation mark
        draw_orientation_indicator(color_code)
        
        print(f"Current: {color_name} background with white exclamation mark")
        print("Exclamation mark should be READABLE IN LANDSCAPE (!) for correct orientation")
        time.sleep(5)  # 5 seconds per color

simple_rotation_test()