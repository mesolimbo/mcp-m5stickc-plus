# Claude Monitor - Framebuffer Version (Maximum Performance)
import time
import gc
from machine import Pin, SPI, I2C, PWM

print("Claude Monitor Framebuffer v1.0")

class FramebufferDisplay:
    def __init__(self):
        # AXP192 setup
        self.i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
        self.i2c.writeto_mem(0x34, 0x12, bytes([0xFF]))
        self.i2c.writeto_mem(0x34, 0x96, bytes([0x84]))
        self.i2c.writeto_mem(0x34, 0x95, bytes([0x02]))
        time.sleep_ms(200)
        
        # High-speed SPI setup (compatible with M5StickC PLUS)
        self.spi = SPI(1, baudrate=26000000, sck=Pin(13), mosi=Pin(15))
        self.reset = Pin(18, Pin.OUT, value=1)
        self.cs = Pin(5, Pin.OUT, value=1)
        self.dc = Pin(23, Pin.OUT, value=0)
        
        # Display dimensions
        self.width = 135
        self.height = 240
        
        # Colors (RGB565 format)
        self.WHITE = 0xFFFF
        self.BLACK = 0x0000
        self.GREEN = 0x07E0
        self.RED = 0xF800
        self.BLUE = 0x001F
        self.YELLOW = 0xFFE0
        self.CYAN = 0x07FF
        self.MAGENTA = 0xF81F
        
        # Create framebuffer (135 x 240 pixels, 2 bytes per pixel)
        self.framebuffer = bytearray(self.width * self.height * 2)
        
        # 5x7 Font definition
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
            '!': [0b01110, 0b10001, 0b10101, 0b10001, 0b10001, 0b10001, 0b01110],  # Clock icon
        }
        
        self._init_display()
        
        # Initialize buzzer for alerts (M5StickC PLUS buzzer on GPIO2)
        try:
            self.buzzer = PWM(Pin(2), freq=800, duty=0)  # Start silent
            self.buzzer_enabled = True
            print("Buzzer initialized")
        except:
            self.buzzer = None
            self.buzzer_enabled = False
            print("Buzzer not available")
        
        # Display timeout management
        self.display_timeout = 60  # 60 seconds
        self.last_activity = time.time()
        self.display_on = True
        
        print("Framebuffer display initialized")
    
    def _cmd(self, c):
        """Send command"""
        self.cs.value(0)
        self.dc.value(0)
        self.spi.write(bytearray([c]))
        self.cs.value(1)
    
    def _data(self, d):
        """Send data"""
        self.cs.value(0)
        self.dc.value(1)
        if isinstance(d, int):
            self.spi.write(bytearray([d]))
        else:
            self.spi.write(d)
        self.cs.value(1)
    
    def _init_display(self):
        """Initialize display"""
        self.reset.value(0)
        time.sleep_ms(10)
        self.reset.value(1)
        time.sleep_ms(100)
        
        self._cmd(0x01)  # SWRESET
        time.sleep_ms(120)
        self._cmd(0x11)  # SLPOUT
        time.sleep_ms(120)
        self._cmd(0x36)
        self._data(0x00)  # Memory access control
        self._cmd(0x3A)
        self._data(0x05)  # RGB565
        self._cmd(0x21)   # Invert display
        self._cmd(0x13)   # Normal display mode
        self._cmd(0x29)   # Display on
        time.sleep_ms(20)
    
    def clear_framebuffer(self, color=None):
        """Clear framebuffer to specific color"""
        if color is None:
            color = self.BLACK
        
        # Fill framebuffer with color
        color_high = (color >> 8) & 0xFF
        color_low = color & 0xFF
        
        for i in range(0, len(self.framebuffer), 2):
            self.framebuffer[i] = color_high
            self.framebuffer[i + 1] = color_low
    
    def set_pixel(self, x, y, color):
        """Set pixel in framebuffer"""
        if 0 <= x < self.width and 0 <= y < self.height:
            idx = (y * self.width + x) * 2
            self.framebuffer[idx] = (color >> 8) & 0xFF
            self.framebuffer[idx + 1] = color & 0xFF
    
    def draw_char_to_framebuffer(self, x, y, char, color, bg_color=None):
        """Draw character directly to framebuffer"""
        if char not in self.FONT_5X7:
            char = ' '
        
        bitmap = self.FONT_5X7[char]
        
        for row in range(7):
            for col in range(5):
                pixel_x = x + col
                pixel_y = y + row
                
                if (bitmap[row] >> (4-col)) & 1:
                    # Foreground pixel
                    self.set_pixel(pixel_x, pixel_y, color)
                elif bg_color is not None:
                    # Background pixel
                    self.set_pixel(pixel_x, pixel_y, bg_color)
    
    def draw_text_to_framebuffer(self, x, y, text, color, bg_color=None):
        """Draw text string to framebuffer"""
        char_x = x
        for char in text.upper():
            self.draw_char_to_framebuffer(char_x, y, char, color, bg_color)
            char_x += 6
    
    def fill_rect_to_framebuffer(self, x, y, w, h, color):
        """Fill rectangle in framebuffer"""
        for py in range(y, min(y + h, self.height)):
            for px in range(x, min(x + w, self.width)):
                self.set_pixel(px, py, color)
    
    def display_framebuffer(self):
        """Transfer entire framebuffer to display in one operation"""
        # Set full screen window with M5StickC PLUS offsets
        self._cmd(0x2A)  # Column address set
        self._data((52) >> 8)  # X start high
        self._data((52) & 0xFF)  # X start low
        self._data((52 + self.width - 1) >> 8)  # X end high
        self._data((52 + self.width - 1) & 0xFF)  # X end low
        
        self._cmd(0x2B)  # Row address set
        self._data((40) >> 8)  # Y start high
        self._data((40) & 0xFF)  # Y start low
        self._data((40 + self.height - 1) >> 8)  # Y end high
        self._data((40 + self.height - 1) & 0xFF)  # Y end low
        
        self._cmd(0x2C)  # Memory write
        
        # Transfer entire framebuffer in one SPI transaction
        self.cs.value(0)
        self.dc.value(1)
        self.spi.write(self.framebuffer)
        self.cs.value(1)
    
    def render_status_screen(self, session_seconds, status, alerts, current_time):
        """Render stylish status screen to framebuffer"""
        # Clear framebuffer
        self.clear_framebuffer(self.BLACK)
        
        # Blue header bar
        self.fill_rect_to_framebuffer(0, 0, self.width, 20, self.BLUE)
        self.draw_text_to_framebuffer(15, 5, "CLAUDE PRO SESSION", self.WHITE, self.BLUE)
        
        # Real-time clock with background
        hours = current_time[3]
        minutes = current_time[4]
        clock_str = f"{hours:02d}:{minutes:02d}"
        self.fill_rect_to_framebuffer(25, 25, 85, 15, 0x2104)  # Dark blue
        self.draw_text_to_framebuffer(40, 30, clock_str, self.CYAN, 0x2104)
        
        # Session time with subtle background
        session_hours = session_seconds // 3600
        session_mins = (session_seconds % 3600) // 60
        session_secs = session_seconds % 60
        time_str = f"SESSION: {session_hours:02d}H{session_mins:02d}M{session_secs:02d}S"
        self.fill_rect_to_framebuffer(2, 48, 131, 12, 0x1082)  # Very dark blue
        self.draw_text_to_framebuffer(5, 50, time_str, self.WHITE, 0x1082)
        
        # Status with background
        status_color = self.GREEN if status == "active" else self.WHITE
        status_bg = 0x0320 if status == "active" else 0x4208  # Green or gray
        status_text = "STATUS: CODING" if status == "active" else "STATUS: IDLE"
        self.fill_rect_to_framebuffer(2, 68, 131, 12, status_bg)
        self.draw_text_to_framebuffer(5, 70, status_text, self.WHITE, status_bg)
        
        # Session statistics with clean layout
        commands_run = (session_seconds // 30) + 1  # Simulate commands
        files_edited = (session_seconds // 45) + 1  # Simulate file edits
        
        self.draw_text_to_framebuffer(5, 90, f"COMMANDS: {commands_run:03d}", self.YELLOW, self.BLACK)
        self.draw_text_to_framebuffer(5, 110, f"FILES: {files_edited:02d}", self.MAGENTA, self.BLACK)
        
        # Productivity with progress bar
        productivity = min(100, (session_seconds // 2) + 20)  # Steady increase
        self.draw_text_to_framebuffer(5, 130, "PRODUCTIVITY:", self.WHITE, self.BLACK)
        
        # Progress bar
        bar_width = int(productivity * 1.15)  # Scale to fit
        self.fill_rect_to_framebuffer(5, 142, 115, 6, 0x2104)  # Background
        bar_color = self.GREEN if productivity > 75 else self.YELLOW
        self.fill_rect_to_framebuffer(5, 142, bar_width, 6, bar_color)
        self.draw_text_to_framebuffer(122, 140, f"{productivity}%", self.WHITE, self.BLACK)
        
        # Alerts with styled background
        if alerts > 0:
            self.fill_rect_to_framebuffer(2, 155, 131, 12, 0x6000)  # Dark red
            alert_str = f"ALERTS: {alerts}"
            self.draw_text_to_framebuffer(5, 157, alert_str, self.WHITE, 0x6000)
        else:
            self.fill_rect_to_framebuffer(2, 155, 131, 12, 0x0320)  # Dark green
            self.draw_text_to_framebuffer(5, 157, "ALERTS: NONE", self.WHITE, 0x0320)
        
        # Model and performance info
        self.draw_text_to_framebuffer(5, 175, "MODEL: SONNET-4", self.CYAN, self.BLACK)
        self.draw_text_to_framebuffer(5, 190, "FRAMEBUFFER MODE", self.GREEN, self.BLACK)
        
        # Gray footer bar
        self.fill_rect_to_framebuffer(0, 205, self.width, 35, 0x4208)  # Gray
        
        # Live token count in footer
        tokens_used = session_seconds * 15  # Simulate token usage
        self.draw_text_to_framebuffer(5, 212, f"TOKENS: {tokens_used:,}", self.WHITE, 0x4208)
        
        # Footer info (no button instructions needed)
        self.draw_text_to_framebuffer(5, 227, "PRESS A: WAKE DISPLAY", self.CYAN, 0x4208)
    
    def beep_alert(self, frequency=800, duration_ms=200):
        """Play alert beep"""
        if self.buzzer and self.buzzer_enabled:
            try:
                self.buzzer.freq(frequency)
                self.buzzer.duty(256)  # 25% duty cycle for quieter sound
                time.sleep_ms(duration_ms)
                self.buzzer.duty(0)  # Turn off
                print(f"Alert beep: {frequency}Hz for {duration_ms}ms")
            except:
                print("Beep failed")
    
    def beep_pattern(self, pattern="alert"):
        """Play specific beep patterns"""
        if not self.buzzer or not self.buzzer_enabled:
            return
        
        if pattern == "alert":
            # Single quiet beep for new alert (work-friendly)
            self.beep_alert(800, 100)
        elif pattern == "acknowledge":
            # Single low beep for acknowledge
            self.beep_alert(600, 100)
        elif pattern == "startup":
            # Rising tone for startup
            self.beep_alert(600, 100)
            time.sleep_ms(50)
            self.beep_alert(800, 100)
            time.sleep_ms(50)
            self.beep_alert(1000, 100)
    
    def turn_off_display(self):
        """Turn off display to save power"""
        if self.display_on:
            self._cmd(0x28)  # Display off
            # Turn off backlight via AXP192
            self.i2c.writeto_mem(0x34, 0x95, bytes([0x00]))  # Backlight off
            self.display_on = False
            print("Display turned off")
    
    def turn_on_display(self):
        """Turn on display and reset activity timer"""
        if not self.display_on:
            self._cmd(0x29)  # Display on
            # Turn on backlight via AXP192
            self.i2c.writeto_mem(0x34, 0x95, bytes([0x02]))  # Backlight on
            self.display_on = True
            print("Display turned on")
        
        # ALWAYS reset activity timer (whether display was on or off)
        self.last_activity = time.time()
        print(f"Activity timer reset - display will timeout at {self.last_activity + self.display_timeout}")
    
    def check_display_timeout(self):
        """Check if display should timeout"""
        if self.display_on and (time.time() - self.last_activity) > self.display_timeout:
            self.turn_off_display()
            return True
        return False


def run_framebuffer_monitor():
    """Run framebuffer-based Claude Monitor with real-time updates"""
    print("Starting Claude Pro Session Monitor...")
    
    # Initialize display
    display = FramebufferDisplay()
    
    # Initialize buttons with pull-up resistors (M5StickC PLUS buttons are active LOW)
    button_a = Pin(37, Pin.IN, Pin.PULL_UP)
    button_b = Pin(39, Pin.IN, Pin.PULL_UP)
    
    # Show startup screen with audio
    display.clear_framebuffer(display.BLACK)
    display.fill_rect_to_framebuffer(10, 40, 115, 15, display.BLUE)
    display.draw_text_to_framebuffer(15, 50, "CLAUDE PRO", display.WHITE)
    display.draw_text_to_framebuffer(20, 70, "SESSION MONITOR", display.GREEN)
    display.draw_text_to_framebuffer(35, 90, "FRAMEBUFFER", display.CYAN)
    display.draw_text_to_framebuffer(45, 110, "V2.0", display.YELLOW)
    display.draw_text_to_framebuffer(15, 140, "INITIALIZING...", display.WHITE)
    display.display_framebuffer()
    
    # Play startup beep
    display.beep_pattern("startup")
    
    print("Pro Session Monitor starting...")
    time.sleep(2)
    
    # Demo session with real-time updates
    session_start = time.time()
    alerts_pending = 0
    last_alert_time = 0  # Track when we last beeped
    last_second = -1
    
    print("Starting real-time session monitoring...")
    
    while True:
        current_timestamp = time.time()
        session_seconds = int(current_timestamp - session_start)
        
        # Get current time for clock display
        current_time = time.localtime()
        
        # Debug: Check button state every few seconds
        if session_seconds % 5 == 0 and session_seconds != last_second:
            button_state = button_a.value()
            time_until_sleep = display.display_timeout - (current_timestamp - display.last_activity)
            print(f"Debug: Button A={button_state}, Display on={display.display_on}, Sleep in {time_until_sleep:.1f}s")
        
        # Check display timeout
        display.check_display_timeout()
        
        # Update display every second for smooth clock (only if display is on)
        if session_seconds != last_second:
            # Simulate alerts occasionally (but only beep once per alert)
            if session_seconds > 0 and session_seconds % 30 == 0:
                if alerts_pending == 0:  # Only add if none pending
                    alerts_pending += 1
                    last_alert_time = session_seconds
                    print(f"New alert at {session_seconds} seconds")
                    # Play alert beep only once per alert
                    display.beep_pattern("alert")
            
            # Determine status
            status = "active" if session_seconds > 5 else "idle"
            
            # Only render if display is on
            if display.display_on:
                render_start = time.ticks_ms()
                
                display.render_status_screen(session_seconds, status, alerts_pending, current_time)
                display.display_framebuffer()
                
                render_end = time.ticks_ms()
                render_time = time.ticks_diff(render_end, render_start)
                
                # Print performance stats periodically
                if session_seconds % 15 == 0 and session_seconds > 0:
                    print(f"Frame: {render_time}ms | Session: {session_seconds}s | Alerts: {alerts_pending}")
            
            last_second = session_seconds
        
        # Handle button A: Only wake display and reset timeout
        button_pressed = button_a.value() == 0  # Active LOW
        if button_pressed:
            # Wake display and reset 60-second timeout
            display.turn_on_display()
            print(f"*** BUTTON A PRESSED at {session_seconds}s - timeout reset ***")
            
            # Force immediate refresh to show current state
            if display.display_on:
                display.render_status_screen(session_seconds, status, alerts_pending, current_time)
                display.display_framebuffer()
            
            time.sleep(0.3)  # Debounce
        
        # Debug: Show button state and timer info every 10 seconds
        if session_seconds % 10 == 0 and session_seconds != last_second and session_seconds > 0:
            time_left = display.display_timeout - (current_timestamp - display.last_activity)
            print(f"Debug {session_seconds}s: Button={button_a.value()}, Display on={display.display_on}, Sleep in {time_left:.1f}s")
        
        # Button B does nothing now (as requested)
        
        # Memory management
        if session_seconds % 60 == 0 and session_seconds > 0:
            gc.collect()
            print("Memory cleanup")
        
        # Fast loop for responsive updates
        time.sleep(0.1)


if __name__ == "__main__":
    run_framebuffer_monitor()