# Basic display debug for M5StickC PLUS
import time
from machine import Pin, SPI

print("Basic Display Debug")

def debug_display():
    print("Step 1: Testing backlight control...")
    backlight = Pin(12, Pin.OUT)
    
    # Flash backlight to confirm it's working
    for i in range(3):
        print(f"  Backlight OFF ({i+1}/3)")
        backlight.value(0)
        time.sleep(1)
        print(f"  Backlight ON ({i+1}/3)")
        backlight.value(1)
        time.sleep(1)
    
    print("Step 2: Initializing SPI and pins...")
    try:
        spi = SPI(1, baudrate=10000000, sck=Pin(13), mosi=Pin(15))
        reset = Pin(18, Pin.OUT)
        cs = Pin(5, Pin.OUT, value=1)  # Start high
        dc = Pin(23, Pin.OUT)
        print("  SPI initialized successfully")
    except Exception as e:
        print(f"  SPI initialization failed: {e}")
        return
    
    print("Step 3: Display reset sequence...")
    reset.value(1)
    time.sleep_ms(10)
    reset.value(0)
    time.sleep_ms(10)
    reset.value(1)
    time.sleep_ms(120)
    print("  Reset complete")
    
    def send_cmd(cmd):
        cs.value(0)
        dc.value(0)  # Command mode
        spi.write(bytearray([cmd]))
        cs.value(1)
        print(f"    CMD: 0x{cmd:02X}")
    
    def send_data(data):
        cs.value(0)
        dc.value(1)  # Data mode
        spi.write(bytearray([data]))
        cs.value(1)
        print(f"    DATA: 0x{data:02X}")
    
    print("Step 4: Basic display commands...")
    try:
        send_cmd(0x01)  # Software reset
        time.sleep_ms(150)
        
        send_cmd(0x11)  # Sleep out
        time.sleep_ms(120)
        
        send_cmd(0x29)  # Display on
        time.sleep_ms(50)
        
        print("  Basic commands sent")
    except Exception as e:
        print(f"  Command sending failed: {e}")
        return
    
    print("Step 5: Try to fill with solid color...")
    try:
        # Set full window (try both orientations)
        send_cmd(0x2A)  # Column address set
        send_data(0x00); send_data(0x00)  # Start column
        send_data(0x00); send_data(0xEF)  # End column (239)
        
        send_cmd(0x2B)  # Row address set  
        send_data(0x00); send_data(0x00)  # Start row
        send_data(0x00); send_data(0x87)  # End row (135)
        
        send_cmd(0x2C)  # Memory write
        
        # Fill with bright red (should be very visible)
        red_pixel = bytearray([0xF8, 0x00])  # Bright red in RGB565
        
        print("  Filling with red pixels...")
        cs.value(0)
        dc.value(1)  # Data mode
        
        # Fill entire screen
        pixel_count = 240 * 136  # Full size
        for i in range(pixel_count):
            spi.write(red_pixel)
            if i % 10000 == 0:
                print(f"    Written {i} pixels...")
        
        cs.value(1)
        print("  Red fill complete!")
        
        time.sleep(3)
        
        # Try different color
        print("  Now filling with bright blue...")
        send_cmd(0x2C)  # Memory write again
        
        blue_pixel = bytearray([0x00, 0x1F])  # Bright blue
        
        cs.value(0)
        dc.value(1)
        
        for i in range(pixel_count):
            spi.write(blue_pixel)
            if i % 10000 == 0:
                print(f"    Written {i} blue pixels...")
        
        cs.value(1)
        print("  Blue fill complete!")
        
    except Exception as e:
        print(f"  Fill failed: {e}")
        import sys
        sys.print_exception(e)
    
    print("Debug complete!")

debug_display()