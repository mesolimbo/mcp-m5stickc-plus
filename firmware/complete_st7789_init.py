# Complete ST7789 initialization for M5StickC PLUS
import time
from machine import Pin, SPI

print("Complete ST7789 Initialization Test")

def complete_st7789_test():
    print("Initializing with full ST7789 sequence...")
    
    # Hardware setup
    backlight = Pin(12, Pin.OUT, value=1)  # Backlight on
    spi = SPI(1, baudrate=10000000, sck=Pin(13), mosi=Pin(15))
    reset = Pin(18, Pin.OUT, value=1)
    cs = Pin(5, Pin.OUT, value=1)
    dc = Pin(23, Pin.OUT, value=0)
    
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
    
    # Hardware reset
    print("Hardware reset...")
    reset.value(0)
    time.sleep_ms(10)
    reset.value(1)
    time.sleep_ms(120)
    
    # Complete ST7789 initialization sequence
    print("ST7789 initialization sequence...")
    
    cmd(0x01)  # Software reset
    time.sleep_ms(150)
    
    cmd(0x11)  # Sleep out
    time.sleep_ms(120)
    
    cmd(0x36)  # Memory data access control
    data(0x00)  # Normal orientation
    
    cmd(0x3A)  # Interface pixel format
    data(0x05)  # 16-bit RGB565
    
    cmd(0xB2)  # Porch control
    data([0x0C, 0x0C, 0x00, 0x33, 0x33])
    
    cmd(0xB7)  # Gate control
    data(0x35)
    
    cmd(0xBB)  # VCOM setting
    data(0x19)
    
    cmd(0xC0)  # LCM control
    data(0x2C)
    
    cmd(0xC2)  # VDV and VRH command enable
    data(0x01)
    
    cmd(0xC3)  # VRH set
    data(0x12)
    
    cmd(0xC4)  # VDV set
    data(0x20)
    
    cmd(0xC6)  # Frame rate control
    data(0x0F)
    
    cmd(0xD0)  # Power control 1
    data([0xA4, 0xA1])
    
    cmd(0xE0)  # Positive voltage gamma control
    data([0xD0, 0x04, 0x0D, 0x11, 0x13, 0x2B, 0x3F, 0x54, 
          0x4C, 0x18, 0x0D, 0x0B, 0x1F, 0x23])
    
    cmd(0xE1)  # Negative voltage gamma control  
    data([0xD0, 0x04, 0x0C, 0x11, 0x13, 0x2C, 0x3F, 0x44,
          0x51, 0x2F, 0x1F, 0x1F, 0x20, 0x23])
    
    cmd(0x21)  # Display inversion on
    
    cmd(0x13)  # Normal display mode on
    
    cmd(0x29)  # Display on
    time.sleep_ms(100)
    
    print("Display should now be initialized!")
    
    # Test with a simple pattern
    print("Drawing test pattern...")
    
    # Set display window
    cmd(0x2A)  # Column address set
    data([0x00, 0x00, 0x00, 0x87])  # 0 to 135
    
    cmd(0x2B)  # Row address set
    data([0x00, 0x00, 0x00, 0xEF])  # 0 to 239
    
    cmd(0x2C)  # Memory write
    
    # Draw alternating stripes (white/red)
    cs.value(0)
    dc.value(1)
    
    white = bytearray([0xFF, 0xFF])
    red = bytearray([0xF8, 0x00])
    
    for y in range(240):
        for x in range(136):
            if (y // 20) % 2 == 0:  # 20-pixel high stripes
                spi.write(white)
            else:
                spi.write(red)
    
    cs.value(1)
    
    print("Pattern complete! You should see white and red stripes.")
    
    # Wait then try solid colors
    time.sleep(3)
    
    print("Testing solid green...")
    cmd(0x2C)  # Memory write
    
    cs.value(0)
    dc.value(1)
    green = bytearray([0x07, 0xE0])
    
    for i in range(136 * 240):
        spi.write(green)
    
    cs.value(1)
    
    print("All tests complete!")

complete_st7789_test()