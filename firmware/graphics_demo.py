"""
Working Graphics Demo for M5StickC PLUS
Based on proven framebuffer approach with proper AXP192 power management
"""

import time
import gc
from machine import Pin, SPI, I2C

class M5StickCDisplay:
    def __init__(self):
        print("Initializing M5StickC PLUS display...")
        
        # AXP192 power management setup (CRITICAL for M5StickC PLUS)
        self.i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
        self.i2c.writeto_mem(0x34, 0x12, bytes([0xFF]))  # Power enable
        self.i2c.writeto_mem(0x34, 0x96, bytes([0x84]))  # Power setup
        self.i2c.writeto_mem(0x34, 0x95, bytes([0x02]))  # Backlight ON
        time.sleep_ms(200)
        
        # SPI setup for ST7789 display
        self.spi = SPI(1, baudrate=26000000, sck=Pin(13), mosi=Pin(15))
        self.reset = Pin(18, Pin.OUT, value=1)
        self.cs = Pin(5, Pin.OUT, value=1)
        self.dc = Pin(23, Pin.OUT, value=0)
        
        # Display dimensions
        self.width = 135
        self.height = 240
        
        # RGB565 Colors
        self.BLACK = 0x0000
        self.WHITE = 0xFFFF
        self.RED = 0xF800
        self.GREEN = 0x07E0
        self.BLUE = 0x001F
        self.YELLOW = 0xFFE0
        self.CYAN = 0x07FF
        self.MAGENTA = 0xF81F
        self.PALE_GREEN = 0x87E0
        self.ORANGE = 0xFD20
        self.PURPLE = 0x8010
        
        # Create framebuffer (135 x 240 pixels, 2 bytes per pixel)
        self.framebuffer = bytearray(self.width * self.height * 2)
        
        # 5x7 bitmap font
        self.FONT = {
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
            '!': [0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04],
            ' ': [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
            '.': [0x00, 0x00, 0x00, 0x00, 0x00, 0x0C, 0x0C],
            '-': [0x00, 0x00, 0x00, 0x1F, 0x00, 0x00, 0x00],
            '+': [0x00, 0x04, 0x04, 0x1F, 0x04, 0x04, 0x00],
        }
        
        # Initialize display
        self._init_display()
        print("M5StickC PLUS display ready!")
    
    def _send_cmd(self, cmd):
        """Send command to display"""
        self.cs.value(0)
        self.dc.value(0)
        self.spi.write(bytearray([cmd]))
        self.cs.value(1)
    
    def _send_data(self, data):
        """Send data to display"""
        self.cs.value(0)
        self.dc.value(1)
        if isinstance(data, int):
            self.spi.write(bytearray([data]))
        else:
            self.spi.write(data)
        self.cs.value(1)
    
    def _init_display(self):
        """Initialize ST7789 display controller"""
        # Hardware reset
        self.reset.value(0)
        time.sleep_ms(10)
        self.reset.value(1)
        time.sleep_ms(120)
        
        # ST7789 initialization sequence
        self._send_cmd(0x01)  # Software reset
        time.sleep_ms(150)
        
        self._send_cmd(0x11)  # Sleep out
        time.sleep_ms(120)
        
        self._send_cmd(0x36)  # Memory access control
        self._send_data(0x00)
        
        self._send_cmd(0x3A)  # Pixel format (RGB565)
        self._send_data(0x05)
        
        self._send_cmd(0x21)  # Display inversion ON (M5StickC PLUS specific)
        
        self._send_cmd(0x13)  # Normal display mode
        
        self._send_cmd(0x29)  # Display ON
        time.sleep_ms(50)
    
    def clear(self, color=None):
        """Clear framebuffer with color"""
        if color is None:
            color = self.BLACK
        
        high_byte = (color >> 8) & 0xFF
        low_byte = color & 0xFF
        
        for i in range(0, len(self.framebuffer), 2):
            self.framebuffer[i] = high_byte
            self.framebuffer[i + 1] = low_byte
    
    def set_pixel(self, x, y, color):
        """Set single pixel in framebuffer"""
        if 0 <= x < self.width and 0 <= y < self.height:
            index = (y * self.width + x) * 2
            self.framebuffer[index] = (color >> 8) & 0xFF
            self.framebuffer[index + 1] = color & 0xFF
    
    def draw_char(self, x, y, char, color, bg_color=None):
        """Draw character using bitmap font"""
        if char not in self.FONT:
            char = ' '
        
        bitmap = self.FONT[char]
        
        for row in range(7):
            for col in range(5):
                if (bitmap[row] >> (4 - col)) & 1:
                    self.set_pixel(x + col, y + row, color)
                elif bg_color is not None:
                    self.set_pixel(x + col, y + row, bg_color)
    
    def draw_text(self, x, y, text, color, bg_color=None):
        """Draw text string"""
        pos_x = x
        for char in str(text).upper():
            self.draw_char(pos_x, y, char, color, bg_color)
            pos_x += 6
    
    def fill_rect(self, x, y, width, height, color):
        """Fill rectangle with color"""
        for py in range(y, min(y + height, self.height)):
            for px in range(x, min(x + width, self.width)):
                self.set_pixel(px, py, color)
    
    def draw_line(self, x0, y0, x1, y1, color):
        """Draw line using Bresenham's algorithm"""
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        
        x, y = x0, y0
        
        while True:
            self.set_pixel(x, y, color)
            
            if x == x1 and y == y1:
                break
                
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
    
    def show(self):
        """Transfer framebuffer to display"""
        # Set display window with M5StickC PLUS offsets
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
        
        # Send framebuffer
        self.cs.value(0)
        self.dc.value(1)
        self.spi.write(self.framebuffer)
        self.cs.value(1)

def demo_hello_world(display):
    """Demo 1: Hello World"""
    display.clear(display.BLACK)
    
    # Title bar
    display.fill_rect(0, 0, 135, 25, display.BLUE)
    display.draw_text(15, 8, "HELLO WORLD!", display.WHITE, display.BLUE)
    
    # Main content
    display.draw_text(10, 40, "M5STICKC PLUS", display.PALE_GREEN)
    display.draw_text(20, 60, "MICROPYTHON", display.YELLOW)
    display.draw_text(10, 80, "GRAPHICS DEMO", display.CYAN)
    
    # Info section
    display.draw_text(5, 110, "VERSION: 2.0", display.WHITE)
    display.draw_text(5, 130, "FRAMEBUFFER", display.ORANGE)
    
    # Instructions
    display.fill_rect(0, 160, 135, 40, 0x2104)  # Dark blue
    display.draw_text(5, 170, "PRESS BUTTON A", display.WHITE, 0x2104)
    display.draw_text(15, 185, "FOR NEXT DEMO", display.WHITE, 0x2104)
    
    # Footer
    display.fill_rect(0, 215, 135, 25, display.GREEN)
    display.draw_text(35, 222, "WORKING!", display.WHITE, display.GREEN)
    
    display.show()

def demo_colors(display):
    """Demo 2: Color showcase"""
    display.clear(display.BLACK)
    
    # Title
    display.fill_rect(0, 0, 135, 22, display.MAGENTA)
    display.draw_text(25, 7, "COLOR DEMO", display.WHITE, display.MAGENTA)
    
    # Color swatches
    colors = [
        ("RED", display.RED, 30),
        ("GREEN", display.GREEN, 45),
        ("BLUE", display.BLUE, 60),
        ("YELLOW", display.YELLOW, 75),
        ("CYAN", display.CYAN, 90),
        ("ORANGE", display.ORANGE, 105),
        ("PURPLE", display.PURPLE, 120)
    ]
    
    for name, color, y in colors:
        display.draw_text(5, y, name, display.WHITE)
        display.fill_rect(50, y, 80, 12, color)
    
    # Rainbow gradient
    display.draw_text(5, 145, "RAINBOW:", display.WHITE)
    for i in range(120):
        if i < 20:
            color = display.RED
        elif i < 40:
            color = display.ORANGE
        elif i < 60:
            color = display.YELLOW
        elif i < 80:
            color = display.GREEN
        elif i < 100:
            color = display.CYAN
        else:
            color = display.BLUE
        
        display.draw_line(10 + i, 160, 10 + i, 170, color)
    
    display.draw_text(20, 185, "BEAUTIFUL!", display.PALE_GREEN)
    display.show()

def demo_shapes(display):
    """Demo 3: Shapes and patterns"""
    display.clear(display.BLACK)
    
    # Title
    display.fill_rect(0, 0, 135, 22, display.GREEN)
    display.draw_text(25, 7, "SHAPES DEMO", display.WHITE, display.GREEN)
    
    # Rectangles
    display.draw_text(5, 30, "RECTANGLES:", display.WHITE)
    display.fill_rect(5, 45, 25, 15, display.RED)
    display.fill_rect(35, 45, 25, 15, display.YELLOW)
    display.fill_rect(65, 45, 25, 15, display.BLUE)
    display.fill_rect(95, 45, 25, 15, display.CYAN)
    
    # Lines
    display.draw_text(5, 70, "LINES:", display.WHITE)
    display.draw_line(5, 85, 130, 85, display.WHITE)
    display.draw_line(5, 90, 130, 100, display.RED)
    display.draw_line(130, 90, 5, 100, display.BLUE)
    
    # Patterns
    display.draw_text(5, 110, "PATTERNS:", display.WHITE)
    
    # Checkerboard
    for y in range(8):
        for x in range(16):
            if (x + y) % 2:
                display.fill_rect(5 + x * 4, 125 + y * 4, 4, 4, display.WHITE)
    
    # Diagonal lines
    for i in range(0, 50, 3):
        display.draw_line(70 + i, 125, 70, 125 + i, display.YELLOW)
        display.draw_line(70, 125 + i, 70 + i, 165, display.CYAN)
    
    display.draw_text(15, 185, "GEOMETRIC ART!", display.MAGENTA)
    display.show()

def demo_animation(display):
    """Demo 4: Animation sequences"""
    display.clear(display.BLACK)
    
    # Title
    display.fill_rect(0, 0, 135, 22, display.CYAN)
    display.draw_text(20, 7, "ANIMATION!", display.BLACK, display.CYAN)
    
    # Moving ball
    display.draw_text(5, 30, "MOVING BALL:", display.WHITE)
    for x in range(110):
        # Clear previous
        if x > 0:
            display.fill_rect(x - 1, 45, 8, 8, display.BLACK)
        
        # Draw new
        display.fill_rect(x, 45, 8, 8, display.RED)
        display.show()
        time.sleep_ms(30)
    
    # Pulsing circle
    display.draw_text(5, 70, "PULSING:", display.WHITE)
    for size in range(1, 20):
        # Clear area
        display.fill_rect(50, 80, 40, 40, display.BLACK)
        
        # Draw circle
        for angle in range(0, 360, 10):
            x = int(70 + size * 0.8 * (angle / 360.0))
            y = int(100 + size * 0.8 * ((angle + 90) / 360.0))
            if 0 <= x < 135 and 0 <= y < 240:
                display.set_pixel(x, y, display.YELLOW)
        
        display.show()
        time.sleep_ms(50)
    
    # Blinking text
    display.draw_text(5, 130, "BLINKING:", display.WHITE)
    for i in range(8):
        if i % 2:
            display.fill_rect(5, 145, 125, 15, display.MAGENTA)
            display.draw_text(30, 150, "BLINK!", display.WHITE, display.MAGENTA)
        else:
            display.fill_rect(5, 145, 125, 15, display.BLACK)
        
        display.show()
        time.sleep_ms(250)
    
    # Success message
    display.fill_rect(0, 170, 135, 30, display.GREEN)
    display.draw_text(15, 180, "ANIMATION", display.WHITE, display.GREEN)
    display.draw_text(25, 195, "COMPLETE!", display.WHITE, display.GREEN)
    display.show()

def demo_interactive(display):
    """Demo 5: Interactive features"""
    display.clear(display.BLACK)
    
    # Title
    display.fill_rect(0, 0, 135, 22, display.YELLOW)
    display.draw_text(15, 7, "INTERACTIVE", display.BLACK, display.YELLOW)
    
    button_a = Pin(37, Pin.IN, Pin.PULL_UP)
    
    display.draw_text(5, 30, "PRESS BUTTON A", display.WHITE)
    display.draw_text(5, 45, "TO CONTINUE!", display.WHITE)
    
    # Live counter
    for count in range(100):
        # Clear status area
        display.fill_rect(5, 70, 125, 80, display.BLACK)
        
        # Counter
        display.draw_text(5, 70, f"COUNT: {count:03d}", display.CYAN)
        
        # Button status
        if button_a.value() == 0:  # Pressed (active low)
            display.fill_rect(5, 90, 125, 15, display.RED)
            display.draw_text(5, 95, "BUTTON: ON", display.WHITE, display.RED)
        else:
            display.fill_rect(5, 90, 125, 15, display.GREEN)
            display.draw_text(5, 95, "BUTTON: OFF", display.WHITE, display.GREEN)
        
        # Progress bar
        progress = count
        display.draw_text(5, 115, "PROGRESS:", display.WHITE)
        display.fill_rect(5, 130, 100, 10, 0x2104)  # Dark background
        display.fill_rect(5, 130, progress, 10, display.BLUE)
        display.draw_text(110, 130, f"{progress}%", display.WHITE)
        
        display.show()
        time.sleep_ms(100)
        
        # Exit if button pressed
        if button_a.value() == 0:
            break
    
    # Final screen
    display.fill_rect(0, 160, 135, 80, display.PURPLE)
    display.draw_text(20, 175, "ALL DEMOS", display.WHITE, display.PURPLE)
    display.draw_text(25, 190, "COMPLETE!", display.WHITE, display.PURPLE)
    display.draw_text(15, 210, "PRESS A TO", display.WHITE, display.PURPLE)
    display.draw_text(20, 225, "RESTART", display.WHITE, display.PURPLE)
    display.show()

def main():
    """Main demo loop"""
    print("Starting M5StickC PLUS Graphics Demo!")
    
    # Initialize display
    display = M5StickCDisplay()
    
    # Initialize button
    button_a = Pin(37, Pin.IN, Pin.PULL_UP)
    button_pressed = False
    
    # Demo functions
    demos = [
        demo_hello_world,
        demo_colors,
        demo_shapes,
        demo_animation,
        demo_interactive
    ]
    
    demo_names = [
        "Hello World",
        "Colors",
        "Shapes", 
        "Animation",
        "Interactive"
    ]
    
    current_demo = 0
    
    print(f"Starting with: {demo_names[current_demo]}")
    demos[current_demo](display)
    
    while True:
        try:
            # Check button press
            if button_a.value() == 0 and not button_pressed:  # Active low
                button_pressed = True
                current_demo = (current_demo + 1) % len(demos)
                
                print(f"Demo {current_demo + 1}/{len(demos)}: {demo_names[current_demo]}")
                demos[current_demo](display)
                
            elif button_a.value() == 1 and button_pressed:
                button_pressed = False
            
            time.sleep_ms(50)
            
            # Periodic memory cleanup
            if time.ticks_ms() % 10000 < 50:
                gc.collect()
                
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()