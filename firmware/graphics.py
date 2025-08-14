"""
Graphics module for M5StickC PLUS
Provides display initialization and drawing functions
"""

import time
from machine import Pin, SPI, I2C

class M5Display:
    """M5StickC PLUS display driver with graphics functions"""
    
    def __init__(self, brightness=True, swap_bytes=True):
        print("Initializing M5StickC PLUS display...")
        
        # Store byte swap setting (like M5.Lcd.setSwapBytes)
        self.swap_bytes = swap_bytes
        
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
        
        # Create framebuffer (2 bytes per pixel for RGB565)
        self.framebuffer = bytearray(self.width * self.height * 2)
        
        # Initialize display hardware
        self._init_hardware()
        print("Graphics module initialized!")
    
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
    
    def clear(self, color=0x0000):
        """Clear framebuffer with specified color"""
        high = (color >> 8) & 0xFF
        low = color & 0xFF
        
        for i in range(0, len(self.framebuffer), 2):
            self.framebuffer[i] = high
            self.framebuffer[i + 1] = low
    
    def pixel(self, x, y, color):
        """Set individual pixel"""
        if 0 <= x < self.width and 0 <= y < self.height:
            index = (y * self.width + x) * 2
            self.framebuffer[index] = (color >> 8) & 0xFF
            self.framebuffer[index + 1] = color & 0xFF
    
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
        """Draw rectangle (filled or outline)"""
        if filled:
            for py in range(y, min(y + height, self.height)):
                for px in range(x, min(x + width, self.width)):
                    self.pixel(px, py, color)
        else:
            # Draw outline
            self.line(x, y, x + width - 1, y, color)  # Top
            self.line(x, y + height - 1, x + width - 1, y + height - 1, color)  # Bottom
            self.line(x, y, x, y + height - 1, color)  # Left
            self.line(x + width - 1, y, x + width - 1, y + height - 1, color)  # Right
    
    def circle(self, cx, cy, radius, color, filled=False):
        """Draw circle using midpoint algorithm"""
        if filled:
            # Filled circle
            for y in range(-radius, radius + 1):
                for x in range(-radius, radius + 1):
                    if x*x + y*y <= radius*radius:
                        self.pixel(cx + x, cy + y, color)
        else:
            # Circle outline
            x = radius
            y = 0
            err = 0
            
            while x >= y:
                self.pixel(cx + x, cy + y, color)
                self.pixel(cx + y, cy + x, color)
                self.pixel(cx - y, cy + x, color)
                self.pixel(cx - x, cy + y, color)
                self.pixel(cx - x, cy - y, color)
                self.pixel(cx - y, cy - x, color)
                self.pixel(cx + y, cy - x, color)
                self.pixel(cx + x, cy - y, color)
                
                if err <= 0:
                    y += 1
                    err += 2*y + 1
                if err > 0:
                    x -= 1
                    err -= 2*x + 1
    
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
            'J': [0x07, 0x01, 0x01, 0x01, 0x01, 0x11, 0x0E],
            'K': [0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11],
            'L': [0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F],
            'M': [0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11],
            'N': [0x11, 0x19, 0x15, 0x15, 0x13, 0x11, 0x11],
            'O': [0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E],
            'P': [0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10],
            'Q': [0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D],
            'R': [0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11],
            'S': [0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E],
            'T': [0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04],
            'U': [0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E],
            'V': [0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04],
            'W': [0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11],
            'X': [0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11],
            'Y': [0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04],
            'Z': [0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F],
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
    
    def set_window(self, x, y, w, h):
        """Set display window for direct writing (scanline streaming)"""
        # M5StickC PLUS display offsets (back to original values)
        x_offset = 52
        y_offset = 40
        
        # Column address set
        self._send_cmd(0x2A)
        self._send_data((x_offset + x) >> 8)
        self._send_data((x_offset + x) & 0xFF)
        self._send_data((x_offset + x + w - 1) >> 8)
        self._send_data((x_offset + x + w - 1) & 0xFF)
        
        # Row address set  
        self._send_cmd(0x2B)
        self._send_data((y_offset + y) >> 8)
        self._send_data((y_offset + y) & 0xFF)
        self._send_data((y_offset + y + h - 1) >> 8)
        self._send_data((y_offset + y + h - 1) & 0xFF)
        
        # Memory write command
        self._send_cmd(0x2C)
    
    def write(self, data):
        """Write raw data to display (for scanline streaming)"""
        if self.swap_bytes and len(data) >= 2:
            # Swap bytes if needed (like M5.Lcd.setSwapBytes)
            swapped = bytearray(len(data))
            for i in range(0, len(data), 2):
                if i + 1 < len(data):
                    swapped[i] = data[i + 1]
                    swapped[i + 1] = data[i]
                else:
                    swapped[i] = data[i]
            data = swapped
        
        self.cs.value(0)
        self.dc.value(1)
        self.spi.write(data)
        self.cs.value(1)
    
    def show(self):
        """Transfer framebuffer to display"""
        # Set window with M5StickC PLUS offsets for framebuffer
        self._send_cmd(0x2A)  # Column address set
        self._send_data(52 >> 8)
        self._send_data(52 & 0xFF)
        self._send_data((52 + self.width - 1) >> 8)
        self._send_data((52 + self.width - 1) & 0xFF)
        
        self._send_cmd(0x2B)  # Row address set
        self._send_data(40 >> 8)
        self._send_data(40 & 0xFF)
        self._send_data((40 + self.height - 1) >> 8)
        self._send_data((40 + self.height - 1) & 0xFF)
        
        self._send_cmd(0x2C)  # Memory write
        
        # Send framebuffer data directly (no byte swapping)
        self.cs.value(0)
        self.dc.value(1)
        self.spi.write(self.framebuffer)
        self.cs.value(1)
    
    def brightness(self, on=True):
        """Control display brightness"""
        if on:
            self.i2c.writeto_mem(0x34, 0x95, bytes([0x02]))  # Backlight ON
        else:
            self.i2c.writeto_mem(0x34, 0x95, bytes([0x00]))  # Backlight OFF
    
    def draw_bitmap(self, x, y, width, height, bitmap_data):
        """Draw RGB565 bitmap image"""
        if not isinstance(bitmap_data, (bytes, bytearray)):
            raise ValueError("Bitmap data must be bytes or bytearray")
        
        expected_size = width * height * 2  # 2 bytes per pixel for RGB565
        if len(bitmap_data) < expected_size:
            raise ValueError(f"Bitmap data too small: got {len(bitmap_data)}, expected {expected_size}")
        
        for py in range(height):
            for px in range(width):
                screen_x = x + px
                screen_y = y + py
                
                if 0 <= screen_x < self.width and 0 <= screen_y < self.height:
                    # Calculate bitmap index (2 bytes per pixel)
                    bitmap_index = (py * width + px) * 2
                    
                    # Extract RGB565 color (little endian format)
                    low_byte = bitmap_data[bitmap_index]
                    high_byte = bitmap_data[bitmap_index + 1]
                    color = (high_byte << 8) | low_byte
                    
                    self.pixel(screen_x, screen_y, color)
    
    def draw_bitmap_scaled(self, x, y, width, height, bitmap_data, scale_x=1, scale_y=1):
        """Draw RGB565 bitmap image with scaling"""
        if not isinstance(bitmap_data, (bytes, bytearray)):
            raise ValueError("Bitmap data must be bytes or bytearray")
        
        expected_size = width * height * 2
        if len(bitmap_data) < expected_size:
            raise ValueError(f"Bitmap data too small: got {len(bitmap_data)}, expected {expected_size}")
        
        for py in range(height):
            for px in range(width):
                # Calculate bitmap index
                bitmap_index = (py * width + px) * 2
                
                # Extract RGB565 color (little endian format)
                low_byte = bitmap_data[bitmap_index]
                high_byte = bitmap_data[bitmap_index + 1]
                color = (high_byte << 8) | low_byte
                
                # Draw scaled pixel(s)
                for sy in range(scale_y):
                    for sx in range(scale_x):
                        screen_x = x + px * scale_x + sx
                        screen_y = y + py * scale_y + sy
                        
                        if 0 <= screen_x < self.width and 0 <= screen_y < self.height:
                            self.pixel(screen_x, screen_y, color)
    
    def draw_rgb565_file(self, path, x=0, y=0, w=None, h=None):
        """Draw RGB565 file using scanline streaming (from cheatsheet)"""
        if w is None:
            w = self.width
        if h is None:
            h = self.height
            
        line_bytes = w * 2
        
        try:
            with open(path, 'rb') as f:
                for row in range(h):
                    buf = f.read(line_bytes)
                    if not buf or len(buf) < line_bytes:
                        break
                    
                    # Set window for this scanline
                    self.set_window(x, y + row, w, 1)
                    # Write scanline directly
                    self.write(buf)
            
            return True
            
        except Exception as e:
            print(f"Error drawing RGB565 file: {e}")
            return False


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

def create_rgb565_bitmap(width, height, fill_color=0x0000):
    """Create an empty RGB565 bitmap"""
    size = width * height * 2
    bitmap = bytearray(size)
    
    # Fill with color if specified
    if fill_color != 0x0000:
        high_byte = (fill_color >> 8) & 0xFF
        low_byte = fill_color & 0xFF
        
        for i in range(0, size, 2):
            bitmap[i] = low_byte      # Little endian
            bitmap[i + 1] = high_byte
    
    return bitmap

def load_rgb565_file(filename):
    """Load RGB565 bitmap from file"""
    try:
        with open(filename, 'rb') as f:
            return f.read()
    except OSError as e:
        print(f"Error loading bitmap file {filename}: {e}")
        return None

def save_rgb565_file(filename, bitmap_data):
    """Save RGB565 bitmap to file"""
    try:
        with open(filename, 'wb') as f:
            f.write(bitmap_data)
        return True
    except OSError as e:
        print(f"Error saving bitmap file {filename}: {e}")
        return False

def hsv_to_rgb565(h, s, v):
    """Convert HSV to RGB565 (h: 0-360, s,v: 0-1)"""
    import math
    
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c
    
    if h < 60:
        r, g, b = c, x, 0
    elif h < 120:
        r, g, b = x, c, 0
    elif h < 180:
        r, g, b = 0, c, x
    elif h < 240:
        r, g, b = 0, x, c
    elif h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    
    r = int((r + m) * 255)
    g = int((g + m) * 255)
    b = int((b + m) * 255)
    
    return rgb565(r, g, b)