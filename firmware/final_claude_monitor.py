# Final Claude Monitor for M5StickC PLUS with corrected display
import gc
import time
from machine import Pin, SPI, I2C

print("M5StickC PLUS - Claude Monitor v2.0")

class M5StickCDisplay:
    def __init__(self):
        print("Initializing M5StickC PLUS Display...")
        
        # Setup AXP192 power management
        self.i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
        self.i2c.writeto_mem(0x34, 0x12, bytes([0xFF]))  # Enable LDOs
        self.i2c.writeto_mem(0x34, 0x96, bytes([0x84]))  # GPIO2 output
        self.i2c.writeto_mem(0x34, 0x95, bytes([0x02]))  # Backlight on
        time.sleep_ms(200)
        
        # Setup SPI
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
        self.MAGENTA = 0xF81F
        self.CYAN = 0x07FF
        
        self._init_display()
        print("Display initialized successfully")
    
    def _cmd(self, c):
        self.cs.value(0)
        self.dc.value(0)
        self.spi.write(bytearray([c]))
        self.cs.value(1)
        time.sleep_ms(1)
    
    def _data(self, d):
        self.cs.value(0)
        self.dc.value(1)
        self.spi.write(bytearray([d]))
        self.cs.value(1)
        time.sleep_ms(1)
    
    def _init_display(self):
        # Reset sequence
        self.reset.value(0)
        time.sleep_ms(50)
        self.reset.value(1)
        time.sleep_ms(200)
        
        # ST7789 initialization
        self._cmd(0x01); time.sleep_ms(150)  # Software reset
        self._cmd(0x11); time.sleep_ms(120)  # Sleep out
        self._cmd(0x36); self._data(0x70)    # Rotation for M5StickC PLUS
        self._cmd(0x3A); self._data(0x05)    # RGB565
        self._cmd(0x21)                      # Display inversion
        self._cmd(0x13)                      # Normal display mode
        self._cmd(0x29); time.sleep_ms(50)   # Display on
    
    def fill_screen(self, color):
        # Use coordinates that almost filled screen (with small optimization)
        self._cmd(0x2A)  # Column set
        self._data(0x00); self._data(0x00)   # Start: 0
        self._data(0x00); self._data(0xFE)   # End: 254 (try slightly wider)
        
        self._cmd(0x2B)  # Row set
        self._data(0x00); self._data(0x00)   # Start: 0  
        self._data(0x01); self._data(0x3F)   # End: 319
        
        self._cmd(0x2C)  # Memory write
        
        # Fill screen
        self.cs.value(0)
        self.dc.value(1)
        color_bytes = bytearray([color >> 8, color & 0xFF])
        
        # Fill more pixels to ensure full coverage
        for _ in range(255 * 320):
            self.spi.write(color_bytes)
        
        self.cs.value(1)
    
    def draw_rect(self, x, y, w, h, color):
        # Draw rectangle (simplified for demo)
        if x + w > 240: w = 240 - x
        if y + h > 320: h = 320 - y
        
        self._cmd(0x2A)
        self._data(x >> 8); self._data(x & 0xFF)
        self._data((x + w - 1) >> 8); self._data((x + w - 1) & 0xFF)
        
        self._cmd(0x2B)
        self._data(y >> 8); self._data(y & 0xFF)
        self._data((y + h - 1) >> 8); self._data((y + h - 1) & 0xFF)
        
        self._cmd(0x2C)
        
        self.cs.value(0)
        self.dc.value(1)
        color_bytes = bytearray([color >> 8, color & 0xFF])
        
        for _ in range(w * h):
            self.spi.write(color_bytes)
        
        self.cs.value(1)
    
    def show_startup(self):
        print("DISPLAY: Showing startup screen")
        self.fill_screen(self.BLACK)
        
        # "CLAUDE" title
        self.draw_rect(20, 40, 200, 30, self.GREEN)
        
        # "MONITOR" subtitle  
        self.draw_rect(20, 80, 200, 30, self.BLUE)
        
        # Status bar
        self.draw_rect(0, 280, 240, 40, self.CYAN)
    
    def show_ready(self, ip):
        print(f"DISPLAY: Ready - {ip}")
        self.fill_screen(self.BLACK)
        
        # Large "READY" indicator
        self.draw_rect(40, 100, 160, 60, self.GREEN)
        
        # IP address area
        self.draw_rect(20, 200, 200, 25, self.WHITE)
    
    def show_error(self, msg):
        print(f"DISPLAY: Error - {msg}")
        self.fill_screen(self.BLACK)
        
        # Error indicator
        self.draw_rect(30, 100, 180, 60, self.RED)
        
        # Error message area
        self.draw_rect(20, 200, 200, 40, self.YELLOW)
    
    def update(self, session_data):
        status = session_data.get('status', 'idle')
        duration = session_data.get('duration', 0)
        cost = session_data.get('cost', 0.0)
        alert_pending = session_data.get('alert_pending', False)
        
        print(f"DISPLAY: {status} | {duration}s | ${cost:.2f}")
        
        # Clear screen
        self.fill_screen(self.BLACK)
        
        # Status bar at top
        if status == 'active':
            self.draw_rect(0, 0, 240, 30, self.GREEN)
        elif status == 'idle':
            self.draw_rect(0, 0, 240, 30, self.BLUE)
        else:
            self.draw_rect(0, 0, 240, 30, self.RED)
        
        # Duration bar (visual time representation)
        if duration > 0:
            bar_width = min(duration * 4, 220)  # 4 pixels per second, max 220
            self.draw_rect(10, 50, bar_width, 20, self.CYAN)
        
        # Cost indicator
        if cost > 0:
            cost_width = min(int(cost * 400), 220)  # Scale cost to pixels
            self.draw_rect(10, 80, cost_width, 20, self.YELLOW)
        
        # Alert indicator
        if alert_pending:
            # Blinking effect
            self.draw_rect(10, 150, 220, 40, self.RED)
        
        # Bottom status bar
        self.draw_rect(0, 290, 240, 30, self.WHITE)

# Sensors class
class Sensors:
    def __init__(self):
        try:
            self.button_a = Pin(37, Pin.IN)
            self.button_b = Pin(39, Pin.IN)
            print("Buttons initialized")
        except:
            print("Button initialization failed")
    
    def read_buttons(self):
        try:
            return self.button_a.value() == 0, self.button_b.value() == 0
        except:
            return False, False

def run_claude_monitor():
    print("Starting Claude Monitor Demo...")
    
    display = M5StickCDisplay()
    sensors = Sensors()
    
    # Startup sequence
    display.show_startup()
    time.sleep(4)
    
    display.show_ready("Ready!")
    time.sleep(3)
    
    # Demo monitoring
    session_data = {
        'status': 'idle',
        'duration': 0,
        'cost': 0.0,
        'alert_pending': False
    }
    
    print("Claude Monitor running (press buttons to interact)...")
    
    for i in range(20):
        if i > 3:
            session_data['status'] = 'active'
            session_data['duration'] = i - 3
            session_data['cost'] = (i - 3) * 0.02
            
            if (i - 3) % 7 == 0:
                session_data['alert_pending'] = True
            else:
                session_data['alert_pending'] = False
        
        display.update(session_data)
        
        # Check buttons
        a, b = sensors.read_buttons()
        if a or b:
            print(f"Button pressed: A={a}, B={b}")
            session_data['alert_pending'] = False
        
        time.sleep(2)
    
    display.show_ready("Demo Complete!")
    print("Claude Monitor demo finished")

if __name__ == "__main__":
    run_claude_monitor()