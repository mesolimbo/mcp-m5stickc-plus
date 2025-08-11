# Working display manager for M5StickC PLUS Claude Monitor
import time
from machine import Pin, SPI

class WorkingDisplay:
    def __init__(self, brightness=80):
        self.width = 135
        self.height = 240
        
        # Colors (RGB565)
        self.BLACK = 0x0000
        self.WHITE = 0xFFFF
        self.GREEN = 0x07E0
        self.PALE_GREEN = 0x87E0
        self.RED = 0xF800
        self.YELLOW = 0xFFE0
        self.BLUE = 0x001F
        self.GRAY = 0x8410
        
        # Initialize hardware
        self.init_display()
        
        print("WorkingDisplay initialized")
    
    def init_display(self):
        """Initialize the M5StickC PLUS display"""
        # Initialize SPI and pins
        self.spi = SPI(1, baudrate=10000000, sck=Pin(13), mosi=Pin(15))
        self.reset = Pin(18, Pin.OUT)
        self.cs = Pin(5, Pin.OUT)
        self.dc = Pin(23, Pin.OUT)
        self.backlight = Pin(12, Pin.OUT)
        
        # Turn on backlight
        self.backlight.value(1)
        
        # Reset display
        self.reset.value(0)
        time.sleep_ms(10)
        self.reset.value(1)
        time.sleep_ms(120)
        
        # Initialize ST7789
        self._cmd(0x11)  # Sleep out
        time.sleep_ms(120)
        
        self._cmd(0x3A)  # Color mode
        self._data(0x05)  # 16-bit RGB565
        
        self._cmd(0x36)  # Memory access control
        self._data(0xA0)  # Rotation for M5StickC PLUS
        
        self._cmd(0x21)  # Inversion on
        self._cmd(0x13)  # Normal display mode
        self._cmd(0x29)  # Display on
        
        # Clear to black
        self.fill(self.BLACK)
    
    def _cmd(self, cmd):
        """Send command to display"""
        self.cs.value(0)
        self.dc.value(0)  # Command mode
        self.spi.write(bytearray([cmd]))
        self.cs.value(1)
    
    def _data(self, data):
        """Send data to display"""
        self.cs.value(0)
        self.dc.value(1)  # Data mode
        if isinstance(data, int):
            self.spi.write(bytearray([data]))
        else:
            self.spi.write(data)
        self.cs.value(1)
    
    def set_window(self, x0, y0, x1, y1):
        """Set drawing window"""
        self._cmd(0x2A)  # Column set
        self._data(x0 >> 8)
        self._data(x0 & 0xFF)
        self._data(x1 >> 8)
        self._data(x1 & 0xFF)
        
        self._cmd(0x2B)  # Row set
        self._data(y0 >> 8)
        self._data(y0 & 0xFF)
        self._data(y1 >> 8)
        self._data(y1 & 0xFF)
        
        self._cmd(0x2C)  # Memory write
    
    def fill(self, color):
        """Fill entire screen with color"""
        self.set_window(0, 0, self.width - 1, self.height - 1)
        
        color_bytes = bytearray([color >> 8, color & 0xFF])
        self.cs.value(0)
        self.dc.value(1)
        
        for _ in range(self.width * self.height):
            self.spi.write(color_bytes)
        
        self.cs.value(1)
    
    def fill_rect(self, x, y, w, h, color):
        """Fill rectangle with color"""
        if x >= self.width or y >= self.height:
            return
        if x + w > self.width:
            w = self.width - x
        if y + h > self.height:
            h = self.height - y
        
        self.set_window(x, y, x + w - 1, y + h - 1)
        
        color_bytes = bytearray([color >> 8, color & 0xFF])
        self.cs.value(0)
        self.dc.value(1)
        
        for _ in range(w * h):
            self.spi.write(color_bytes)
        
        self.cs.value(1)
    
    def hline(self, x, y, w, color):
        """Draw horizontal line"""
        self.fill_rect(x, y, w, 1, color)
    
    def vline(self, x, y, h, color):
        """Draw vertical line"""
        self.fill_rect(x, y, 1, h, color)
    
    def show_startup(self):
        """Show startup screen"""
        print("DISPLAY: Startup screen")
        self.fill(self.BLACK)
        
        # Draw "CLAUDE" text area
        self.fill_rect(10, 40, 115, 30, self.PALE_GREEN)
        
        # Draw "MONITOR" text area  
        self.fill_rect(10, 80, 115, 30, self.PALE_GREEN)
        
        # Draw status bar
        self.fill_rect(0, 200, self.width, 20, self.GRAY)
        
    def show_ready(self, ip="Ready"):
        """Show ready screen"""
        print(f"DISPLAY: Ready - {ip}")
        self.fill(self.BLACK)
        
        # Green "READY" indicator
        self.fill_rect(30, 50, 75, 40, self.GREEN)
        
        # IP address area (simplified)
        self.fill_rect(10, 120, 115, 20, self.PALE_GREEN)
        
    def show_error(self, message):
        """Show error screen"""
        print(f"DISPLAY: Error - {message}")
        self.fill(self.BLACK)
        
        # Red error indicator
        self.fill_rect(20, 60, 95, 40, self.RED)
        
        # Error message area
        self.fill_rect(10, 120, 115, 30, self.RED)
    
    def update(self, session_data):
        """Update main display with session data"""
        status = session_data.get('status', 'idle')
        duration = session_data.get('duration', 0)
        cost = session_data.get('cost', 0.0)
        alert_pending = session_data.get('alert_pending', False)
        alerts_enabled = session_data.get('alerts_enabled', True)
        
        print(f"DISPLAY: {status} | {duration}s | ${cost:.2f} | Alert: {alert_pending}")
        
        self.fill(self.BLACK)
        
        # Status indicator at top
        if status == 'active':
            self.fill_rect(0, 0, self.width, 25, self.GREEN)
        elif status == 'idle':
            self.fill_rect(0, 0, self.width, 25, self.GRAY)
        elif status == 'server_offline':
            self.fill_rect(0, 0, self.width, 25, self.RED)
        else:
            self.fill_rect(0, 0, self.width, 25, self.YELLOW)
        
        # Session time display (simplified bars)
        minutes = duration // 60
        bar_width = min(minutes * 2, 115)  # 2 pixels per minute, max 115
        if bar_width > 0:
            self.fill_rect(10, 40, bar_width, 15, self.PALE_GREEN)
        
        # Cost display (simplified)
        cost_level = min(int(cost * 20), 115)  # Scale cost to pixels
        if cost_level > 0:
            self.fill_rect(10, 70, cost_level, 15, self.WHITE)
        
        # Alert indicator
        if alert_pending:
            # Blink effect
            if int(time.time() * 2) % 2:
                self.fill_rect(10, 150, 115, 30, self.YELLOW)
        
        # Audio status indicator
        if not alerts_enabled:
            self.fill_rect(100, 190, 25, 15, self.GRAY)
        
        # Activity indicator at bottom
        self.fill_rect(0, self.height - 5, self.width, 5, self.PALE_GREEN)
    
    def show_message(self, message, duration=2):
        """Show temporary message"""
        print(f"DISPLAY: Message - {message}")
        self.fill(self.BLACK)
        
        # Message area
        self.fill_rect(10, 100, 115, 40, self.YELLOW)
        
        time.sleep(duration)
    
    def brightness(self, level):
        """Set brightness (simplified - just on/off)"""
        self.backlight.value(1 if level > 0 else 0)
