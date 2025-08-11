# Minimal display test - just get something visible
import time
from machine import Pin, SPI, I2C

print("Minimal Display Test")

# Setup AXP192 first
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
i2c.writeto_mem(0x34, 0x12, bytes([0xFF]))  # Power
i2c.writeto_mem(0x34, 0x96, bytes([0x84]))  # GPIO
i2c.writeto_mem(0x34, 0x95, bytes([0x02]))  # Backlight
time.sleep_ms(100)

# Simple SPI setup
spi = SPI(1, baudrate=10000000, sck=Pin(13), mosi=Pin(15))
reset = Pin(18, Pin.OUT)
cs = Pin(5, Pin.OUT, value=1)
dc = Pin(23, Pin.OUT)

# Reset
reset.value(0); time.sleep_ms(20)
reset.value(1); time.sleep_ms(150)

def cmd(c):
    cs.value(0); dc.value(0)
    spi.write(bytearray([c]))
    cs.value(1)

def data(d):
    cs.value(0); dc.value(1)
    spi.write(bytearray([d]))
    cs.value(1)

# Minimal init
print("Basic init...")
cmd(0x11); time.sleep_ms(120)  # Sleep out
cmd(0x29)  # Display on

print("Try full screen red...")
# Set very basic window
cmd(0x2A); data(0x00); data(0x00); data(0x01); data(0x3F)  # 0-319
cmd(0x2B); data(0x00); data(0x00); data(0x01); data(0xDF)  # 0-479  
cmd(0x2C)

# Send red pixels
cs.value(0); dc.value(1)
red = bytearray([0xF8, 0x00])

print("Sending red pixels...")
for i in range(50000):  # Just first 50k pixels
    spi.write(red)
    if i % 10000 == 0:
        print(f"  {i} pixels...")

cs.value(1)
print("Done - should see red!")

time.sleep(3)

print("Try smaller window...")
cmd(0x2A); data(0x00); data(0x10); data(0x00); data(0x50)  # Small window
cmd(0x2B); data(0x00); data(0x10); data(0x00); data(0x50)
cmd(0x2C)

cs.value(0); dc.value(1)
white = bytearray([0xFF, 0xFF])

for i in range(64 * 64):  # 64x64 white square
    spi.write(white)

cs.value(1)
print("Small white square done!")