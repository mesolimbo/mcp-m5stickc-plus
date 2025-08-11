# Simple coordinate system debug test
import time
from machine import Pin, SPI, I2C

print("Debug: Coordinate system test")

def debug_coordinates():
    # AXP192 setup (required for display power)
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    i2c.writeto_mem(0x34, 0x12, bytes([0xFF]))  # Enable LDOs
    i2c.writeto_mem(0x34, 0x96, bytes([0x84]))  # GPIO2 output
    i2c.writeto_mem(0x34, 0x95, bytes([0x02]))  # Backlight on
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
    
    # Initialize display
    print("Initializing ST7789...")
    reset.value(0); time.sleep_ms(50)
    reset.value(1); time.sleep_ms(200)
    
    cmd(0x01); time.sleep_ms(150)  # Software reset
    cmd(0x11); time.sleep_ms(120)  # Sleep out
    cmd(0x36); data(0x00)          # Rotation 0x00 (the one that worked)
    cmd(0x3A); data(0x05)          # RGB565 pixel format
    cmd(0x21)                      # Display inversion on
    cmd(0x13)                      # Normal display mode
    cmd(0x29); time.sleep_ms(50)   # Display on
    
    print("Display initialized")
    
    # Test 1: Simple full screen fill (like our working test)
    print("Test 1: Full screen red")
    cmd(0x2A)  # Column Address Set
    data(0x00); data(52)   # Start: 52 (x_offset)
    data(0x00); data(186)  # End: 186 (52+134)
    
    cmd(0x2B)  # Row Address Set  
    data(0x00); data(40)   # Start: 40 (y_offset)
    data(0x01); data(23)   # End: 279 (40+239)
    
    cmd(0x2C)  # Memory Write
    
    cs.value(0); dc.value(1)
    red = bytearray([0xF8, 0x00])  # Red color
    for _ in range(135 * 240):
        spi.write(red)
    cs.value(1)
    
    print("Red screen should be showing")
    time.sleep(5)
    
    # Test 2: Simple rectangle
    print("Test 2: Green rectangle in center")
    cmd(0x2A)  # Column Address Set
    data(0x00); data(92)   # Start: 52+40 = 92
    data(0x00); data(146)  # End: 92+54 = 146
    
    cmd(0x2B)  # Row Address Set  
    data(0x00); data(160)  # Start: 40+120 = 160
    data(0x00); data(199)  # End: 160+39 = 199
    
    cmd(0x2C)  # Memory Write
    
    cs.value(0); dc.value(1)
    green = bytearray([0x07, 0xE0])  # Green color
    for _ in range(55 * 40):  # 55x40 rectangle
        spi.write(green)
    cs.value(1)
    
    print("Green rectangle should be showing")
    time.sleep(5)
    
    # Test 3: Clear to black
    print("Test 3: Clear to black")
    cmd(0x2A)  # Column Address Set
    data(0x00); data(52)   # Start: 52
    data(0x00); data(186)  # End: 186
    
    cmd(0x2B)  # Row Address Set  
    data(0x00); data(40)   # Start: 40
    data(0x01); data(23)   # End: 279
    
    cmd(0x2C)  # Memory Write
    
    cs.value(0); dc.value(1)
    black = bytearray([0x00, 0x00])  # Black color
    for _ in range(135 * 240):
        spi.write(black)
    cs.value(1)
    
    print("Black screen should be showing")
    time.sleep(3)
    
    # Test 4: Border test (like our working coordinate test)
    print("Test 4: Border test")
    
    # Top border (red)
    cmd(0x2A); data(0x00); data(52); data(0x00); data(186)
    cmd(0x2B); data(0x00); data(40); data(0x00); data(44)
    cmd(0x2C)
    cs.value(0); dc.value(1)
    for _ in range(135 * 5):
        spi.write(red)
    cs.value(1)
    
    # Bottom border (red)
    cmd(0x2A); data(0x00); data(52); data(0x00); data(186)
    cmd(0x2B); data(0x01); data(19); data(0x01); data(23)
    cmd(0x2C)
    cs.value(0); dc.value(1)
    for _ in range(135 * 5):
        spi.write(red)
    cs.value(1)
    
    # Left border (green)
    cmd(0x2A); data(0x00); data(52); data(0x00); data(56)
    cmd(0x2B); data(0x00); data(40); data(0x01); data(23)
    cmd(0x2C)
    cs.value(0); dc.value(1)
    for _ in range(5 * 240):
        spi.write(green)
    cs.value(1)
    
    # Right border (green)
    cmd(0x2A); data(0x00); data(182); data(0x00); data(186)
    cmd(0x2B); data(0x00); data(40); data(0x01); data(23)
    cmd(0x2C)
    cs.value(0); dc.value(1)
    for _ in range(5 * 240):
        spi.write(green)
    cs.value(1)
    
    print("Border test complete!")
    print("Should see: Red top/bottom borders, Green left/right borders")

debug_coordinates()