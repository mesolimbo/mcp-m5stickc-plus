# Claude Monitor - High Performance Version
import time
import gc
from machine import Pin, SPI, I2C

print("Claude Monitor Optimized v1.0")

class OptimizedClaudeDisplay:
    def __init__(self):
        # AXP192 setup (required for display power)
        self.i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
        self.i2c.writeto_mem(0x34, 0x12, bytes([0xFF]))  # Enable LDOs
        self.i2c.writeto_mem(0x34, 0x96, bytes([0x84]))  # GPIO2 output
        self.i2c.writeto_mem(0x34, 0x95, bytes([0x02]))  # Backlight on
        time.sleep_ms(200)
        
        # High-speed SPI setup
        self.spi = SPI(1, baudrate=40000000, sck=Pin(13), mosi=Pin(15))
        self.reset = Pin(18, Pin.OUT, value=1)
        self.cs = Pin(5, Pin.OUT, value=1)
        self.dc = Pin(23, Pin.OUT, value=0)
        
        # Colors
        self.WHITE = 0xFFFF
        self.BLACK = 0x0000
        self.GREEN = 0x07E0
        self.RED = 0xF800
        self.BLUE = 0x001F
        
        # 5x7 Font bitmap
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
            '/': [0b00000, 0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b00000],
        }
        
        self._init_display()
        print("Optimized display initialized")
    
    def _cmd(self, c):
        """Send command - no delays"""
        self.cs.value(0)
        self.dc.value(0)
        self.spi.write(bytearray([c]))
        self.cs.value(1)
    
    def _data(self, d):
        """Send data - no delays"""
        self.cs.value(0)
        self.dc.value(1)
        if isinstance(d, int):
            self.spi.write(bytearray([d]))
        else:
            self.spi.write(d)
        self.cs.value(1)
    
    def _init_display(self):
        """Initialize display with minimal delays"""
        self.reset.value(0)
        time.sleep_ms(10)
        self.reset.value(1)
        time.sleep_ms(100)
        
        # ST7789 init sequence
        self._cmd(0x01)  # SWRESET
        time.sleep_ms(120)
        self._cmd(0x11)  # SLPOUT
        time.sleep_ms(120)
        self._cmd(0x36)
        self._data(0x00)  # Correct landscape rotation
        self._cmd(0x3A)
        self._data(0x05)  # RGB565
        self._cmd(0x21)   # Invert on
        self._cmd(0x13)   # Normal display
        self._cmd(0x29)   # Display on
        time.sleep_ms(20)
    
    def _set_window(self, x, y, w, h):
        """Set display window with M5StickC PLUS offsets"""
        x_start = x + 52
        y_start = y + 40
        x_end = x + w - 1 + 52
        y_end = y + h - 1 + 40
        
        self._cmd(0x2A)
        self._data(x_start >> 8)
        self._data(x_start & 0xFF)
        self._data(x_end >> 8)
        self._data(x_end & 0xFF)
        
        self._cmd(0x2B)
        self._data(y_start >> 8)
        self._data(y_start & 0xFF)
        self._data(y_end >> 8)
        self._data(y_end & 0xFF)
        
        self._cmd(0x2C)
    
    def fill_area_fast(self, x, y, w, h, color):
        """Fast area fill using bulk writes"""
        self._set_window(x, y, w, h)
        
        # Prepare color data in bulk
        pixel_count = w * h
        if pixel_count > 1000:
            # For large areas, use chunks
            chunk_size = 500
            color_chunk = bytearray(chunk_size * 2)
            for i in range(0, chunk_size * 2, 2):
                color_chunk[i] = color >> 8
                color_chunk[i + 1] = color & 0xFF
            
            self.cs.value(0)
            self.dc.value(1)
            
            full_chunks = pixel_count // chunk_size
            for _ in range(full_chunks):
                self.spi.write(color_chunk)
            
            remainder = pixel_count % chunk_size
            if remainder > 0:
                remainder_data = bytearray(remainder * 2)
                for i in range(0, remainder * 2, 2):
                    remainder_data[i] = color >> 8
                    remainder_data[i + 1] = color & 0xFF
                self.spi.write(remainder_data)
            
            self.cs.value(1)
        else:
            # For small areas, direct write
            color_data = bytearray(pixel_count * 2)
            for i in range(0, pixel_count * 2, 2):
                color_data[i] = color >> 8
                color_data[i + 1] = color & 0xFF
            
            self.cs.value(0)
            self.dc.value(1)
            self.spi.write(color_data)
            self.cs.value(1)
    
    def draw_char_fast(self, x, y, char, color, bg_color=None):
        """Fast character drawing using bulk pixel data"""
        if char not in self.FONT_5X7:
            char = ' '
        
        bitmap = self.FONT_5X7[char]
        
        # Create pixel data for entire character
        char_data = bytearray(5 * 7 * 2)  # 5x7 pixels, 2 bytes each
        idx = 0
        
        for row in range(7):
            for col in range(5):
                if (bitmap[row] >> (4-col)) & 1:
                    # Foreground pixel
                    char_data[idx] = color >> 8
                    char_data[idx + 1] = color & 0xFF
                else:
                    # Background pixel (if specified)
                    if bg_color is not None:
                        char_data[idx] = bg_color >> 8
                        char_data[idx + 1] = bg_color & 0xFF
                    else:
                        # Skip background pixels
                        if (bitmap[row] >> (4-col)) & 1:
                            char_data[idx] = color >> 8
                            char_data[idx + 1] = color & 0xFF
                        else:
                            # Transparent - use black
                            char_data[idx] = 0
                            char_data[idx + 1] = 0
                idx += 2
        
        # Set window and write all character data at once
        self._set_window(x, y, 5, 7)
        self.cs.value(0)
        self.dc.value(1)
        self.spi.write(char_data)
        self.cs.value(1)
    
    def draw_text_fast(self, x, y, text, color, bg_color=None):
        """Fast text drawing"""
        char_x = x
        for char in text.upper():
            self.draw_char_fast(char_x, y, char, color, bg_color)
            char_x += 6
    
    def clear_screen_fast(self):
        """Fast screen clear"""
        self.fill_area_fast(0, 0, 135, 240, self.BLACK)
    
    def partial_clear(self, x, y, w, h):
        """Clear only a specific area"""
        self.fill_area_fast(x, y, w, h, self.BLACK)
    
    def show_session_data_optimized(self, session_time_mins, cost, status, alerts):
        """Optimized session display with partial updates"""
        # Clear only text areas instead of full screen
        text_areas = [
            (30, 5, 75, 15),    # Title
            (5, 25, 125, 15),   # Status
            (5, 45, 125, 15),   # Time
            (5, 65, 125, 15),   # Cost
            (5, 85, 125, 15),   # Alerts
            (5, 105, 125, 15),  # Model
            (5, 210, 125, 15),  # Uptime
        ]
        
        for x, y, w, h in text_areas:
            self.partial_clear(x, y, w, h)
        
        # Title
        self.draw_text_fast(30, 5, "CLAUDE", self.WHITE, self.BLACK)
        
        # Status with color coding
        status_color = self.GREEN if status == "active" else self.WHITE
        status_text = "STATUS: ACTIVE" if status == "active" else "STATUS: IDLE"
        self.draw_text_fast(5, 25, status_text, status_color, self.BLACK)
        
        # Session time
        hours = session_time_mins // 60
        mins = session_time_mins % 60
        time_str = f"TIME: {hours}H {mins:02d}M"
        self.draw_text_fast(5, 45, time_str, self.WHITE, self.BLACK)
        
        # Cost
        cost_str = f"COST: ${cost:.2f}"
        self.draw_text_fast(5, 65, cost_str, self.WHITE, self.BLACK)
        
        # Alerts
        if alerts > 0:
            alert_str = f"ALERTS: {alerts}"
            self.draw_text_fast(5, 85, alert_str, self.RED, self.BLACK)
            # Fast alert indicator
            self.fill_area_fast(120, 85, 10, 7, self.RED)
        else:
            self.draw_text_fast(5, 85, "ALERTS: 0", self.WHITE, self.BLACK)
        
        # Model info
        self.draw_text_fast(5, 105, "MODEL: SONNET", self.WHITE, self.BLACK)
        
        # Controls (static - draw once)
        self.draw_text_fast(5, 130, "A: ACK ALERT", self.WHITE, self.BLACK)
        self.draw_text_fast(5, 150, "B: REFRESH", self.WHITE, self.BLACK)
        
        # Footer
        self.draw_text_fast(5, 210, f"UPTIME: {session_time_mins}M", self.WHITE, self.BLACK)


def run_optimized_monitor():
    """Run optimized Claude Monitor"""
    print("Starting Optimized Claude Monitor...")
    
    # Initialize display
    display = OptimizedClaudeDisplay()
    
    # Initialize buttons
    button_a = Pin(37, Pin.IN)
    button_b = Pin(39, Pin.IN)
    
    # Show startup with fast clear
    display.clear_screen_fast()
    display.draw_text_fast(25, 50, "CLAUDE", display.WHITE)
    display.draw_text_fast(20, 70, "MONITOR", display.WHITE)
    display.draw_text_fast(35, 90, "OPTIMIZED", display.GREEN)
    display.draw_text_fast(30, 110, "V2.0", display.WHITE)
    print("Showing optimized startup...")
    time.sleep(2)
    
    # Demo session
    session_start = time.time()
    alerts_pending = 0
    refresh_counter = 0
    last_update_time = 0
    
    print("Starting high-speed session simulation...")
    
    while True:
        current_time = time.time()
        session_seconds = int(current_time - session_start)
        session_minutes = session_seconds // 60
        
        # Only update display if time changed (reduce unnecessary redraws)
        if current_time - last_update_time >= 1.0:
            # Calculate cost
            estimated_cost = session_minutes * 0.005
            
            # Simulate alerts
            if session_minutes > 0 and session_minutes % 5 == 0 and refresh_counter == 0:
                alerts_pending += 1
                print(f"Alert at {session_minutes} minutes")
            
            # Update display efficiently
            status = "active" if session_minutes > 0 else "idle"
            display.show_session_data_optimized(session_minutes, estimated_cost, status, alerts_pending)
            
            last_update_time = current_time
        
        # Check buttons
        if button_a.value() == 0:
            if alerts_pending > 0:
                alerts_pending = 0
                print("Alert acknowledged")
            time.sleep(0.2)
        
        if button_b.value() == 0:
            print("Manual refresh")
            refresh_counter = (refresh_counter + 1) % 5
            time.sleep(0.2)
        
        # Memory cleanup
        if session_seconds % 60 == 0:
            gc.collect()
        
        time.sleep(0.1)  # Much faster update loop


if __name__ == "__main__":
    run_optimized_monitor()