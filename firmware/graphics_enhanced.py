"""
Enhanced graphics module for M5StickC PLUS with image support
Uses optimized framebuffer management
"""

import time
import gc
from machine import Pin, SPI, I2C

class M5DisplayEnhanced:
    """Enhanced M5StickC PLUS display driver with image support"""
    
    def __init__(self, brightness=True):
        print("Initializing M5StickC PLUS enhanced display...")
        
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
        
        # Create smaller framebuffer sections to avoid memory issues
        # We'll use strip-based rendering (multiple smaller buffers)
        self.strip_height = 30  # Process 30 lines at a time
        self.framebuffer = bytearray(self.width * self.strip_height * 2)
        
        # Initialize display hardware
        self._init_hardware()
        print("Enhanced graphics module initialized!")
    
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
        """Set drawing window with M5StickC PLUS offsets"""
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
        """Clear entire screen using strip rendering"""
        # Fill framebuffer with color
        high = (color >> 8) & 0xFF
        low = color & 0xFF
        
        for i in range(0, len(self.framebuffer), 2):
            self.framebuffer[i] = high
            self.framebuffer[i + 1] = low
        
        # Clear screen in strips
        for y in range(0, self.height, self.strip_height):
            strip_h = min(self.strip_height, self.height - y)
            self._set_window(0, y, self.width, strip_h)
            
            # Send strip data
            self.cs.value(0)
            self.dc.value(1)
            strip_size = self.width * strip_h * 2
            self.spi.write(self.framebuffer[:strip_size])
            self.cs.value(1)
    
    def pixel(self, x, y, color):
        """Set individual pixel (direct to display)"""
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
        """Draw rectangle using optimized strip rendering"""
        if filled:
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
            
            # Fill small buffer with color
            line_buffer = bytearray(width * 2)
            high = (color >> 8) & 0xFF
            low = color & 0xFF
            
            for i in range(0, len(line_buffer), 2):
                line_buffer[i] = high
                line_buffer[i + 1] = low
            
            # Draw rectangle line by line
            self._set_window(x, y, width, height)
            self.cs.value(0)
            self.dc.value(1)
            for _ in range(height):
                self.spi.write(line_buffer)
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
            'V': [0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04],
            'X': [0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11],
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
    
    def display_image(self, image_data, x=0, y=0, width=135, height=240):
        """Display image from RGB565 data"""
        print(f"Displaying image at ({x},{y}) size {width}x{height}")
        
        # Display image in strips to manage memory
        strip_height = min(self.strip_height, len(image_data) // (width * 2))
        
        for strip_y in range(0, height, strip_height):
            current_strip_height = min(strip_height, height - strip_y)
            
            # Calculate data offset for this strip
            data_offset = strip_y * width * 2
            data_size = current_strip_height * width * 2
            
            # Set window for this strip
            self._set_window(x, y + strip_y, width, current_strip_height)
            
            # Send image data for this strip
            self.cs.value(0)
            self.dc.value(1)
            self.spi.write(image_data[data_offset:data_offset + data_size])
            self.cs.value(1)
            
            # Small delay and garbage collection
            time.sleep_ms(10)
            gc.collect()
    
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

def create_volcano_image():
    """Create volcano image data in RGB565 format for M5StickC PLUS"""
    # This creates a simple volcano-like image using gradients
    # In a real implementation, you'd convert the PNG to RGB565 data
    
    image_data = bytearray(135 * 240 * 2)  # RGB565 format
    
    for y in range(240):
        for x in range(135):
            # Create a simple volcano scene
            if y < 60:
                # Sky - blue gradient
                blue_intensity = 100 + int(100 * (60 - y) / 60)
                color = rgb565(50, 100, blue_intensity)
            elif y < 120:
                # Mountain slope
                # Create triangle mountain peak
                peak_x = 67  # Center
                mountain_width = abs(x - peak_x) + (y - 60) * 1.5
                
                if mountain_width < 60:
                    # Mountain slope - dark gray to brown
                    intensity = int(60 + mountain_width)
                    color = rgb565(intensity, intensity - 20, intensity - 30)
                else:
                    # Sky
                    color = rgb565(100, 150, 200)
            elif y < 180:
                # Volcano crater and slopes
                center_dist = abs(x - 67)
                if center_dist < 20 and y > 80 and y < 140:
                    # Lava/crater - red/orange
                    red_intensity = 255 - int(center_dist * 4)
                    color = rgb565(red_intensity, red_intensity // 3, 0)
                else:
                    # Rocky slopes - dark brown/gray
                    rock_intensity = 40 + int((180 - y) / 2)
                    color = rgb565(rock_intensity, rock_intensity - 10, rock_intensity - 20)
            else:
                # Foreground - green vegetation
                green_variation = 80 + int((x + y) % 40)
                color = rgb565(20, green_variation, 30)
            
            # Write pixel to image data
            pixel_index = (y * 135 + x) * 2
            image_data[pixel_index] = (color >> 8) & 0xFF
            image_data[pixel_index + 1] = color & 0xFF
    
    return image_data