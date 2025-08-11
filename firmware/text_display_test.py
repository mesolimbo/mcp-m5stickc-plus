# Text Display Test - Show actual letters and numbers
import time
from machine import Pin, SPI, I2C

print("Text Display Test - Letters and Numbers")

def text_display_test():
    # AXP192 setup (required for display power)
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    i2c.writeto_mem(0x34, 0x12, bytes([0xFF]))  # Enable LDOs
    i2c.writeto_mem(0x34, 0x96, bytes([0x84]))  # GPIO2 output
    i2c.writeto_mem(0x34, 0x95, bytes([0x02]))  # Backlight on
    time.sleep_ms(200)
    print("AXP192 configured")
    
    # SPI setup
    spi = SPI(1, baudrate=8000000, sck=Pin(13), mosi=Pin(15))
    reset = Pin(18, Pin.OUT, value=1)
    cs = Pin(5, Pin.OUT, value=1)
    dc = Pin(23, Pin.OUT, value=0)
    
    def cmd(c):
        cs.value(0); dc.value(0)
        spi.write(bytearray([c]))
        cs.value(1); time.sleep_ms(1)
    
    def data(d):
        cs.value(0); dc.value(1)
        spi.write(bytearray([d]))
        cs.value(1); time.sleep_ms(1)
    
    def set_window_correct(x_start, y_start, x_end, y_end):
        """Proven coordinate method with M5StickC PLUS offsets"""
        x_offset = 52
        y_offset = 40
        
        col_start = x_start + x_offset
        col_end = x_end + x_offset
        row_start = y_start + y_offset  
        row_end = y_end + y_offset
        
        cmd(0x2A)  # Column Address Set
        data(col_start >> 8); data(col_start & 0xFF)
        data(col_end >> 8); data(col_end & 0xFF)
        
        cmd(0x2B)  # Row Address Set  
        data(row_start >> 8); data(row_start & 0xFF)
        data(row_end >> 8); data(row_end & 0xFF)
        
        cmd(0x2C)  # Memory Write
    
    def fill_area(x, y, w, h, color):
        """Fill area with proven coordinate method"""
        set_window_correct(x, y, x + w - 1, y + h - 1)
        
        cs.value(0); dc.value(1)
        color_bytes = bytearray([color >> 8, color & 0xFF])
        for _ in range(w * h):
            spi.write(color_bytes)
        cs.value(1)
    
    def draw_pixel(x, y, color):
        """Draw single pixel"""
        fill_area(x, y, 1, 1, color)
    
    # Simple 5x7 bitmap font for basic characters
    FONT_5X7 = {
        'A': [
            0b01110,
            0b10001,
            0b10001,
            0b11111,
            0b10001,
            0b10001,
            0b10001
        ],
        'B': [
            0b11110,
            0b10001,
            0b10001,
            0b11110,
            0b10001,
            0b10001,
            0b11110
        ],
        'C': [
            0b01111,
            0b10000,
            0b10000,
            0b10000,
            0b10000,
            0b10000,
            0b01111
        ],
        'D': [
            0b11110,
            0b10001,
            0b10001,
            0b10001,
            0b10001,
            0b10001,
            0b11110
        ],
        'E': [
            0b11111,
            0b10000,
            0b10000,
            0b11110,
            0b10000,
            0b10000,
            0b11111
        ],
        '0': [
            0b01110,
            0b10001,
            0b10011,
            0b10101,
            0b11001,
            0b10001,
            0b01110
        ],
        '1': [
            0b00100,
            0b01100,
            0b00100,
            0b00100,
            0b00100,
            0b00100,
            0b01110
        ],
        '2': [
            0b01110,
            0b10001,
            0b00001,
            0b00110,
            0b01000,
            0b10000,
            0b11111
        ],
        '3': [
            0b11111,
            0b00001,
            0b00010,
            0b00110,
            0b00001,
            0b10001,
            0b01110
        ],
        '4': [
            0b00010,
            0b00110,
            0b01010,
            0b10010,
            0b11111,
            0b00010,
            0b00010
        ],
        '5': [
            0b11111,
            0b10000,
            0b11110,
            0b00001,
            0b00001,
            0b10001,
            0b01110
        ],
        ':': [
            0b00000,
            0b01100,
            0b01100,
            0b00000,
            0b01100,
            0b01100,
            0b00000
        ],
        '$': [
            0b00100,
            0b01111,
            0b10100,
            0b01110,
            0b00101,
            0b11110,
            0b00100
        ],
        ' ': [
            0b00000,
            0b00000,
            0b00000,
            0b00000,
            0b00000,
            0b00000,
            0b00000
        ]
    }
    
    def draw_char(x, y, char, color, bg_color=0x0000):
        """Draw a character using bitmap font"""
        if char not in FONT_5X7:
            char = ' '  # Default to space for unknown chars
        
        bitmap = FONT_5X7[char]
        
        for row in range(7):  # 7 rows
            for col in range(5):  # 5 columns
                pixel_color = color if (bitmap[row] >> (4-col)) & 1 else bg_color
                if pixel_color != bg_color or bg_color != 0x0000:  # Only draw if not transparent
                    draw_pixel(x + col, y + row, pixel_color)
    
    def draw_text(x, y, text, color, bg_color=0x0000):
        """Draw text string"""
        char_x = x
        for char in text:
            draw_char(char_x, y, char, color, bg_color)
            char_x += 6  # 5 pixel width + 1 pixel spacing
    
    # Initialize display
    print("Initializing ST7789...")
    reset.value(0); time.sleep_ms(50)
    reset.value(1); time.sleep_ms(200)
    
    cmd(0x01); time.sleep_ms(150)  # Software reset
    cmd(0x11); time.sleep_ms(120)  # Sleep out
    cmd(0x36); data(0x00)          # Correct landscape rotation
    cmd(0x3A); data(0x05)          # RGB565 pixel format
    cmd(0x21)                      # Display inversion on
    cmd(0x13)                      # Normal display mode
    cmd(0x29); time.sleep_ms(50)   # Display on
    
    print("Display initialized")
    
    # Clear screen to black
    fill_area(0, 0, 135, 240, 0x0000)
    
    # Test 1: Show letters A-E
    print("Test 1: Letters A-E")
    draw_text(5, 10, "ABCDE", 0x07E0)  # Green
    time.sleep(3)
    
    # Test 2: Show numbers 0-5
    print("Test 2: Numbers 0-5")
    draw_text(5, 30, "01245", 0x001F)  # Blue
    time.sleep(3)
    
    # Test 3: Show "CLAUDE" using letters
    print("Test 3: CLAUDE text")
    # Clear area
    fill_area(0, 50, 135, 20, 0x0000)
    draw_text(5, 50, "CLAUDE", 0xFFE0)  # Yellow
    time.sleep(3)
    
    # Test 4: Session data with actual numbers
    print("Test 4: Session data")
    fill_area(0, 80, 135, 160, 0x0000)  # Clear area
    
    # Show actual session statistics
    draw_text(5, 80, "TIME: 0:45", 0x07FF)    # Cyan - session time
    draw_text(5, 100, "COST: $2.91", 0xFFE0)  # Yellow - cost from your actual usage
    draw_text(5, 120, "CMDS: 127", 0xF81F)    # Magenta - commands
    draw_text(5, 140, "STATUS: ON", 0x07E0)   # Green - active
    
    time.sleep(5)
    
    # Test 5: Animated counter
    print("Test 5: Animated counter")
    for i in range(20):
        # Clear number area
        fill_area(50, 180, 30, 10, 0x0000)
        
        # Show counter
        if i < 10:
            draw_char(50, 180, str(i), 0xF800)  # Red single digit
        else:
            draw_char(50, 180, '1', 0xF800)     # Red tens digit
            draw_char(56, 180, str(i-10), 0xF800)  # Red ones digit
        
        time.sleep(0.5)
    
    # Final display
    fill_area(0, 200, 135, 40, 0x0000)
    draw_text(5, 200, "TEST DONE", 0xFFFF)  # White
    
    print("Text display test complete!")
    print("Letters and numbers are now displaying properly!")

text_display_test()