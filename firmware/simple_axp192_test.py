# Simple test with AXP192 and lower SPI speed
import time
from machine import Pin, SPI, I2C

print("Simple AXP192 + Display Test")

# Step 1: Enable display via AXP192
print("Configuring AXP192...")
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
axp192_addr = 0x34

# Enable display power
i2c.writeto_mem(axp192_addr, 0x12, bytes([0xFF]))  # Enable LDOs
i2c.writeto_mem(axp192_addr, 0x96, bytes([0x84]))  # GPIO2 as output  
i2c.writeto_mem(axp192_addr, 0x95, bytes([0x02]))  # GPIO2 high (backlight)

print("AXP192 configured, display should be powered")
time.sleep_ms(100)

# Step 2: Simple SPI test with lower speed
print("Testing SPI...")
spi = SPI(1, baudrate=10000000, sck=Pin(13), mosi=Pin(15))  # Lower speed
reset = Pin(18, Pin.OUT, value=1)
cs = Pin(5, Pin.OUT, value=1)
dc = Pin(23, Pin.OUT)

# Reset display
reset.value(0)
time.sleep_ms(20)
reset.value(1) 
time.sleep_ms(150)

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

print("Basic display init...")
cmd(0x11)  # Sleep out
time.sleep_ms(120)
cmd(0x29)  # Display on

print("Filling with red...")
# Simple window and fill
cmd(0x2A); data(0x00); data(0x00); data(0x00); data(0x87)  # Column
cmd(0x2B); data(0x00); data(0x00); data(0x00); data(0xEF)  # Row
cmd(0x2C)  # Memory write

# Fill with red
cs.value(0)
dc.value(1)
for i in range(136 * 240):
    spi.write(bytearray([0xF8, 0x00]))  # Red pixel
cs.value(1)

print("Test complete!")