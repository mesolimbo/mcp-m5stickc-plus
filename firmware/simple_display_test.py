# Simple display test to verify M5StickC PLUS LCD can light up
import time
from machine import Pin, SPI

print("Simple M5StickC PLUS Display Test")
print("==================================")

def test_backlight():
    """Test just the backlight"""
    print("Testing backlight...")
    try:
        backlight = Pin(12, Pin.OUT)
        
        print("Turning backlight ON")
        backlight.value(1)
        time.sleep(3)
        
        print("Turning backlight OFF")
        backlight.value(0)
        time.sleep(2)
        
        print("Turning backlight ON again")
        backlight.value(1)
        
        print("Backlight test complete!")
        return True
        
    except Exception as e:
        print(f"Backlight test failed: {e}")
        return False

def test_basic_spi():
    """Test basic SPI communication without complex commands"""
    print("Testing basic SPI...")
    try:
        # Initialize SPI with M5StickC PLUS pins
        spi = SPI(1, baudrate=10000000, sck=Pin(13), mosi=Pin(15))
        
        # Initialize control pins
        reset = Pin(18, Pin.OUT)
        cs = Pin(5, Pin.OUT)
        dc = Pin(23, Pin.OUT)
        
        # Reset sequence
        print("Resetting display...")
        reset.value(0)
        time.sleep_ms(10)
        reset.value(1)
        time.sleep_ms(120)
        
        # Try to send a simple command
        print("Sending wake up command...")
        cs.value(0)
        dc.value(0)  # Command mode
        spi.write(bytearray([0x11]))  # Sleep out
        cs.value(1)
        time.sleep_ms(120)
        
        print("Basic SPI test complete!")
        return True
        
    except Exception as e:
        print(f"Basic SPI test failed: {e}")
        import sys
        sys.print_exception(e)
        return False

def test_fill_screen():
    """Try to fill screen with a solid color"""
    print("Testing screen fill...")
    try:
        # Initialize SPI and pins
        spi = SPI(1, baudrate=10000000, sck=Pin(13), mosi=Pin(15))
        reset = Pin(18, Pin.OUT)
        cs = Pin(5, Pin.OUT)
        dc = Pin(23, Pin.OUT)
        backlight = Pin(12, Pin.OUT)
        
        # Turn on backlight
        backlight.value(1)
        
        # Reset display
        reset.value(0)
        time.sleep_ms(10)
        reset.value(1)
        time.sleep_ms(120)
        
        # Basic initialization
        def send_cmd(cmd):
            cs.value(0)
            dc.value(0)
            spi.write(bytearray([cmd]))
            cs.value(1)
            
        def send_data(data):
            cs.value(0)
            dc.value(1)
            if isinstance(data, int):
                spi.write(bytearray([data]))
            else:
                spi.write(data)
            cs.value(1)
        
        print("Initializing display...")
        send_cmd(0x11)  # Sleep out
        time.sleep_ms(120)
        
        send_cmd(0x3A)  # Color mode
        send_data(0x05)  # 16-bit RGB565
        
        send_cmd(0x36)  # Memory access control
        send_data(0xA0)  # Rotation
        
        send_cmd(0x21)  # Inversion on
        send_cmd(0x13)  # Normal display mode
        send_cmd(0x29)  # Display on
        
        print("Display should be initialized. Trying to fill with green...")
        
        # Set full window
        send_cmd(0x2A)  # Column set
        send_data(0x00)
        send_data(0x00)
        send_data(0x00)
        send_data(0x87)  # 135 width
        
        send_cmd(0x2B)  # Row set
        send_data(0x00)
        send_data(0x00)
        send_data(0x00)
        send_data(0xEF)  # 239 height
        
        send_cmd(0x2C)  # Memory write
        
        # Fill with green (RGB565: 0x07E0)
        green_bytes = bytearray([0x07, 0xE0])
        cs.value(0)
        dc.value(1)
        
        print("Filling screen...")
        for _ in range(135 * 240):  # All pixels
            spi.write(green_bytes)
        
        cs.value(1)
        
        print("Screen fill complete! Display should be green.")
        return True
        
    except Exception as e:
        print(f"Screen fill test failed: {e}")
        import sys
        sys.print_exception(e)
        return False

def main():
    print("Starting M5StickC PLUS display tests...")
    
    # Test 1: Backlight
    print("\n--- Test 1: Backlight ---")
    backlight_ok = test_backlight()
    
    if backlight_ok:
        # Test 2: Basic SPI
        print("\n--- Test 2: Basic SPI ---")
        spi_ok = test_basic_spi()
        
        if spi_ok:
            # Test 3: Fill Screen
            print("\n--- Test 3: Fill Screen ---")
            fill_ok = test_fill_screen()
            
            if fill_ok:
                print("\n🎉 All tests passed! Display should be working.")
            else:
                print("\n❌ Screen fill failed")
        else:
            print("\n❌ SPI communication failed")
    else:
        print("\n❌ Backlight test failed")
    
    print("\nTest complete. Check your M5StickC PLUS display!")

if __name__ == "__main__":
    main()
else:
    print("Simple display test module loaded")
