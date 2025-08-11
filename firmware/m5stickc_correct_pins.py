# M5StickC PLUS with correct pins and AXP192 power management
import time
from machine import Pin, SPI, I2C

print("M5StickC PLUS - Correct Pin Configuration Test")

def test_with_axp192():
    print("Step 1: Initialize I2C for AXP192 power management...")
    try:
        # AXP192 power management chip
        i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
        devices = i2c.scan()
        print(f"I2C devices found: {[hex(d) for d in devices]}")
        
        # AXP192 is usually at address 0x34
        axp192_addr = 0x34
        if axp192_addr in devices:
            print("AXP192 found! Enabling display power...")
            
            # Enable LDO2 (display power) - typical AXP192 command
            i2c.writeto_mem(axp192_addr, 0x12, bytes([0xFF]))  # Enable all LDOs
            
            # Set backlight brightness via AXP192 GPIO
            i2c.writeto_mem(axp192_addr, 0x96, bytes([0x84]))  # GPIO2 as output
            i2c.writeto_mem(axp192_addr, 0x95, bytes([0x02]))  # GPIO2 high (backlight on)
            
            print("AXP192 display power enabled")
        else:
            print("AXP192 not found, trying GPIO12 for backlight...")
            backlight = Pin(12, Pin.OUT, value=1)
            
    except Exception as e:
        print(f"AXP192 setup failed: {e}")
        print("Falling back to GPIO12 backlight...")
        backlight = Pin(12, Pin.OUT, value=1)
    
    print("Step 2: Initialize SPI with correct M5StickC PLUS pins...")
    # Correct pins for M5StickC PLUS
    spi = SPI(1, baudrate=40000000, sck=Pin(13), mosi=Pin(15))
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
    
    print("Step 3: ST7789V2 initialization...")
    # Hardware reset
    reset.value(0)
    time.sleep_ms(20)
    reset.value(1)
    time.sleep_ms(150)
    
    # ST7789V2 specific initialization
    cmd(0x01)  # Software reset
    time.sleep_ms(150)
    
    cmd(0x11)  # Sleep out
    time.sleep_ms(120)
    
    cmd(0x36)  # Memory data access control
    data(0x70)  # M5StickC PLUS specific rotation
    
    cmd(0x3A)  # Interface pixel format
    data(0x05)  # 16-bit RGB565
    
    cmd(0xB2)  # Porch control
    data([0x0C, 0x0C, 0x00, 0x33, 0x33])
    
    cmd(0xB7)  # Gate control
    data(0x35)
    
    cmd(0xBB)  # VCOM setting
    data(0x32)  # Different value for V2
    
    cmd(0xC2)  # VDV and VRH command enable
    data(0x01)
    
    cmd(0xC3)  # VRH set
    data(0x15)  # Different value for V2
    
    cmd(0xC4)  # VDV set
    data(0x20)
    
    cmd(0xC6)  # Frame rate control
    data(0x0F)
    
    cmd(0xD0)  # Power control 1
    data([0xA4, 0xA1])
    
    # Gamma correction for ST7789V2
    cmd(0xE0)
    data([0xD0, 0x05, 0x0A, 0x09, 0x08, 0x05, 0x2E, 0x44,
          0x45, 0x0F, 0x17, 0x16, 0x2B, 0x33])
    
    cmd(0xE1)
    data([0xD0, 0x05, 0x0A, 0x09, 0x08, 0x05, 0x2E, 0x43,
          0x45, 0x0F, 0x16, 0x16, 0x2B, 0x33])
    
    cmd(0x21)  # Display inversion on
    cmd(0x13)  # Normal display mode
    cmd(0x29)  # Display on
    time.sleep_ms(50)
    
    print("Step 4: Test pattern with correct dimensions...")
    # M5StickC PLUS is 135x240, but test both orientations
    
    # Set window for 135x240
    cmd(0x2A)  # Column address set
    data([0x00, 0x34, 0x00, 0x89])  # Offset for M5StickC: 52 to 187 (135 pixels)
    
    cmd(0x2B)  # Row address set
    data([0x00, 0x28, 0x01, 0x17])  # Offset: 40 to 279 (240 pixels)
    
    cmd(0x2C)  # Memory write
    
    # Fill with bright magenta (highly visible)
    cs.value(0)
    dc.value(1)
    magenta = bytearray([0xF8, 0x1F])  # Bright magenta
    
    for i in range(135 * 240):
        spi.write(magenta)
    
    cs.value(1)
    
    print("M5StickC PLUS display test complete!")
    print("You should see a bright magenta/purple screen")

test_with_axp192()