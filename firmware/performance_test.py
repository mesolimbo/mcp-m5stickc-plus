# Performance test for display optimization
import time
import gc
from machine import Pin, SPI, I2C

def setup_axp192():
    """Setup power management"""
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    i2c.writeto_mem(0x34, 0x12, bytes([0xFF]))
    i2c.writeto_mem(0x34, 0x96, bytes([0x84]))
    i2c.writeto_mem(0x34, 0x95, bytes([0x02]))
    time.sleep_ms(200)
    return i2c

def test_original_speed():
    """Test original slow method"""
    print("Testing ORIGINAL method...")
    
    setup_axp192()
    
    # Original slow SPI setup
    spi = SPI(1, baudrate=8000000, sck=Pin(13), mosi=Pin(15))
    reset = Pin(18, Pin.OUT, value=1)
    cs = Pin(5, Pin.OUT, value=1)
    dc = Pin(23, Pin.OUT, value=0)
    
    # Init display
    reset.value(0)
    time.sleep_ms(50)
    reset.value(1)
    time.sleep_ms(200)
    
    def slow_cmd(c):
        cs.value(0)
        dc.value(0)
        spi.write(bytearray([c]))
        cs.value(1)
        time.sleep_ms(1)  # Original delay
    
    def slow_data(d):
        cs.value(0)
        dc.value(1)
        spi.write(bytearray([d]))
        cs.value(1)
        time.sleep_ms(1)  # Original delay
    
    # Basic init
    slow_cmd(0x01)
    time.sleep_ms(150)
    slow_cmd(0x11)
    time.sleep_ms(120)
    slow_cmd(0x36)
    slow_data(0x00)
    slow_cmd(0x3A)
    slow_data(0x05)
    slow_cmd(0x29)
    
    # Test text rendering speed
    start_time = time.ticks_ms()
    
    # Draw test text (simulate character by character)
    test_chars = "CLAUDE MONITOR"
    char_count = 0
    for char in test_chars:
        # Simulate drawing 35 pixels per character (5x7)
        for i in range(35):
            cs.value(0)
            dc.value(1)
            spi.write(bytearray([0xFF, 0xFF]))  # White pixel
            cs.value(1)
            time.sleep_ms(1)  # Original delay per pixel
        char_count += 1
    
    end_time = time.ticks_ms()
    duration = time.ticks_diff(end_time, start_time)
    
    print(f"Original method: {char_count} chars in {duration}ms")
    print(f"Average per char: {duration/char_count:.1f}ms")
    return duration, char_count

def test_optimized_speed():
    """Test optimized fast method"""
    print("\nTesting OPTIMIZED method...")
    
    setup_axp192()
    
    # Optimized fast SPI setup
    spi = SPI(1, baudrate=40000000, sck=Pin(13), mosi=Pin(15))
    reset = Pin(18, Pin.OUT, value=1)
    cs = Pin(5, Pin.OUT, value=1)
    dc = Pin(23, Pin.OUT, value=0)
    
    # Init display
    reset.value(0)
    time.sleep_ms(10)
    reset.value(1)
    time.sleep_ms(100)
    
    def fast_cmd(c):
        cs.value(0)
        dc.value(0)
        spi.write(bytearray([c]))
        cs.value(1)
        # No delay
    
    def fast_data(d):
        cs.value(0)
        dc.value(1)
        if isinstance(d, int):
            spi.write(bytearray([d]))
        else:
            spi.write(d)
        cs.value(1)
        # No delay
    
    # Basic init
    fast_cmd(0x01)
    time.sleep_ms(120)
    fast_cmd(0x11)
    time.sleep_ms(120)
    fast_cmd(0x36)
    fast_data(0x00)
    fast_cmd(0x3A)
    fast_data(0x05)
    fast_cmd(0x29)
    
    # Test optimized text rendering
    start_time = time.ticks_ms()
    
    # Optimized bulk character drawing
    test_chars = "CLAUDE MONITOR"
    char_count = 0
    
    for char in test_chars:
        # Simulate bulk write for entire character (5x7 = 35 pixels)
        char_data = bytearray(35 * 2)  # 35 pixels * 2 bytes each
        for i in range(0, 70, 2):
            char_data[i] = 0xFF      # High byte
            char_data[i + 1] = 0xFF  # Low byte (white pixel)
        
        # Single bulk write for entire character
        cs.value(0)
        dc.value(1)
        spi.write(char_data)
        cs.value(1)
        # No delay
        char_count += 1
    
    end_time = time.ticks_ms()
    duration = time.ticks_diff(end_time, start_time)
    
    print(f"Optimized method: {char_count} chars in {duration}ms")
    print(f"Average per char: {duration/char_count:.1f}ms")
    return duration, char_count

def run_performance_test():
    """Run complete performance comparison"""
    print("M5StickC PLUS Display Performance Test")
    print("=" * 40)
    
    try:
        # Test original method
        original_time, char_count = test_original_speed()
        
        # Wait between tests
        time.sleep(2)
        gc.collect()
        
        # Test optimized method  
        optimized_time, _ = test_optimized_speed()
        
        # Calculate improvement
        improvement = original_time / optimized_time if optimized_time > 0 else 0
        
        print(f"\n" + "=" * 40)
        print("PERFORMANCE RESULTS:")
        print("=" * 40)
        print(f"Original time:   {original_time}ms")
        print(f"Optimized time:  {optimized_time}ms")
        print(f"Speed improvement: {improvement:.1f}x faster")
        print(f"Time saved: {original_time - optimized_time}ms ({((original_time - optimized_time)/original_time)*100:.1f}%)")
        
        if improvement > 10:
            print("🚀 EXCELLENT - Over 10x improvement!")
        elif improvement > 5:
            print("✅ GREAT - Over 5x improvement!")
        elif improvement > 2:
            print("👍 GOOD - Over 2x improvement!")
        else:
            print("⚠️ Marginal improvement")
        
    except Exception as e:
        print(f"Test error: {e}")
        import sys
        sys.print_exception(e)

if __name__ == "__main__":
    run_performance_test()