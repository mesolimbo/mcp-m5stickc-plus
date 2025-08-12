# Claude Monitor WiFi - Real Session Tracking for M5StickC PLUS
import gc
import time
import json
import network
import urequests
from machine import Pin, SPI, I2C, reset

print("Claude Monitor WiFi v1.0")

# Configuration
WIFI_SSID = "ssid"
WIFI_PASSWORD = "password"
SERVER_URL = "http://127.0.0.1:8080"  # MCP server on PC

class M5StickDisplay:
    def __init__(self):
        # AXP192 power management (CRITICAL)
        self.i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
        self.i2c.writeto_mem(0x34, 0x12, bytes([0xFF]))
        self.i2c.writeto_mem(0x34, 0x96, bytes([0x84]))
        self.i2c.writeto_mem(0x34, 0x95, bytes([0x02]))
        time.sleep_ms(200)
        
        # SPI display setup
        self.spi = SPI(1, baudrate=8000000, sck=Pin(13), mosi=Pin(15))
        self.reset = Pin(18, Pin.OUT, value=1)
        self.cs = Pin(5, Pin.OUT, value=1)
        self.dc = Pin(23, Pin.OUT, value=0)
        
        # Colors
        self.BLACK = 0x0000
        self.WHITE = 0xFFFF
        self.RED = 0xF800
        self.GREEN = 0x07E0
        self.BLUE = 0x001F
        self.YELLOW = 0xFFE0
        self.CYAN = 0x07FF
        
        self._init_display()
        print("Display initialized")
    
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
    
    def fill_area(self, x, y, w, h, color):
        """Fill area using correct M5StickC PLUS coordinates"""
        # Apply hardware offsets
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
        
        self.cs.value(0); self.dc.value(1)
        color_bytes = bytearray([color >> 8, color & 0xFF])
        for _ in range(w * h):
            self.spi.write(color_bytes)
        self.cs.value(1)
    
    def clear_screen(self):
        """Clear entire screen"""
        self.fill_area(0, 0, 135, 240, self.BLACK)
    
    def show_startup(self):
        """Show Claude Monitor startup screen"""
        self.clear_screen()
        
        # Title
        self.fill_area(5, 20, 125, 20, self.GREEN)  # "CLAUDE"
        self.fill_area(5, 45, 125, 20, self.BLUE)   # "MONITOR"
        
        # WiFi connecting indicator
        self.fill_area(5, 80, 125, 15, self.YELLOW) # "Connecting..."
        
        # Version info
        self.fill_area(5, 200, 125, 15, self.WHITE) # Version
    
    def show_wifi_status(self, connected, ip=None):
        """Show WiFi connection status"""
        self.clear_screen()
        
        if connected:
            self.fill_area(5, 50, 125, 30, self.GREEN)  # Connected
            if ip:
                # Show IP as colored bars (simplified)
                ip_parts = ip.split('.')
                colors = [self.RED, self.BLUE, self.YELLOW, self.CYAN]
                for i, part in enumerate(ip_parts[:4]):
                    width = min(int(part) // 2, 60)
                    self.fill_area(5 + i * 30, 100, width, 10, colors[i])
        else:
            self.fill_area(5, 50, 125, 30, self.RED)    # Not connected
        
        # Status bar
        self.fill_area(0, 220, 135, 20, self.WHITE)
    
    def show_session_data(self, data):
        """Display Claude session statistics"""
        self.clear_screen()
        
        status = data.get('status', 'unknown')
        duration = data.get('duration', 0)
        cost = data.get('cost', 0.0)
        alert_pending = data.get('alert_pending', False)
        
        print(f"Display: {status} | {duration}s | ${cost:.3f} | Alert: {alert_pending}")
        
        # Status indicator at top
        if status == 'active':
            self.fill_area(0, 0, 135, 15, self.GREEN)
        else:
            self.fill_area(0, 0, 135, 15, self.BLUE)
        
        # Duration bar (visual time representation)
        if duration > 0:
            # Scale to fit display width (max 2 minutes = full width)
            bar_width = min(duration * 125 // 120, 125)
            self.fill_area(5, 25, bar_width, 20, self.CYAN)
            
            # Duration segments (every 30 seconds)
            for i in range(1, duration // 30 + 1):
                x = min(i * 125 // 4, 125)
                self.fill_area(x, 25, 2, 20, self.WHITE)
        
        # Cost indicator
        if cost > 0:
            # Scale cost (max $0.50 = full width)
            cost_width = min(int(cost * 250), 125)
            self.fill_area(5, 55, cost_width, 15, self.YELLOW)
        
        # Alert indicator (flashing red if pending)
        if alert_pending:
            self.fill_area(5, 80, 125, 25, self.RED)
            print("ALERT: Command approval needed!")
        else:
            self.fill_area(5, 80, 125, 25, self.BLACK)
        
        # Session stats area
        stats = data.get('stats', {})
        sessions_today = stats.get('sessions_today', 0)
        commands_run = stats.get('commands_run', 0)
        
        # Show session count as dots
        for i in range(min(sessions_today, 10)):
            self.fill_area(5 + i * 12, 120, 8, 8, self.GREEN)
        
        # Show command count as bars
        if commands_run > 0:
            cmd_height = min(commands_run * 2, 40)
            self.fill_area(5, 180 - cmd_height, 10, cmd_height, self.MAGENTA)
        
        # Bottom status
        self.fill_area(0, 220, 135, 20, self.WHITE)
    
    def show_error(self, message):
        """Show error message"""
        self.clear_screen()
        self.fill_area(5, 50, 125, 30, self.RED)
        self.fill_area(5, 90, 125, 20, self.YELLOW)
        print(f"ERROR: {message}")

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
            print(f"\nWiFi connection failed after {timeout}s")
            return False
    
    def is_connected(self):
        """Check if still connected"""
        self.connected = self.wlan.isconnected()
        return self.connected

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
            print(f"Request failed: {e}")
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
    """Main Claude Monitor application"""
    print("Starting Claude Monitor WiFi...")
    
    # Initialize components
    display = M5StickDisplay()
    wifi = WiFiManager()
    
    # Buttons
    button_a = Pin(37, Pin.IN)  # Large button - acknowledge alerts
    button_b = Pin(39, Pin.IN)  # Small button - manual refresh
    
    # Show startup
    display.show_startup()
    time.sleep(2)
    
    # Connect to WiFi
    if not wifi.connect(WIFI_SSID, WIFI_PASSWORD):
        display.show_error("WiFi Failed")
        time.sleep(5)
        reset()
    
    display.show_wifi_status(True, wifi.ip)
    time.sleep(2)
    
    # Initialize session client
    client = SessionClient(SERVER_URL)
    
    print("Claude Monitor running...")
    last_update = 0
    error_count = 0
    
    while True:
        try:
            current_time = time.time()
            
            # Update every 5 seconds or on button press
            button_a_pressed = button_a.value() == 0
            button_b_pressed = button_b.value() == 0
            
            if (current_time - last_update > 5) or button_b_pressed:
                print("Fetching session data...")
                
                # Check WiFi connection
                if not wifi.is_connected():
                    display.show_error("WiFi Lost")
                    time.sleep(2)
                    if wifi.connect(WIFI_SSID, WIFI_PASSWORD):
                        display.show_wifi_status(True, wifi.ip)
                    else:
                        continue
                
                # Get session data from server
                session_data = client.get_status()
                
                if session_data:
                    display.show_session_data(session_data)
                    error_count = 0
                    last_update = current_time
                else:
                    error_count += 1
                    if error_count > 3:
                        display.show_error("Server Error")
                
            # Handle alert acknowledgment
            if button_a_pressed:
                print("Button A: Acknowledging alert...")
                if client.acknowledge_alert():
                    print("Alert acknowledged")
                time.sleep(0.5)  # Debounce
            
            # Memory cleanup
            if current_time % 30 == 0:
                gc.collect()
            
            time.sleep(0.5)
            
        except KeyboardInterrupt:
            print("Stopping Claude Monitor")
            break
        except Exception as e:
            print(f"Main loop error: {e}")
            display.show_error(str(e))
            time.sleep(5)

if __name__ == "__main__":
    # Check configuration
    if WIFI_SSID == "YOUR_WIFI_SSID":
        print("ERROR: Please configure WIFI_SSID and WIFI_PASSWORD")
        print("Edit the firmware file and set your WiFi credentials")
        while True:
            time.sleep(1)
    
    run_claude_monitor()