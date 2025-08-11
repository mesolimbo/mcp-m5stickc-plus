# Conservative M5StickC PLUS display test - use exact M5Stack settings
import time
from machine import Pin, SPI, I2C

print("Conservative M5StickC PLUS Display Test")

def conservative_test():
    # Step 1: AXP192 setup (this works)
    print("Setting up AXP192...")
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    i2c.writeto_mem(0x34, 0x12, bytes([0xFF]))
    i2c.writeto_mem(0x34, 0x96, bytes([0x84])) 
    i2c.writeto_mem(0x34, 0x95, bytes([0x02]))
    time.sleep_ms(200)
    print("AXP192 configured")
    
    # Step 2: Very conservative SPI setup
    print("Setting up SPI...")
    spi = SPI(1, baudrate=8000000, sck=Pin(13), mosi=Pin(15))  # Slow speed
    reset = Pin(18, Pin.OUT, value=1)
    cs = Pin(5, Pin.OUT, value=1)  
    dc = Pin(23, Pin.OUT, value=0)
    
    def send_cmd(cmd):
        cs.value(0)
        dc.value(0)
        spi.write(bytearray([cmd]))
        cs.value(1)
        time.sleep_ms(1)  # Small delay
    
    def send_data(data):
        cs.value(0)
        dc.value(1)
        spi.write(bytearray([data]))
        cs.value(1)
        time.sleep_ms(1)
    
    # Step 3: M5StickC PLUS specific reset and init
    print("Display reset...")
    reset.value(0)
    time.sleep_ms(50)
    reset.value(1)
    time.sleep_ms(200)
    
    # Step 4: Exact M5Stack initialization sequence
    print("M5Stack ST7789 init sequence...")
    
    send_cmd(0x01)  # Software reset
    time.sleep_ms(150)
    
    send_cmd(0x11)  # Sleep out
    time.sleep_ms(120)
    
    # M5StickC PLUS specific settings
    send_cmd(0x36)  # Memory Data Access Control
    send_data(0x70)  # M5StickC Plus rotation: MY=0, MX=1, MV=1, ML=1
    
    send_cmd(0x3A)  # Interface Pixel Format
    send_data(0x05)  # 16-bit RGB565
    
    send_cmd(0x2A)  # Column Address Set - M5StickC Plus offset
    send_data(0x00); send_data(0x34)  # Start: 52 
    send_data(0x00); send_data(0xBA)  # End: 186 (52+135-1)
    
    send_cmd(0x2B)  # Page Address Set
    send_data(0x00); send_data(0x28)  # Start: 40
    send_data(0x01); send_data(0x17)  # End: 279 (40+240-1)
    
    send_cmd(0x21)  # Display Inversion On
    send_cmd(0x13)  # Normal Display Mode On
    send_cmd(0x29)  # Display On
    time.sleep_ms(50)
    
    print("Display initialized")
    
    # Step 5: Simple test pattern
    print("Drawing test pattern...")
    
    send_cmd(0x2C)  # Memory Write
    
    # Draw simple stripes
    cs.value(0)
    dc.value(1)
    
    # 10 red lines, then 10 green lines, repeat
    red = bytearray([0xF8, 0x00])    # Red
    green = bytearray([0x07, 0xE0])  # Green
    
    pixels_per_line = 135
    total_lines = 240
    
    for line in range(total_lines):
        if (line // 20) % 2 == 0:
            color = red
        else:
            color = green
            
        for pixel in range(pixels_per_line):
            spi.write(color)
    
    cs.value(1)
    
    print("Pattern complete! Should see red/green stripes")
    
    time.sleep(5)
    
    # Step 6: Try solid colors
    print("Testing solid blue...")
    send_cmd(0x2C)  # Memory Write
    
    cs.value(0)
    dc.value(1)
    blue = bytearray([0x00, 0x1F])
    
    for i in range(135 * 240):
        spi.write(blue)
    
    cs.value(1)
    print("Blue fill complete!")

conservative_test()