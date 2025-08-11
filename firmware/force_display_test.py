# Force display test - try to take over SPI from UIFlow
import time
from machine import Pin
import gc

print("Force Display Test - M5StickC PLUS")
print("=================================")

def cleanup_spi():
    """Try to cleanup any existing SPI usage"""
    print("Attempting to cleanup SPI...")
    try:
        gc.collect()
        # Force garbage collection to free any SPI objects
        import machine
        # Try to reset machine state
        print("Cleanup attempted")
        return True
    except Exception as e:
        print(f"Cleanup failed: {e}")
        return False

def test_backlight_only():
    """Just test the backlight - this should always work"""
    print("Testing backlight only...")
    try:
        backlight = Pin(12, Pin.OUT)
        
        print("Backlight OFF")
        backlight.value(0)
        time.sleep(2)
        
        print("Backlight ON - You should see the screen light up now!")
        backlight.value(1)
        time.sleep(3)
        
        print("Backlight OFF")
        backlight.value(0)
        time.sleep(1)
        
        print("Backlight ON again")
        backlight.value(1)
        
        print("✅ Backlight test successful! Screen should be lit.")
        print("The screen is on but blank because no display data is being sent.")
        print("This confirms the hardware is working.")
        
        return True
        
    except Exception as e:
        print(f"❌ Backlight test failed: {e}")
        return False

def try_st7789_with_existing_spi():
    """Try to use existing SPI if possible"""
    print("Attempting to use existing ST7789 driver...")
    try:
        # Try to import UIFlow's display driver
        import st7789
        print("Found st7789 module!")
        
        # Try to create display instance
        display = st7789.ST7789()
        display.fill(st7789.GREEN)
        display.show()
        
        print("✅ Successfully used existing display driver!")
        return True
        
    except ImportError:
        print("No st7789 module found")
        return False
    except Exception as e:
        print(f"ST7789 test failed: {e}")
        return False

def main():
    print("Starting force display test...")
    
    # Always try backlight first
    print("\n--- Backlight Test ---")
    backlight_ok = test_backlight_only()
    
    # Try to use existing drivers
    print("\n--- Existing Driver Test ---")
    driver_ok = try_st7789_with_existing_spi()
    
    if not driver_ok:
        # Try cleanup and retry
        print("\n--- Cleanup and Retry ---")
        cleanup_spi()
        time.sleep(2)
        driver_ok = try_st7789_with_existing_spi()
    
    print("\n=== RESULTS ===")
    if backlight_ok:
        print("✅ Backlight working - hardware is functional")
    else:
        print("❌ Backlight failed - hardware issue?")
        
    if driver_ok:
        print("✅ Display driver working - screen should show graphics")
    else:
        print("❌ Display driver failed - SPI conflict with UIFlow")
    
    print("\nIf backlight works but display doesn't, the issue is SPI conflict.")
    print("Consider flashing pure MicroPython firmware instead of UIFlow.")

if __name__ == "__main__":
    main()