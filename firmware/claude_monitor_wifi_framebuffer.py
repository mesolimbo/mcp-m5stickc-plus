# Claude Monitor WiFi + Framebuffer - Best of Both Worlds
import time
import gc
import json
import network
import urequests
from machine import Pin, SPI, I2C, PWM, reset

print("Claude Monitor WiFi + Framebuffer v1.0")

# Configuration
WIFI_SSID = "ssid"
WIFI_PASSWORD = "password"
SERVER_URL = "http://127.0.0.1:8080"  # MCP server on PC

class FramebufferWiFiDisplay:
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
        }
        
        self._init_display()
        
        # Initialize buzzer for alerts
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
        
        print("Framebuffer WiFi display initialized")
    
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
    
    def render_session_screen(self, session_data, current_time):
        """Render session screen from real server data"""
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
        
        # Session time from server data
        duration = session_data.get('duration', 0)
        session_hours = duration // 3600
        session_mins = (duration % 3600) // 60
        session_secs = duration % 60
        time_str = f"SESSION: {session_hours:02d}H{session_mins:02d}M{session_secs:02d}S"
        self.fill_rect_to_framebuffer(2, 48, 131, 12, 0x1082)  # Very dark blue
        self.draw_text_to_framebuffer(5, 50, time_str, self.WHITE, 0x1082)
        
        # Status from server
        status = session_data.get('status', 'idle')
        status_color = self.GREEN if status == "active" else self.WHITE
        status_bg = 0x0320 if status == "active" else 0x4208  # Green or gray
        status_text = "STATUS: CODING" if status == "active" else "STATUS: IDLE"
        self.fill_rect_to_framebuffer(2, 68, 131, 12, status_bg)
        self.draw_text_to_framebuffer(5, 70, status_text, self.WHITE, status_bg)
        
        # Real session statistics from server
        commands_run = session_data.get('commands', 0)
        files_edited = session_data.get('files_edited', 0)
        
        self.draw_text_to_framebuffer(5, 90, f"COMMANDS: {commands_run:03d}", self.YELLOW, self.BLACK)
        self.draw_text_to_framebuffer(5, 110, f"FILES: {files_edited:02d}", self.MAGENTA, self.BLACK)
        
        # Productivity calculation from real data
        productivity = min(100, duration // 6 + 20 if duration > 0 else 0)  # Grows with session time
        self.draw_text_to_framebuffer(5, 130, "PRODUCTIVITY:", self.WHITE, self.BLACK)
        
        # Progress bar
        bar_width = int(productivity * 1.15)  # Scale to fit
        self.fill_rect_to_framebuffer(5, 142, 115, 6, 0x2104)  # Background
        bar_color = self.GREEN if productivity > 75 else self.YELLOW
        self.fill_rect_to_framebuffer(5, 142, bar_width, 6, bar_color)
        self.draw_text_to_framebuffer(122, 140, f"{productivity}%", self.WHITE, self.BLACK)
        
        # Alerts from server
        alerts = session_data.get('alerts', 0)
        if alerts > 0:
            self.fill_rect_to_framebuffer(2, 155, 131, 12, 0x6000)  # Dark red
            alert_str = f"ALERTS: {alerts}"
            self.draw_text_to_framebuffer(5, 157, alert_str, self.WHITE, 0x6000)
        else:
            self.fill_rect_to_framebuffer(2, 155, 131, 12, 0x0320)  # Dark green
            self.draw_text_to_framebuffer(5, 157, "ALERTS: NONE", self.WHITE, 0x0320)
        
        # Connection status and model info
        self.draw_text_to_framebuffer(5, 175, "MODEL: SONNET-4", self.CYAN, self.BLACK)
        self.draw_text_to_framebuffer(5, 190, "WIFI: CONNECTED", self.GREEN, self.BLACK)
        
        # Gray footer bar
        self.fill_rect_to_framebuffer(0, 205, self.width, 35, 0x4208)  # Gray
        
        # Live session info in footer
        session_active = session_data.get('active', False)
        footer_text = "REAL SESSION DATA" if session_active else "NO SESSION"
        self.draw_text_to_framebuffer(5, 212, footer_text, self.WHITE, 0x4208)
        
        # Footer controls
        self.draw_text_to_framebuffer(5, 227, "PRESS A: WAKE DISPLAY", self.CYAN, 0x4208)
    
    def show_wifi_connecting(self):
        """Show WiFi connecting screen"""
        self.clear_framebuffer(self.BLACK)
        self.fill_rect_to_framebuffer(0, 0, self.width, 20, self.YELLOW)
        self.draw_text_to_framebuffer(25, 5, "CONNECTING...", self.BLACK, self.YELLOW)
        self.draw_text_to_framebuffer(15, 50, "WIFI: SSID", self.WHITE, self.BLACK)
        self.draw_text_to_framebuffer(15, 70, "PLEASE WAIT...", self.CYAN, self.BLACK)
        self.display_framebuffer()
    
    def show_wifi_connected(self, ip):
        """Show WiFi connected screen"""
        self.clear_framebuffer(self.BLACK)
        self.fill_rect_to_framebuffer(0, 0, self.width, 20, self.GREEN)
        self.draw_text_to_framebuffer(25, 5, "WIFI CONNECTED", self.WHITE, self.GREEN)
        self.draw_text_to_framebuffer(5, 50, f"IP: {ip}", self.WHITE, self.BLACK)
        self.draw_text_to_framebuffer(5, 70, "CONNECTING TO SERVER", self.CYAN, self.BLACK)
        self.display_framebuffer()
    
    def show_wifi_failed(self):
        """Show WiFi connection failed"""
        self.clear_framebuffer(self.BLACK)
        self.fill_rect_to_framebuffer(0, 0, self.width, 20, self.RED)
        self.draw_text_to_framebuffer(25, 5, "WIFI FAILED", self.WHITE, self.RED)
        self.draw_text_to_framebuffer(15, 50, "CHECK NETWORK", self.WHITE, self.BLACK)
        self.draw_text_to_framebuffer(15, 70, "RESTARTING...", self.YELLOW, self.BLACK)
        self.display_framebuffer()
    
    def beep_alert(self, frequency=800, duration_ms=100):
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


class WiFiManager:
    def __init__(self):
        self.wlan = network.WLAN(network.STA_IF)
        self.connected = False
        self.ip = None
    
    def connect(self, ssid, password, timeout=15):
        """Connect to WiFi network"""
        print(f"Connecting to WiFi: {ssid}")
        
        self.wlan.active(True)
        self.wlan.connect(ssid, password)
        
        # Wait for connection
        start_time = time.time()
        while not self.wlan.isconnected() and (time.time() - start_time) < timeout:
            time.sleep(1)
            print(".", end="")
        
        if self.wlan.isconnected():
            self.connected = True
            self.ip = self.wlan.ifconfig()[0]
            print(f"\nWiFi connected! IP: {self.ip}")
            return True
        else:
            print(f"\nWiFi connection failed after {timeout} seconds")
            return False
    
    def is_connected(self):
        """Check if still connected to WiFi"""
        return self.wlan.isconnected()


class SessionClient:
    def __init__(self, server_url):
        self.server_url = server_url
        self.last_data = None
    
    def get_status(self):
        """Get session status from MCP server"""
        try:
            response = urequests.get(f"{self.server_url}/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.last_data = data
                response.close()
                return data
            else:
                print(f"Server error: {response.status_code}")
                response.close()
                return None
        except Exception as e:
            print(f"HTTP error: {e}")
            return None
    
    def acknowledge_alert(self):
        """Send alert acknowledgment to server"""
        try:
            response = urequests.post(f"{self.server_url}/acknowledge", timeout=5)
            success = response.status_code == 200
            response.close()
            return success
        except Exception as e:
            print(f"Acknowledge failed: {e}")
            return False


def run_claude_monitor():
    """Main Claude Monitor WiFi + Framebuffer application"""
    print("Starting Claude Monitor WiFi + Framebuffer...")
    
    # Initialize components
    display = FramebufferWiFiDisplay()
    wifi = WiFiManager()
    session_client = SessionClient(SERVER_URL)
    
    # Buttons with pull-up resistors (M5StickC PLUS buttons are active LOW)
    button_a = Pin(37, Pin.IN, Pin.PULL_UP)
    button_b = Pin(39, Pin.IN, Pin.PULL_UP)
    
    # Show WiFi connecting
    display.show_wifi_connecting()
    time.sleep(2)
    
    # Connect to WiFi
    if not wifi.connect(WIFI_SSID, WIFI_PASSWORD):
        display.show_wifi_failed()
        time.sleep(5)
        reset()
    
    # Show WiFi connected
    display.show_wifi_connected(wifi.ip)
    time.sleep(2)
    
    # Main loop
    last_update = 0
    last_alert_count = 0
    last_second = -1
    
    print("Starting real-time WiFi session monitoring...")
    
    while True:
        try:
            current_timestamp = time.time()
            current_time = time.localtime()
            
            # Check display timeout
            display.check_display_timeout()
            
            # Update every 5 seconds or on button press
            button_a_pressed = button_a.value() == 0  # Active LOW
            button_b_pressed = button_b.value() == 0  # Active LOW
            
            if (current_timestamp - last_update > 5) or button_b_pressed:
                print("Fetching session data...")
                
                # Check WiFi connection
                if not wifi.is_connected():
                    display.show_wifi_failed()
                    time.sleep(2)
                    if wifi.connect(WIFI_SSID, WIFI_PASSWORD):
                        display.show_wifi_connected(wifi.ip)
                    else:
                        continue
                
                # Get session data from server
                session_data = session_client.get_status()
                if session_data:
                    print(f"Session data: {session_data}")
                    
                    # Check for new alerts
                    current_alerts = session_data.get('alerts', 0)
                    if current_alerts > last_alert_count:
                        display.beep_alert()
                        print(f"New alert! Count: {current_alerts}")
                    last_alert_count = current_alerts
                    
                    # Only render if display is on
                    if display.display_on:
                        display.render_session_screen(session_data, current_time)
                        display.display_framebuffer()
                else:
                    print("Failed to get session data")
                
                last_update = current_timestamp
            
            # Handle button A: Only wake display and reset timeout
            if button_a_pressed:
                # Wake display and reset 60-second timeout
                display.turn_on_display()
                print(f"*** BUTTON A PRESSED - timeout reset ***")
                
                # Force immediate refresh to show current state
                if display.display_on and session_client.last_data:
                    display.render_session_screen(session_client.last_data, current_time)
                    display.display_framebuffer()
                
                time.sleep(0.3)  # Debounce
            
            # Memory management
            if int(current_timestamp) % 60 == 0 and int(current_timestamp) != last_second:
                gc.collect()
                print("Memory cleanup")
                last_second = int(current_timestamp)
            
            # Fast loop for responsive updates
            time.sleep(0.2)
            
        except Exception as e:
            print(f"Main loop error: {e}")
            time.sleep(1)


if __name__ == "__main__":
    run_claude_monitor()