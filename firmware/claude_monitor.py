# Claude Monitor Final - Readable Text Display
import time
import gc
from machine import Pin, SPI, I2C

print("Claude Monitor Final v1.0")

class ClaudeMonitorDisplay:
    def __init__(self):
        # AXP192 setup (required for display power)
        self.i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
        self.i2c.writeto_mem(0x34, 0x12, bytes([0xFF]))  # Enable LDOs
        self.i2c.writeto_mem(0x34, 0x96, bytes([0x84]))  # GPIO2 output
        self.i2c.writeto_mem(0x34, 0x95, bytes([0x02]))  # Backlight on
        time.sleep_ms(200)
        
        # SPI setup
        self.spi = SPI(1, baudrate=8000000, sck=Pin(13), mosi=Pin(15))
        self.reset = Pin(18, Pin.OUT, value=1)
        self.cs = Pin(5, Pin.OUT, value=1)
        self.dc = Pin(23, Pin.OUT, value=0)
        
        # Colors
        self.WHITE = 0xFFFF
        self.BLACK = 0x0000
        self.GREEN = 0x07E0
        self.RED = 0xF800
        self.BLUE = 0x001F
        
        # Font definition (complete A-Z, 0-9, symbols)
        self.FONT_5X7 = {
            'A': [0b01110, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001],
            'B': [0b11110, 0b10001, 0b10001, 0b11110, 0b10001, 0b10001, 0b11110],
            'C': [0b01111, 0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b01111],
            'D': [0b11110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b11110],
            'E': [0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b11111],
            'F': [0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b10000],
            'G': [0b01111, 0b10000, 0b10000, 0b10011, 0b10001, 0b10001, 0b01111],
            'H': [0b10001, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001],
            'I': [0b01110, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110],
            'J': [0b00111, 0b00001, 0b00001, 0b00001, 0b00001, 0b10001, 0b01110],
            'K': [0b10001, 0b10010, 0b10100, 0b11000, 0b10100, 0b10010, 0b10001],
            'L': [0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b11111],
            'M': [0b10001, 0b11011, 0b10101, 0b10101, 0b10001, 0b10001, 0b10001],
            'N': [0b10001, 0b11001, 0b10101, 0b10101, 0b10011, 0b10001, 0b10001],
            'O': [0b01110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110],
            'P': [0b11110, 0b10001, 0b10001, 0b11110, 0b10000, 0b10000, 0b10000],
            'Q': [0b01110, 0b10001, 0b10001, 0b10001, 0b10101, 0b10010, 0b01101],
            'R': [0b11110, 0b10001, 0b10001, 0b11110, 0b10100, 0b10010, 0b10001],
            'S': [0b01111, 0b10000, 0b10000, 0b01110, 0b00001, 0b00001, 0b11110],
            'T': [0b11111, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100],
            'U': [0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110],
            'V': [0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01010, 0b00100],
            'W': [0b10001, 0b10001, 0b10001, 0b10101, 0b10101, 0b11011, 0b10001],
            'X': [0b10001, 0b10001, 0b01010, 0b00100, 0b01010, 0b10001, 0b10001],
            'Y': [0b10001, 0b10001, 0b01010, 0b00100, 0b00100, 0b00100, 0b00100],
            'Z': [0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b11111],
            '0': [0b01110, 0b10001, 0b10011, 0b10101, 0b11001, 0b10001, 0b01110],
            '1': [0b00100, 0b01100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110],
            '2': [0b01110, 0b10001, 0b00001, 0b00110, 0b01000, 0b10000, 0b11111],
            '3': [0b11111, 0b00001, 0b00010, 0b00110, 0b00001, 0b10001, 0b01110],
            '4': [0b00010, 0b00110, 0b01010, 0b10010, 0b11111, 0b00010, 0b00010],
            '5': [0b11111, 0b10000, 0b11110, 0b00001, 0b00001, 0b10001, 0b01110],
            '6': [0b00110, 0b01000, 0b10000, 0b11110, 0b10001, 0b10001, 0b01110],
            '7': [0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b10000],
            '8': [0b01110, 0b10001, 0b10001, 0b01110, 0b10001, 0b10001, 0b01110],
            '9': [0b01110, 0b10001, 0b10001, 0b01111, 0b00001, 0b00010, 0b01100],
            ':': [0b00000, 0b01100, 0b01100, 0b00000, 0b01100, 0b01100, 0b00000],
            '$': [0b00100, 0b01111, 0b10100, 0b01110, 0b00101, 0b11110, 0b00100],
            ' ': [0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000],
            '.': [0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b11000, 0b11000],
            '-': [0b00000, 0b00000, 0b00000, 0b11111, 0b00000, 0b00000, 0b00000],
            'M': [0b10001, 0b11011, 0b10101, 0b10001, 0b10001, 0b10001, 0b10001],
            'H': [0b10001, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001],
            '/': [0b00000, 0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b00000],
        }
        
        self._init_display()
        print("Claude Monitor Display initialized")
    
    def _cmd(self, c):
        self.cs.value(0); self.dc.value(0)
        self.spi.write(bytearray([c]))
        self.cs.value(1); time.sleep_ms(1)
    
    def _data(self, d):
        self.cs.value(0); self.dc.value(1)
        self.spi.write(bytearray([d]))
        self.cs.value(1); time.sleep_ms(1)
    
    def _init_display(self):
        self.reset.value(0); time.sleep_ms(50)
        self.reset.value(1); time.sleep_ms(200)
        
        # ST7789 init with correct rotation
        self._cmd(0x01); time.sleep_ms(150)
        self._cmd(0x11); time.sleep_ms(120)
        self._cmd(0x36); self._data(0x00)  # Correct landscape rotation
        self._cmd(0x3A); self._data(0x05)
        self._cmd(0x21)
        self._cmd(0x13)
        self._cmd(0x29); time.sleep_ms(50)
    
    def _set_window(self, x, y, w, h):
        """Set display window with M5StickC PLUS hardware offsets"""
        x_start = x + 52
        y_start = y + 40
        x_end = x + w - 1 + 52
        y_end = y + h - 1 + 40
        
        self._cmd(0x2A)
        self._data(x_start >> 8); self._data(x_start & 0xFF)
        self._data(x_end >> 8); self._data(x_end & 0xFF)
        
        self._cmd(0x2B)
        self._data(y_start >> 8); self._data(y_start & 0xFF)
        self._data(y_end >> 8); self._data(y_end & 0xFF)
        
        self._cmd(0x2C)
    
    def fill_area(self, x, y, w, h, color):
        """Fill rectangular area"""
        self._set_window(x, y, w, h)
        
        self.cs.value(0); self.dc.value(1)
        color_bytes = bytearray([color >> 8, color & 0xFF])
        for _ in range(w * h):
            self.spi.write(color_bytes)
        self.cs.value(1)
    
    def draw_pixel(self, x, y, color):
        """Draw single pixel"""
        self.fill_area(x, y, 1, 1, color)
    
    def draw_char(self, x, y, char, color):
        """Draw single character"""
        if char not in self.FONT_5X7:
            char = ' '
        
        bitmap = self.FONT_5X7[char]
        for row in range(7):
            for col in range(5):
                if (bitmap[row] >> (4-col)) & 1:
                    self.draw_pixel(x + col, y + row, color)
    
    def draw_text(self, x, y, text, color):
        """Draw text string"""
        char_x = x
        for char in text.upper():
            self.draw_char(char_x, y, char, color)
            char_x += 6
    
    def clear_screen(self):
        """Clear entire screen"""
        self.fill_area(0, 0, 135, 240, self.BLACK)
    
    def show_startup(self):
        """Show Claude Monitor startup screen"""
        self.clear_screen()
        self.draw_text(25, 50, "CLAUDE", self.WHITE)
        self.draw_text(20, 70, "MONITOR", self.WHITE)
        self.draw_text(30, 100, "V1.0", self.WHITE)
        self.draw_text(10, 130, "INITIALIZING", self.WHITE)
    
    def show_session_data(self, session_time_mins, cost, status, alerts):
        """Show current session data"""
        self.clear_screen()
        
        # Title
        self.draw_text(30, 5, "CLAUDE", self.WHITE)
        
        # Status
        if status == "active":
            self.draw_text(5, 25, "STATUS: ACTIVE", self.WHITE)
        else:
            self.draw_text(5, 25, "STATUS: IDLE", self.WHITE)
        
        # Session time
        hours = session_time_mins // 60
        mins = session_time_mins % 60
        time_str = f"TIME: {hours}H {mins:02d}M"
        self.draw_text(5, 45, time_str, self.WHITE)
        
        # Cost
        cost_str = f"COST: ${cost:.2f}"
        self.draw_text(5, 65, cost_str, self.WHITE)
        
        # Alerts
        if alerts > 0:
            alert_str = f"ALERTS: {alerts}"
            self.draw_text(5, 85, alert_str, self.WHITE)
            # Flash indicator
            self.fill_area(120, 85, 10, 7, self.RED)
        
        # Model info
        self.draw_text(5, 105, "MODEL: SONNET", self.WHITE)
        
        # Controls
        self.draw_text(5, 130, "A: ACK ALERT", self.WHITE)
        self.draw_text(5, 150, "B: REFRESH", self.WHITE)
        
        # Footer
        self.draw_text(5, 210, f"UPTIME: {session_time_mins}M", self.WHITE)

def run_claude_monitor():
    """Run Claude Monitor demonstration"""
    print("Starting Claude Monitor...")
    
    # Initialize display
    display = ClaudeMonitorDisplay()
    
    # Initialize buttons
    button_a = Pin(37, Pin.IN)  # Large button - acknowledge alerts
    button_b = Pin(39, Pin.IN)  # Small button - refresh/manual update
    
    # Show startup
    display.show_startup()
    print("Showing startup screen...")
    time.sleep(3)
    
    # Demo session data
    session_start = time.time()
    alerts_pending = 0
    refresh_counter = 0
    
    print("Starting session simulation...")
    
    while True:
        # Calculate session time
        session_seconds = int(time.time() - session_start)
        session_minutes = session_seconds // 60
        
        # Simulate cost accumulation (based on your actual $2.91 for 9h 37m)
        # Your rate: $2.91 / 577 minutes = ~$0.005 per minute
        estimated_cost = session_minutes * 0.005
        
        # Simulate alerts (every 5 minutes)
        if session_minutes > 0 and session_minutes % 5 == 0 and refresh_counter == 0:
            alerts_pending += 1
            print(f"New alert at {session_minutes} minutes")
        
        # Update display
        status = "active" if session_minutes > 0 else "idle"
        display.show_session_data(session_minutes, estimated_cost, status, alerts_pending)
        
        # Check buttons
        if button_a.value() == 0:  # Button A pressed
            if alerts_pending > 0:
                alerts_pending = 0
                print("Alert acknowledged")
            time.sleep(0.3)  # Debounce
        
        if button_b.value() == 0:  # Button B pressed
            print("Manual refresh")
            refresh_counter = (refresh_counter + 1) % 5
            time.sleep(0.3)  # Debounce
        
        # Memory management
        if session_seconds % 30 == 0:
            gc.collect()
        
        time.sleep(2)  # Update every 2 seconds

if __name__ == "__main__":
    run_claude_monitor()