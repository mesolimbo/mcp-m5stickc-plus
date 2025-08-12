# Framebuffer vs Character-by-Character Performance Test
import time
import gc
from machine import Pin, SPI, I2C

def setup_display():
    """Common display setup"""
    # AXP192 setup
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    i2c.writeto_mem(0x34, 0x12, bytes([0xFF]))
    i2c.writeto_mem(0x34, 0x96, bytes([0x84]))
    i2c.writeto_mem(0x34, 0x95, bytes([0x02]))
    time.sleep_ms(200)
    
    # Compatible high-speed SPI
    spi = SPI(1, baudrate=26000000, sck=Pin(13), mosi=Pin(15))
    reset = Pin(18, Pin.OUT, value=1)
    cs = Pin(5, Pin.OUT, value=1)
    dc = Pin(23, Pin.OUT, value=0)
    
    # Initialize display
    reset.value(0)
    time.sleep_ms(10)
    reset.value(1)
    time.sleep_ms(100)
    
    def cmd(c):
        cs.value(0)
        dc.value(0)
        spi.write(bytearray([c]))
        cs.value(1)
    
    def data(d):
        cs.value(0)
        dc.value(1)
        if isinstance(d, int):
            spi.write(bytearray([d]))
        else:
            spi.write(d)
        cs.value(1)
    
    cmd(0x01); time.sleep_ms(120)
    cmd(0x11); time.sleep_ms(120)
    cmd(0x36); data(0x00)
    cmd(0x3A); data(0x05)
    cmd(0x21); cmd(0x13); cmd(0x29)
    time.sleep_ms(20)
    
    return spi, cs, dc, cmd, data

def test_character_by_character():
    """Test original character-by-character rendering"""
    print("Testing CHARACTER-BY-CHARACTER method...")
    
    spi, cs, dc, cmd, data = setup_display()
    
    # Test text to render
    test_lines = [
        "CLAUDE MONITOR",
        "STATUS: ACTIVE", 
        "TIME: 02H 15M",
        "COST: $2.45",
        "ALERTS: 3",
        "MODEL: SONNET",
        "UPTIME: 135M"
    ]
    
    start_time = time.ticks_ms()
    
    # Simulate drawing each character individually with window setting
    total_chars = 0
    for line_num, line in enumerate(test_lines):
        y_pos = 20 + (line_num * 20)
        
        for char_num, char in enumerate(line):
            x_pos = 5 + (char_num * 6)
            
            # Set window for single character (simulate worst case)
            cmd(0x2A)  # Column address
            data((x_pos + 52) >> 8); data((x_pos + 52) & 0xFF)
            data((x_pos + 57) >> 8); data((x_pos + 57) & 0xFF)
            
            cmd(0x2B)  # Row address
            data((y_pos + 40) >> 8); data((y_pos + 40) & 0xFF)
            data((y_pos + 47) >> 8); data((y_pos + 47) & 0xFF)
            
            cmd(0x2C)  # Memory write
            
            # Send 5x7 = 35 pixels (simulating character bitmap)
            cs.value(0)
            dc.value(1)
            for pixel in range(35):
                spi.write(bytearray([0xFF, 0xFF]))  # White pixel
            cs.value(1)
            
            total_chars += 1
    
    end_time = time.ticks_ms()
    char_time = time.ticks_diff(end_time, start_time)
    
    print(f"Character method: {total_chars} chars in {char_time}ms")
    print(f"Average per char: {char_time/total_chars:.1f}ms")
    print(f"Total screen update: {char_time}ms")
    
    return char_time, total_chars

def test_framebuffer():
    """Test framebuffer rendering"""
    print("\nTesting FRAMEBUFFER method...")
    
    spi, cs, dc, cmd, data = setup_display()
    
    # Create framebuffer (135x240 pixels, 2 bytes each)
    width, height = 135, 240
    framebuffer = bytearray(width * height * 2)
    
    start_time = time.ticks_ms()
    
    # Simulate rendering all text to framebuffer
    # (In reality, this would be done via bitmap operations)
    
    # Clear framebuffer
    for i in range(0, len(framebuffer), 2):
        framebuffer[i] = 0x00     # Black background
        framebuffer[i + 1] = 0x00
    
    # Simulate text rendering to framebuffer (much faster than real bitmap operations)
    test_lines = [
        "CLAUDE MONITOR",
        "STATUS: ACTIVE", 
        "TIME: 02H 15M",
        "COST: $2.45",
        "ALERTS: 3",
        "MODEL: SONNET",
        "UPTIME: 135M"
    ]
    
    total_chars = 0
    for line_num, line in enumerate(test_lines):
        y_start = 20 + (line_num * 20)
        
        for char_num, char in enumerate(line):
            x_start = 5 + (char_num * 6)
            
            # Simulate setting 5x7 pixels for each character in framebuffer
            for y in range(7):
                for x in range(5):
                    if x_start + x < width and y_start + y < height:
                        idx = ((y_start + y) * width + (x_start + x)) * 2
                        framebuffer[idx] = 0xFF     # White text
                        framebuffer[idx + 1] = 0xFF
            
            total_chars += 1
    
    framebuffer_time = time.ticks_ms()
    framebuffer_render_time = time.ticks_diff(framebuffer_time, start_time)
    
    # Now transfer entire framebuffer to display in ONE operation
    cmd(0x2A)  # Column address
    data(52 >> 8); data(52 & 0xFF)
    data((52 + width - 1) >> 8); data((52 + width - 1) & 0xFF)
    
    cmd(0x2B)  # Row address  
    data(40 >> 8); data(40 & 0xFF)
    data((40 + height - 1) >> 8); data((40 + height - 1) & 0xFF)
    
    cmd(0x2C)  # Memory write
    
    # Single bulk transfer
    cs.value(0)
    dc.value(1)
    spi.write(framebuffer)
    cs.value(1)
    
    end_time = time.ticks_ms()
    
    transfer_time = time.ticks_diff(end_time, framebuffer_time)
    total_time = time.ticks_diff(end_time, start_time)
    
    print(f"Framebuffer method: {total_chars} chars")
    print(f"Render to FB: {framebuffer_render_time}ms")
    print(f"Transfer to display: {transfer_time}ms")
    print(f"Total time: {total_time}ms")
    
    return total_time, total_chars, framebuffer_render_time, transfer_time

def run_framebuffer_comparison():
    """Run complete performance comparison"""
    print("M5StickC PLUS Framebuffer Performance Test")
    print("=" * 50)
    
    try:
        # Test character-by-character
        char_time, char_count = test_character_by_character()
        
        time.sleep(2)
        gc.collect()
        
        # Test framebuffer
        fb_time, fb_char_count, render_time, transfer_time = test_framebuffer()
        
        # Results
        print(f"\n" + "=" * 50)
        print("FRAMEBUFFER PERFORMANCE RESULTS")
        print("=" * 50)
        print(f"Character-by-char: {char_time}ms ({char_count} chars)")
        print(f"Framebuffer total: {fb_time}ms ({fb_char_count} chars)")
        print(f"  - Render phase: {render_time}ms")
        print(f"  - Transfer phase: {transfer_time}ms")
        print()
        
        if fb_time > 0:
            improvement = char_time / fb_time
            print(f"Speed improvement: {improvement:.1f}x faster")
            print(f"Time saved: {char_time - fb_time}ms ({((char_time - fb_time)/char_time)*100:.1f}%)")
            
            if improvement > 20:
                print("🚀 INCREDIBLE - Over 20x improvement!")
            elif improvement > 10:
                print("🚀 EXCELLENT - Over 10x improvement!")
            elif improvement > 5:
                print("✅ GREAT - Over 5x improvement!")
            else:
                print("👍 GOOD improvement")
        
        print()
        print("Key advantages of framebuffer method:")
        print("• Single SPI transaction instead of hundreds")
        print("• No window setting overhead per character")
        print("• Ability to render complex graphics")
        print("• Instant screen updates")
        print("• Better animation capabilities")
        
    except Exception as e:
        print(f"Test error: {e}")
        import sys
        sys.print_exception(e)

if __name__ == "__main__":
    run_framebuffer_comparison()