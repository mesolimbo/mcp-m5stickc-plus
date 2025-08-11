# Wake up and reset M5StickC PLUS display
import time
from machine import Pin, SPI

print("Waking up M5StickC PLUS display...")

def wake_and_reset_display():
    # Initialize hardware
    backlight = Pin(12, Pin.OUT)
    spi = SPI(1, baudrate=10000000, sck=Pin(13), mosi=Pin(15))
    reset = Pin(18, Pin.OUT)
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
    
    print("Step 1: Force backlight on...")
    backlight.value(1)
    time.sleep_ms(100)
    
    print("Step 2: Hardware reset...")
    reset.value(0)
    time.sleep_ms(20)
    reset.value(1)
    time.sleep_ms(150)
    
    print("Step 3: Wake up display...")
    cmd(0x11)  # Sleep out
    time.sleep_ms(120)
    
    cmd(0x13)  # Normal display mode
    time.sleep_ms(10)
    
    cmd(0x29)  # Display on
    time.sleep_ms(50)
    
    print("Step 4: Clear display to black...")
    # Set full window
    cmd(0x2A)  # Column set
    data([0x00, 0x00, 0x00, 0x87])  # 0-135
    
    cmd(0x2B)  # Row set
    data([0x00, 0x00, 0x00, 0xEF])  # 0-239
    
    cmd(0x2C)  # Memory write
    
    # Fill with black to clear any overlapping patterns
    cs.value(0)
    dc.value(1)
    black = bytearray([0x00, 0x00])
    
    for i in range(136 * 240):
        spi.write(black)
    
    cs.value(1)
    
    print("Step 5: Test with simple white square...")
    time.sleep_ms(500)
    
    # Draw a simple white square in center
    cmd(0x2A)  # Column set
    data([0x00, 0x28, 0x00, 0x5F])  # x: 40-95 (56 pixels wide)
    
    cmd(0x2B)  # Row set  
    data([0x00, 0x50, 0x00, 0xBF])  # y: 80-191 (112 pixels tall)
    
    cmd(0x2C)  # Memory write
    
    cs.value(0)
    dc.value(1)
    white = bytearray([0xFF, 0xFF])
    
    for i in range(56 * 112):  # Fill the square
        spi.write(white)
    
    cs.value(1)
    
    print("Display should now show a white square in center!")
    
    time.sleep(3)
    
    print("Step 6: Test with colored corners...")
    # Clear to black first
    cmd(0x2A); data([0x00, 0x00, 0x00, 0x87])
    cmd(0x2B); data([0x00, 0x00, 0x00, 0xEF])
    cmd(0x2C)
    
    cs.value(0)
    dc.value(1)
    for i in range(136 * 240):
        spi.write(black)
    cs.value(1)
    
    # Red corner (top-left)
    cmd(0x2A); data([0x00, 0x00, 0x00, 0x1F])  # 0-31
    cmd(0x2B); data([0x00, 0x00, 0x00, 0x1F])  # 0-31
    cmd(0x2C)
    
    cs.value(0)
    dc.value(1)
    red = bytearray([0xF8, 0x00])
    for i in range(32 * 32):
        spi.write(red)
    cs.value(1)
    
    # Green corner (top-right)
    cmd(0x2A); data([0x00, 0x68, 0x00, 0x87])  # 104-135
    cmd(0x2B); data([0x00, 0x00, 0x00, 0x1F])  # 0-31
    cmd(0x2C)
    
    cs.value(0)
    dc.value(1)
    green = bytearray([0x07, 0xE0])
    for i in range(32 * 32):
        spi.write(green)
    cs.value(1)
    
    print("Display reset complete! You should see colored corners.")

wake_and_reset_display()