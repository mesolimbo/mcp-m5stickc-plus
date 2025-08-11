# Fine-tune coordinates to eliminate the black bar
import time
from machine import Pin, SPI, I2C

print("Fine-tuning M5StickC PLUS coordinates")

def fine_tune_test():
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
    
    def set_window_and_fill(x_start, y_start, x_end, y_end, color, label):
        print(f"{label}: ({x_start},{y_start}) to ({x_end},{y_end})")
        
        cmd(0x2A)  # Column Address Set
        data(x_start >> 8); data(x_start & 0xFF)
        data(x_end >> 8); data(x_end & 0xFF)
        
        cmd(0x2B)  # Page Address Set  
        data(y_start >> 8); data(y_start & 0xFF)
        data(y_end >> 8); data(y_end & 0xFF)
        
        cmd(0x2C)  # Memory Write
        
        # Fill with color
        cs.value(0); dc.value(1)
        color_bytes = bytearray([color >> 8, color & 0xFF])
        pixels = (x_end - x_start + 1) * (y_end - y_start + 1)
        
        for _ in range(pixels):
            spi.write(color_bytes)
        cs.value(1)
    
    # Initialize display
    reset.value(0); time.sleep_ms(50)
    reset.value(1); time.sleep_ms(200)
    
    cmd(0x01); time.sleep_ms(150)
    cmd(0x11); time.sleep_ms(120)
    cmd(0x36); data(0x70)  # M5StickC rotation
    cmd(0x3A); data(0x05)  # RGB565
    cmd(0x21); cmd(0x13); cmd(0x29)
    time.sleep_ms(50)
    
    print("Testing coordinates to eliminate black bar...")
    
    # Test different x-start values to eliminate the left black bar
    # If 10% is black, we need to shift left by ~24 pixels (10% of 240)
    
    # Test 1: Shift more to the left
    set_window_and_fill(0, 0, 239, 319, 0xF800, "Test 1: Full range red")  # Red
    time.sleep(3)
    
    # Test 2: Try even wider to see if we can cover more
    set_window_and_fill(0, 0, 259, 319, 0x07E0, "Test 2: Extra wide green")  # Green  
    time.sleep(3)
    
    # Test 3: Try different y-coordinates too
    set_window_and_fill(0, 0, 239, 339, 0x001F, "Test 3: Taller blue")  # Blue
    time.sleep(3)
    
    # Test 4: M5StickC specific - try landscape orientation numbers
    # M5StickC PLUS is 135x240, but in landscape might be 240x135
    set_window_and_fill(0, 0, 134, 239, 0xFFE0, "Test 4: Portrait yellow")  # Yellow
    time.sleep(3)
    
    # Test 5: Try with slight negative offset (if controller supports it)
    set_window_and_fill(0, 0, 269, 319, 0xF81F, "Test 5: Even wider magenta")  # Magenta
    
    print("Fine-tuning tests complete!")

fine_tune_test()