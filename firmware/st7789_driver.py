# Simple ST7789 LCD driver for M5StickC PLUS
# Based on ST7789 datasheet and MicroPython SPI

from machine import Pin, SPI
import time

class ST7789:
    def __init__(self, spi, width=135, height=240, reset=None, cs=None, dc=None, backlight=None, rotation=0):
        self.spi = spi
        self.width = width
        self.height = height
        self.reset = reset
        self.cs = cs
        self.dc = dc
        self.backlight = backlight
        self.rotation = rotation
        
        # Initialize pins
        if self.reset:
            self.reset.init(Pin.OUT, value=1)
        if self.cs:
            self.cs.init(Pin.OUT, value=1)
        if self.dc:
            self.dc.init(Pin.OUT, value=0)
        if self.backlight:
            self.backlight.init(Pin.OUT, value=1)
            
        self.init_display()
    
    def write_cmd(self, cmd):
        """Write command to display"""
        if self.cs:
            self.cs.value(0)
        if self.dc:
            self.dc.value(0)  # Command mode
        self.spi.write(bytearray([cmd]))
        if self.cs:
            self.cs.value(1)
    
    def write_data(self, data):
        """Write data to display"""
        if self.cs:
            self.cs.value(0)
        if self.dc:
            self.dc.value(1)  # Data mode
        if isinstance(data, int):
            self.spi.write(bytearray([data]))
        else:
            self.spi.write(data)
        if self.cs:
            self.cs.value(1)
    
    def init_display(self):
        """Initialize ST7789 display"""
        # Reset sequence
        if self.reset:
            self.reset.value(0)
            time.sleep_ms(10)
            self.reset.value(1)
            time.sleep_ms(120)
        
        # ST7789 initialization sequence
        self.write_cmd(0x01)  # SWRESET
        time.sleep_ms(150)
        
        self.write_cmd(0x11)  # SLPOUT
        time.sleep_ms(120)
        
        # Color mode - 16bit RGB565
        self.write_cmd(0x3A)
        self.write_data(0x05)
        
        # Memory access control
        self.write_cmd(0x36)
        if self.rotation == 0:
            self.write_data(0x00)
        elif self.rotation == 1:
            self.write_data(0x60)
        elif self.rotation == 2:
            self.write_data(0xC0)
        elif self.rotation == 3:
            self.write_data(0xA0)
        
        # Column address set
        self.write_cmd(0x2A)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data((self.width >> 8) & 0xFF)
        self.write_data(self.width & 0xFF)
        
        # Row address set
        self.write_cmd(0x2B)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data((self.height >> 8) & 0xFF)
        self.write_data(self.height & 0xFF)
        
        # Display inversion on (M5StickC PLUS specific)
        self.write_cmd(0x21)
        
        # Normal display on
        self.write_cmd(0x13)
        
        # Display on
        self.write_cmd(0x29)
        time.sleep_ms(10)
        
        # Set backlight
        if self.backlight:
            self.backlight.value(1)
        
        print("ST7789 display initialized")
    
    def set_window(self, x0, y0, x1, y1):
        """Set drawing window"""
        self.write_cmd(0x2A)  # Column address set
        self.write_data(x0 >> 8)
        self.write_data(x0 & 0xFF)
        self.write_data(x1 >> 8)
        self.write_data(x1 & 0xFF)
        
        self.write_cmd(0x2B)  # Row address set
        self.write_data(y0 >> 8)
        self.write_data(y0 & 0xFF)
        self.write_data(y1 >> 8)
        self.write_data(y1 & 0xFF)
        
        self.write_cmd(0x2C)  # Memory write
    
    def fill(self, color):
        """Fill entire screen with color"""
        self.set_window(0, 0, self.width - 1, self.height - 1)
        
        # Send color data
        color_bytes = bytearray([(color >> 8) & 0xFF, color & 0xFF])
        pixel_count = self.width * self.height
        
        if self.cs:
            self.cs.value(0)
        if self.dc:
            self.dc.value(1)  # Data mode
        
        # Send color for each pixel
        for _ in range(pixel_count):
            self.spi.write(color_bytes)
        
        if self.cs:
            self.cs.value(1)
    
    def pixel(self, x, y, color):
        """Set single pixel"""
        if x >= self.width or y >= self.height or x < 0 or y < 0:
            return
        
        self.set_window(x, y, x, y)
        self.write_data(color >> 8)
        self.write_data(color & 0xFF)
    
    def hline(self, x, y, w, color):
        """Draw horizontal line"""
        if y >= self.height or y < 0:
            return
        if x >= self.width:
            return
        if x + w > self.width:
            w = self.width - x
        
        self.set_window(x, y, x + w - 1, y)
        color_bytes = bytearray([(color >> 8) & 0xFF, color & 0xFF])
        
        if self.cs:
            self.cs.value(0)
        if self.dc:
            self.dc.value(1)
        
        for _ in range(w):
            self.spi.write(color_bytes)
        
        if self.cs:
            self.cs.value(1)
    
    def vline(self, x, y, h, color):
        """Draw vertical line"""
        if x >= self.width or x < 0:
            return
        if y >= self.height:
            return
        if y + h > self.height:
            h = self.height - y
        
        for i in range(h):
            self.pixel(x, y + i, color)
    
    def rect(self, x, y, w, h, color):
        """Draw rectangle outline"""
        self.hline(x, y, w, color)
        self.hline(x, y + h - 1, w, color)
        self.vline(x, y, h, color)
        self.vline(x + w - 1, y, h, color)
    
    def fill_rect(self, x, y, w, h, color):
        """Fill rectangle"""
        if x >= self.width or y >= self.height:
            return
        if x + w > self.width:
            w = self.width - x
        if y + h > self.height:
            h = self.height - y
        
        for row in range(h):
            self.hline(x, y + row, w, color)
    
    def text(self, string, x, y, color, size=1):
        """Draw simple text (very basic 8x8 font)"""
        # Simple 8x8 bitmap font for basic characters
        font_8x8 = {
            ' ': [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
            'A': [0x7E, 0x81, 0x81, 0xFF, 0x81, 0x81, 0x81, 0x00],
            'C': [0x7E, 0x81, 0x80, 0x80, 0x80, 0x81, 0x7E, 0x00],
            'E': [0xFF, 0x80, 0x80, 0xFE, 0x80, 0x80, 0xFF, 0x00],
            'I': [0xFF, 0x18, 0x18, 0x18, 0x18, 0x18, 0xFF, 0x00],
            'L': [0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0xFF, 0x00],
            'M': [0x81, 0xC3, 0xA5, 0x99, 0x81, 0x81, 0x81, 0x00],
            'O': [0x7E, 0x81, 0x81, 0x81, 0x81, 0x81, 0x7E, 0x00],
            'R': [0xFE, 0x81, 0x81, 0xFE, 0x90, 0x88, 0x84, 0x00],
            'T': [0xFF, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x00],
            'U': [0x81, 0x81, 0x81, 0x81, 0x81, 0x81, 0x7E, 0x00],
            'D': [0xFC, 0x82, 0x81, 0x81, 0x81, 0x82, 0xFC, 0x00],
            'N': [0x81, 0xC1, 0xA1, 0x91, 0x89, 0x85, 0x83, 0x00],
            '5': [0xFF, 0x80, 0x80, 0xFE, 0x01, 0x01, 0xFE, 0x00],
            'S': [0x7E, 0x80, 0x80, 0x7E, 0x01, 0x01, 0x7E, 0x00],
            'P': [0xFE, 0x81, 0x81, 0xFE, 0x80, 0x80, 0x80, 0x00],
            'Y': [0x81, 0x42, 0x24, 0x18, 0x18, 0x18, 0x18, 0x00],
            ':': [0x00, 0x18, 0x18, 0x00, 0x18, 0x18, 0x00, 0x00],
            '0': [0x7E, 0x81, 0x89, 0x95, 0xA1, 0x81, 0x7E, 0x00],
            '1': [0x10, 0x30, 0x10, 0x10, 0x10, 0x10, 0x7C, 0x00],
            '2': [0x7E, 0x01, 0x01, 0x7E, 0x80, 0x80, 0xFF, 0x00],
            '3': [0x7E, 0x01, 0x01, 0x3E, 0x01, 0x01, 0x7E, 0x00],
            '4': [0x81, 0x81, 0x81, 0xFF, 0x01, 0x01, 0x01, 0x00],
            '6': [0x7E, 0x80, 0x80, 0xFE, 0x81, 0x81, 0x7E, 0x00],
            '7': [0xFF, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x00],
            '8': [0x7E, 0x81, 0x81, 0x7E, 0x81, 0x81, 0x7E, 0x00],
            '9': [0x7E, 0x81, 0x81, 0x7F, 0x01, 0x01, 0x7E, 0x00],
            '$': [0x10, 0x7E, 0x90, 0x7C, 0x12, 0xFC, 0x10, 0x00],
            '.': [0x00, 0x00, 0x00, 0x00, 0x00, 0x18, 0x18, 0x00]
        }
        
        for i, char in enumerate(string):
            if char.upper() in font_8x8:
                pattern = font_8x8[char.upper()]
                char_x = x + i * 8 * size
                
                for row in range(8):
                    for col in range(8):
                        if pattern[row] & (0x80 >> col):
                            if size == 1:
                                self.pixel(char_x + col, y + row, color)
                            else:
                                self.fill_rect(char_x + col * size, y + row * size, size, size, color)
    
    def brightness(self, value):
        """Set backlight brightness (0-100)"""
        if self.backlight:
            # Simple on/off for now
            self.backlight.value(1 if value > 0 else 0)
