# Fixed M5StickC PLUS display test with correct orientation
import time
from machine import Pin, SPI, I2C

print("M5StickC PLUS - Fixed Display Test")

def fixed_display_test():
    # Step 1: Configure AXP192 first
    print("Configuring AXP192...")
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    axp192_addr = 0x34
    
    # Enable display power and backlight
    i2c.writeto_mem(axp192_addr, 0x12, bytes([0xFF]))  # Enable LDOs
    i2c.writeto_mem(axp192_addr, 0x96, bytes([0x84]))  # GPIO2 output
    i2c.writeto_mem(axp192_addr, 0x95, bytes([0x02]))  # GPIO2 high
    time.sleep_ms(100)
    
    # Step 2: Initialize SPI
    print("Initializing SPI...")
    spi = SPI(1, baudrate=20000000, sck=Pin(13), mosi=Pin(15))
    reset = Pin(18, Pin.OUT, value=1)
    cs = Pin(5, Pin.OUT, value=1)
    dc = Pin(23, Pin.OUT)
    
    def cmd(c):
        cs.value(0)
        dc.value(0)
        spi.write(bytearray([c]))
        cs.value(1)
    
    def data(d):
        cs.value(0)
        dc.value(1)
        if isinstance(d, list):
            spi.write(bytearray(d))
        else:
            spi.write(bytearray([d]))
        cs.value(1)
    
    def fill_rect(x, y, w, h, color):
        # Set window
        cmd(0x2A)  # Column set
        data([x >> 8, x & 0xFF, (x + w - 1) >> 8, (x + w - 1) & 0xFF])
        
        cmd(0x2B)  # Row set
        data([y >> 8, y & 0xFF, (y + h - 1) >> 8, (y + h - 1) & 0xFF])
        
        cmd(0x2C)  # Memory write
        
        # Send pixels
        color_bytes = bytearray([color >> 8, color & 0xFF])
        cs.value(0)
        dc.value(1)
        for _ in range(w * h):
            spi.write(color_bytes)
        cs.value(1)
    
    # Step 3: Reset and initialize display
    print("Resetting display...")
    reset.value(0)
    time.sleep_ms(20)
    reset.value(1)
    time.sleep_ms(150)
    
    print("ST7789V2 initialization...")
    cmd(0x01)  # Software reset
    time.sleep_ms(150)
    
    cmd(0x11)  # Sleep out
    time.sleep_ms(120)
    
    # Try different orientations
    cmd(0x36)  # Memory data access control
    data(0x00)  # Normal orientation first
    
    cmd(0x3A)  # Pixel format
    data(0x05)  # 16-bit RGB565
    
    cmd(0x21)  # Display inversion on
    cmd(0x13)  # Normal display mode
    cmd(0x29)  # Display on
    time.sleep_ms(50)
    
    # Colors
    BLACK = 0x0000
    WHITE = 0xFFFF
    RED = 0xF800
    GREEN = 0x07E0
    BLUE = 0x001F
    
    print("Test 1: Clear to black...")
    fill_rect(0, 0, 240, 320, BLACK)  # Try full range first
    time.sleep(1)
    
    print("Test 2: Simple color blocks...")
    # Quarter screen blocks
    fill_rect(0, 0, 120, 160, RED)      # Top-left red
    fill_rect(120, 0, 120, 160, GREEN)  # Top-right green
    fill_rect(0, 160, 120, 160, BLUE)   # Bottom-left blue  
    fill_rect(120, 160, 120, 160, WHITE) # Bottom-right white
    
    time.sleep(3)
    
    print("Test 3: Try different rotation...")
    cmd(0x36); data(0x60)  # Rotate 90 degrees
    
    # Clear and test
    fill_rect(0, 0, 320, 240, BLACK)
    fill_rect(50, 50, 100, 100, RED)    # Red square in middle
    
    time.sleep(2)
    
    print("Test 4: M5StickC PLUS specific rotation...")
    cmd(0x36); data(0x70)  # M5StickC Plus rotation
    
    # Clear to black
    fill_rect(0, 0, 135, 240, BLACK)
    
    # Simple test pattern
    fill_rect(10, 10, 30, 30, RED)      # Red square top-left
    fill_rect(95, 10, 30, 30, GREEN)    # Green square top-right  
    fill_rect(10, 200, 30, 30, BLUE)    # Blue square bottom-left
    fill_rect(95, 200, 30, 30, WHITE)   # White square bottom-right
    
    # Center stripe
    fill_rect(0, 110, 135, 20, GREEN)   # Green horizontal stripe
    
    print("Display test complete!")

fixed_display_test()