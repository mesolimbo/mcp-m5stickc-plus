# Test different coordinate ranges to find full screen
import time
from machine import Pin, SPI, I2C

print("M5StickC PLUS Coordinate Mapping Test")

def coordinate_test():
    # AXP192 setup
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    i2c.writeto_mem(0x34, 0x12, bytes([0xFF]))
    i2c.writeto_mem(0x34, 0x96, bytes([0x84]))
    i2c.writeto_mem(0x34, 0x95, bytes([0x02]))
    time.sleep_ms(200)
    
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
    
    def set_window(x_start, y_start, x_end, y_end):
        cmd(0x2A)  # Column Address Set
        data(x_start >> 8); data(x_start & 0xFF)
        data(x_end >> 8); data(x_end & 0xFF)
        
        cmd(0x2B)  # Page Address Set
        data(y_start >> 8); data(y_start & 0xFF)
        data(y_end >> 8); data(y_end & 0xFF)
        
        cmd(0x2C)  # Memory Write
    
    def fill_color(pixels, color):
        cs.value(0); dc.value(1)
        color_bytes = bytearray([color >> 8, color & 0xFF])
        for _ in range(pixels):
            spi.write(color_bytes)
        cs.value(1)
    
    # Initialize display
    reset.value(0); time.sleep_ms(50)
    reset.value(1); time.sleep_ms(200)
    
    cmd(0x01); time.sleep_ms(150)  # Software reset
    cmd(0x11); time.sleep_ms(120)  # Sleep out
    cmd(0x36); data(0x70)          # M5StickC rotation
    cmd(0x3A); data(0x05)          # RGB565
    cmd(0x21); cmd(0x13); cmd(0x29) # Inversion, normal, display on
    time.sleep_ms(50)
    
    print("Testing different coordinate ranges...")
    
    # Test 1: Current coordinates (52,40 to 186,279) - should show on right half
    print("Test 1: Current coordinates (right half)")
    set_window(52, 40, 186, 279)
    fill_color(135 * 240, 0xF800)  # Red
    time.sleep(3)
    
    # Test 2: Try starting from 0,0 
    print("Test 2: From origin (0,0 to 134,239)")
    set_window(0, 0, 134, 239)
    fill_color(135 * 240, 0x07E0)  # Green
    time.sleep(3)
    
    # Test 3: Try wider range
    print("Test 3: Wider range (0,0 to 239,319)")
    set_window(0, 0, 239, 319)
    fill_color(240 * 320, 0x001F)  # Blue
    time.sleep(3)
    
    # Test 4: Try shifted left coordinates
    print("Test 4: Shifted left (26,40 to 160,279)")
    set_window(26, 40, 160, 279)  # Shift left by 26 pixels
    fill_color(135 * 240, 0xFFE0)  # Yellow
    time.sleep(3)
    
    # Test 5: Try full physical range
    print("Test 5: Full physical (0,0 to 239,319)")
    set_window(0, 0, 239, 319)
    # Fill with checkerboard pattern
    cs.value(0); dc.value(1)
    for y in range(320):
        for x in range(240):
            if (x // 20 + y // 20) % 2:
                spi.write(bytearray([0xF8, 0x1F]))  # Magenta
            else:
                spi.write(bytearray([0xFF, 0xFF]))  # White
    cs.value(1)
    
    print("Coordinate tests complete!")
    print("Which test showed full screen coverage?")

coordinate_test()