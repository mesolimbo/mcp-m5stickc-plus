"""
Memory-efficient graphics module for M5StickC PLUS
Uses smaller framebuffer sections instead of full-screen buffer
"""

import time
from machine import Pin, SPI, I2C

class M5DisplayLite:
    """Memory-efficient M5StickC PLUS display driver"""
    
    def __init__(self, brightness=True):
        print("Initializing M5StickC PLUS display (lite)...")
        
        # AXP192 power management (CRITICAL for M5StickC PLUS)
        self.i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
        self.i2c.writeto_mem(0x34, 0x12, bytes([0xFF]))  # Enable power
        self.i2c.writeto_mem(0x34, 0x96, bytes([0x84]))  # Power config
        if brightness:
            self.i2c.writeto_mem(0x34, 0x95, bytes([0x02]))  # Backlight ON
        else:
            self.i2c.writeto_mem(0x34, 0x95, bytes([0x00]))  # Backlight OFF
        time.sleep_ms(200)
        
        # SPI configuration for ST7789
        self.spi = SPI(1, baudrate=26000000, sck=Pin(13), mosi=Pin(15))
        self.reset = Pin(18, Pin.OUT, value=1)
        self.cs = Pin(5, Pin.OUT, value=1)
        self.dc = Pin(23, Pin.OUT, value=0)
        
        # Display specifications
        self.width = 135
        self.height = 240
        
        # Use smaller line buffer instead of full framebuffer
        self.line_buffer = bytearray(self.width * 2)  # One line at a time
        
        # Initialize display hardware
        self._init_hardware()
        print("Graphics lite module initialized!")
    
    def _send_cmd(self, cmd):
        """Send command to ST7789"""
        self.cs.value(0)
        self.dc.value(0)
        self.spi.write(bytearray([cmd]))
        self.cs.value(1)
    
    def _send_data(self, data):
        """Send data to ST7789"""
        self.cs.value(0)
        self.dc.value(1)
        if isinstance(data, int):
            self.spi.write(bytearray([data]))
        else:
            self.spi.write(data)
        self.cs.value(1)
    
    def _init_hardware(self):
        """Initialize ST7789 display controller"""
        # Hardware reset sequence
        self.reset.value(0)
        time.sleep_ms(10)
        self.reset.value(1)
        time.sleep_ms(120)
        
        # ST7789 initialization commands
        self._send_cmd(0x01)  # Software reset
        time.sleep_ms(150)
        
        self._send_cmd(0x11)  # Exit sleep mode
        time.sleep_ms(120)
        
        self._send_cmd(0x36)  # Memory data access control
        self._send_data(0x00)
        
        self._send_cmd(0x3A)  # Interface pixel format (RGB565)
        self._send_data(0x05)
        
        self._send_cmd(0x21)  # Display inversion ON (M5StickC PLUS)
        self._send_cmd(0x13)  # Normal display mode
        self._send_cmd(0x29)  # Display ON
        time.sleep_ms(50)
    
    def _set_window(self, x, y, w, h):
        """Set drawing window"""
        # Set window with M5StickC PLUS offsets
        x_start = x + 52
        y_start = y + 40
        x_end = x_start + w - 1
        y_end = y_start + h - 1
        
        self._send_cmd(0x2A)  # Column address set
        self._send_data(x_start >> 8)
        self._send_data(x_start & 0xFF)
        self._send_data(x_end >> 8)
        self._send_data(x_end & 0xFF)
        
        self._send_cmd(0x2B)  # Row address set
        self._send_data(y_start >> 8)
        self._send_data(y_start & 0xFF)
        self._send_data(y_end >> 8)
        self._send_data(y_end & 0xFF)
        
        self._send_cmd(0x2C)  # Memory write
    
    def clear(self, color=0x0000):
        """Clear entire screen with color"""
        # Fill line buffer with color
        high = (color >> 8) & 0xFF
        low = color & 0xFF
        
        for i in range(0, len(self.line_buffer), 2):
            self.line_buffer[i] = high
            self.line_buffer[i + 1] = low
        
        # Set full screen window
        self._set_window(0, 0, self.width, self.height)
        
        # Send line buffer for each row
        self.cs.value(0)
        self.dc.value(1)
        for _ in range(self.height):
            self.spi.write(self.line_buffer)
        self.cs.value(1)
    
    def pixel(self, x, y, color):
        """Set individual pixel"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self._set_window(x, y, 1, 1)
            self._send_data(color >> 8)
            self._send_data(color & 0xFF)
    
    def line(self, x0, y0, x1, y1, color):
        """Draw line using Bresenham's algorithm"""
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        
        x, y = x0, y0
        while True:
            self.pixel(x, y, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
    
    def rect(self, x, y, width, height, color, filled=True):
        """Draw rectangle"""
        if filled:
            # Fill line buffer with color
            high = (color >> 8) & 0xFF
            low = color & 0xFF
            
            # Clamp to screen bounds
            if x < 0:
                width += x
                x = 0
            if y < 0:
                height += y
                y = 0
            if x + width > self.width:
                width = self.width - x
            if y + height > self.height:
                height = self.height - y
            
            if width <= 0 or height <= 0:
                return
            
            # Create line buffer for this width
            temp_buffer = bytearray(width * 2)
            for i in range(0, len(temp_buffer), 2):
                temp_buffer[i] = high
                temp_buffer[i + 1] = low
            
            # Set window and send data
            self._set_window(x, y, width, height)
            self.cs.value(0)
            self.dc.value(1)
            for _ in range(height):
                self.spi.write(temp_buffer)
            self.cs.value(1)
        else:
            # Draw outline
            self.line(x, y, x + width - 1, y, color)  # Top
            self.line(x, y + height - 1, x + width - 1, y + height - 1, color)  # Bottom
            self.line(x, y, x, y + height - 1, color)  # Left
            self.line(x + width - 1, y, x + width - 1, y + height - 1, color)  # Right
    
    def text(self, x, y, string, color, bg_color=None, scale=1):
        """Draw text using built-in font"""
        pos_x = x
        for char in str(string).upper():
            self._draw_char(pos_x, y, char, color, bg_color, scale)
            pos_x += 6 * scale
    
    def _draw_char(self, x, y, char, color, bg_color=None, scale=1):
        """Draw single character using 5x7 font"""
        # Simple 5x7 font data
        font_data = {
            'A': [0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11],
            'B': [0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E],
            'C': [0x0F, 0x10, 0x10, 0x10, 0x10, 0x10, 0x0F],
            'D': [0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E],
            'E': [0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F],
            'F': [0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10],
            'G': [0x0F, 0x10, 0x10, 0x13, 0x11, 0x11, 0x0F],
            'H': [0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11],
            'I': [0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E],
            'L': [0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F],
            'M': [0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11],
            'N': [0x11, 0x19, 0x15, 0x15, 0x13, 0x11, 0x11],
            'O': [0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E],
            'P': [0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10],
            'R': [0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11],
            'S': [0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E],
            'T': [0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04],
            'U': [0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E],
            'K': [0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11],
            'Y': [0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04],
            'W': [0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11],
            '0': [0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E],
            '1': [0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E],
            '2': [0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F],
            '3': [0x1F, 0x01, 0x02, 0x06, 0x01, 0x11, 0x0E],
            '4': [0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02],
            '5': [0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E],
            '6': [0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E],
            '7': [0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x10],
            '8': [0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E],
            '9': [0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C],
            ':': [0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x0C, 0x00],
            '.': [0x00, 0x00, 0x00, 0x00, 0x00, 0x0C, 0x0C],
            '-': [0x00, 0x00, 0x00, 0x1F, 0x00, 0x00, 0x00],
            '!': [0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04],
            ' ': [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
            '+': [0x00, 0x04, 0x04, 0x1F, 0x04, 0x04, 0x00],
            '/': [0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x00],
        }
        
        if char not in font_data:
            char = ' '
        
        bitmap = font_data[char]
        
        for row in range(7):
            for col in range(5):
                if (bitmap[row] >> (4 - col)) & 1:
                    # Draw foreground pixel(s)
                    for sy in range(scale):
                        for sx in range(scale):
                            self.pixel(x + col * scale + sx, y + row * scale + sy, color)
                elif bg_color is not None:
                    # Draw background pixel(s)
                    for sy in range(scale):
                        for sx in range(scale):
                            self.pixel(x + col * scale + sx, y + row * scale + sy, bg_color)
    
    def brightness(self, on=True):
        """Control display brightness"""
        if on:
            self.i2c.writeto_mem(0x34, 0x95, bytes([0x02]))  # Backlight ON
        else:
            self.i2c.writeto_mem(0x34, 0x95, bytes([0x00]))  # Backlight OFF


# Color constants (RGB565 format)
class Colors:
    BLACK = 0x0000
    WHITE = 0xFFFF
    RED = 0xF800
    GREEN = 0x07E0
    BLUE = 0x001F
    YELLOW = 0xFFE0
    CYAN = 0x07FF
    MAGENTA = 0xF81F
    PALE_GREEN = 0x87E0
    ORANGE = 0xFD20
    PURPLE = 0x8010
    GRAY = 0x8410
    DARK_BLUE = 0x2104
    DARK_GREEN = 0x0320
    DARK_RED = 0x6000


# Utility functions
def rgb565(r, g, b):
    """Convert RGB (0-255) to RGB565 format"""
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)