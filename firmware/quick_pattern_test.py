# Quick pattern test for M5StickC PLUS display orientation
import time
from machine import Pin, SPI

print("Quick Pattern Test")

def quick_pattern():
    # Initialize hardware
    spi = SPI(1, baudrate=10000000, sck=Pin(13), mosi=Pin(15))
    reset = Pin(18, Pin.OUT)
    cs = Pin(5, Pin.OUT)
    dc = Pin(23, Pin.OUT)
    backlight = Pin(12, Pin.OUT)
    
    backlight.value(1)
    
    # Reset
    reset.value(0)
    time.sleep_ms(10)
    reset.value(1)
    time.sleep_ms(120)
    
    def cmd(c):
        cs.value(0)
        dc.value(0)
        spi.write(bytearray([c]))
        cs.value(1)
        
    def data(d):
        cs.value(0)
        dc.value(1)
        spi.write(bytearray([d]))
        cs.value(1)
    
    def fill_rect(x, y, w, h, color):
        # Set window
        cmd(0x2A)
        data(x >> 8); data(x & 0xFF)
        data((x + w - 1) >> 8); data((x + w - 1) & 0xFF)
        
        cmd(0x2B)
        data(y >> 8); data(y & 0xFF)
        data((y + h - 1) >> 8); data((y + h - 1) & 0xFF)
        
        cmd(0x2C)
        
        # Fill
        color_bytes = bytearray([color >> 8, color & 0xFF])
        cs.value(0)
        dc.value(1)
        for _ in range(w * h):
            spi.write(color_bytes)
        cs.value(1)
    
    # Initialize display
    cmd(0x11); time.sleep_ms(120)
    cmd(0x3A); data(0x05)
    cmd(0x36); data(0xA0)  # Current rotation
    cmd(0x21); cmd(0x13); cmd(0x29)
    
    # Colors
    GREEN = 0x07E0
    WHITE = 0xFFFF
    RED = 0xF800
    BLUE = 0x001F
    
    print("Pattern 1: Assuming 135x240 portrait")
    # Clear to black
    fill_rect(0, 0, 135, 240, 0x0000)
    # Top-left green square
    fill_rect(0, 0, 67, 60, GREEN)
    # Top-right white square  
    fill_rect(68, 0, 67, 60, WHITE)
    # Bottom-left white square
    fill_rect(0, 120, 67, 120, WHITE)
    # Bottom-right green square
    fill_rect(68, 120, 67, 120, GREEN)
    
    time.sleep(3)
    
    print("Pattern 2: Trying 240x135 landscape")
    cmd(0x36); data(0xC0)  # Landscape rotation
    
    # Clear to black
    fill_rect(0, 0, 240, 135, 0x0000)
    # Left-top red square
    fill_rect(0, 0, 120, 67, RED)
    # Right-top blue square
    fill_rect(120, 0, 120, 67, BLUE)
    # Left-bottom blue square
    fill_rect(0, 68, 120, 67, BLUE)
    # Right-bottom red square
    fill_rect(120, 68, 120, 67, RED)
    
    print("Done! Check the patterns")

quick_pattern()