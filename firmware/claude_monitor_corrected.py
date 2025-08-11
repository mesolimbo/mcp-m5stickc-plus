# Claude Monitor for M5StickC PLUS with Corrected Display & Coordinates
import gc
import time
from machine import Pin, SPI, I2C

print("M5StickC PLUS - Claude Monitor v2.1 (Corrected)")

class M5StickCDisplay:
    def __init__(self):
        print("Initializing M5StickC PLUS Display...")
        
        # Setup AXP192 power management (CRITICAL for display)
        self.i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
        self.i2c.writeto_mem(0x34, 0x12, bytes([0xFF]))  # Enable LDOs
        self.i2c.writeto_mem(0x34, 0x96, bytes([0x84]))  # GPIO2 output
        self.i2c.writeto_mem(0x34, 0x95, bytes([0x02]))  # Backlight on
        time.sleep_ms(200)
        
        # Setup SPI for ST7789V2 display
        self.spi = SPI(1, baudrate=8000000, sck=Pin(13), mosi=Pin(15))
        self.reset = Pin(18, Pin.OUT, value=1)
        self.cs = Pin(5, Pin.OUT, value=1)
        self.dc = Pin(23, Pin.OUT, value=0)
        
        # M5StickC PLUS ST7789V2 hardware offsets (CRITICAL)
        self.x_offset = 52
        self.y_offset = 40
        self.width = 135    # Logical display width
        self.height = 240   # Logical display height
        
        # Colors (RGB565)
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
        
        # ST7789V2 initialization with correct rotation
        self._cmd(0x01); time.sleep_ms(150)  # Software reset
        self._cmd(0x11); time.sleep_ms(120)  # Sleep out
        self._cmd(0x36); self._data(0x00)    # Correct landscape rotation
        self._cmd(0x3A); self._data(0x05)    # RGB565 pixel format
        self._cmd(0x21)                      # Display inversion on
        self._cmd(0x13)                      # Normal display mode
        self._cmd(0x29); time.sleep_ms(50)   # Display on
    
    def _set_window(self, x, y, w, h):
        """Set display window with M5StickC PLUS hardware offsets"""
        # Apply hardware offsets to logical coordinates
        x_start = x + self.x_offset
        x_end = x + w - 1 + self.x_offset
        y_start = y + self.y_offset
        y_end = y + h - 1 + self.y_offset
        
        self._cmd(0x2A)  # Column Address Set
        self._data(x_start >> 8); self._data(x_start & 0xFF)
        self._data(x_end >> 8); self._data(x_end & 0xFF)
        
        self._cmd(0x2B)  # Row Address Set
        self._data(y_start >> 8); self._data(y_start & 0xFF)
        self._data(y_end >> 8); self._data(y_end & 0xFF)
        
        self._cmd(0x2C)  # Memory Write
    
    def fill_screen(self, color):
        """Fill entire screen using correct coordinate system"""
        self._set_window(0, 0, self.width, self.height)
        
        self.cs.value(0)
        self.dc.value(1)
        color_bytes = bytearray([color >> 8, color & 0xFF])
        
        # Fill entire logical display area
        for _ in range(self.width * self.height):
            self.spi.write(color_bytes)
        
        self.cs.value(1)
    
    def draw_rect(self, x, y, w, h, color):
        """Draw rectangle using correct coordinate system"""
        # Bounds checking with correct dimensions
        if x >= self.width or y >= self.height:
            return
        if x + w > self.width:
            w = self.width - x
        if y + h > self.height:
            h = self.height - y
        
        self._set_window(x, y, w, h)
        
        self.cs.value(0)
        self.dc.value(1)
        color_bytes = bytearray([color >> 8, color & 0xFF])
        
        for _ in range(w * h):
            self.spi.write(color_bytes)
        
        self.cs.value(1)
    
    def show_startup(self):
        print("DISPLAY: Showing startup screen")
        self.fill_screen(self.BLACK)
        
        # "CLAUDE" title bar (green)
        self.draw_rect(10, 30, 115, 25, self.GREEN)
        
        # "MONITOR" subtitle (blue)  
        self.draw_rect(10, 60, 115, 25, self.BLUE)
        
        # Version info (white)
        self.draw_rect(10, 95, 115, 15, self.WHITE)
        
        # Status bar at bottom (cyan)
        self.draw_rect(0, 220, 135, 20, self.CYAN)
        
        print("Startup screen displayed")
    
    def show_ready(self, message="Ready"):
        print(f"DISPLAY: Ready - {message}")
        self.fill_screen(self.BLACK)
        
        # Large "READY" indicator (green)
        self.draw_rect(20, 80, 95, 40, self.GREEN)
        
        # Message area (white)
        self.draw_rect(10, 130, 115, 20, self.WHITE)
        
        # Status border
        self.draw_rect(5, 75, 125, 50, self.CYAN)
    
    def show_error(self, msg="Error"):
        print(f"DISPLAY: Error - {msg}")
        self.fill_screen(self.BLACK)
        
        # Error indicator (red)
        self.draw_rect(20, 80, 95, 40, self.RED)
        
        # Error message area (yellow)
        self.draw_rect(10, 130, 115, 20, self.YELLOW)
    
    def update_session(self, session_data):
        """Update display with session information"""
        status = session_data.get('status', 'idle')
        duration = session_data.get('duration', 0)
        cost = session_data.get('cost', 0.0)
        alert_pending = session_data.get('alert_pending', False)
        
        print(f"SESSION: {status} | {duration}s | ${cost:.2f} | Alert: {alert_pending}")
        
        # Clear screen
        self.fill_screen(self.BLACK)
        
        # Status bar at top
        if status == 'active':
            self.draw_rect(0, 0, 135, 20, self.GREEN)
        elif status == 'idle':
            self.draw_rect(0, 0, 135, 20, self.BLUE)
        else:
            self.draw_rect(0, 0, 135, 20, self.RED)
        
        # Duration indicator (horizontal bar)
        if duration > 0:
            # Scale duration to fit display width
            bar_width = min(duration * 3, 125)  # 3 pixels per second, max 125
            self.draw_rect(5, 30, bar_width, 15, self.CYAN)
        
        # Cost indicator
        if cost > 0:
            # Scale cost to display width  
            cost_width = min(int(cost * 500), 125)  # Scale to pixels
            self.draw_rect(5, 50, cost_width, 15, self.YELLOW)
        
        # Alert indicator (flashing red if alert pending)
        if alert_pending:
            self.draw_rect(5, 100, 125, 30, self.RED)
            # Flash effect
            time.sleep_ms(200)
            self.draw_rect(5, 100, 125, 30, self.BLACK)
            time.sleep_ms(200)
            self.draw_rect(5, 100, 125, 30, self.RED)
        
        # Clock/timer area
        self.draw_rect(5, 150, 125, 20, self.WHITE)
        
        # Bottom status
        self.draw_rect(0, 220, 135, 20, self.MAGENTA)

# Button handling
class Sensors:
    def __init__(self):
        try:
            self.button_a = Pin(37, Pin.IN)  # Large button
            self.button_b = Pin(39, Pin.IN)  # Small button
            print("Buttons initialized")
        except Exception as e:
            print(f"Button initialization failed: {e}")
            self.button_a = None
            self.button_b = None
    
    def read_buttons(self):
        """Read button states (active low)"""
        try:
            if self.button_a and self.button_b:
                return (self.button_a.value() == 0, self.button_b.value() == 0)
            return (False, False)
        except:
            return (False, False)

def run_claude_monitor_demo():
    """Run Claude Monitor demonstration"""
    print("Starting Claude Monitor v2.1...")
    
    try:
        display = M5StickCDisplay()
        sensors = Sensors()
        
        # Startup sequence
        print("Running startup sequence...")
        display.show_startup()
        time.sleep(3)
        
        display.show_ready("System Ready")
        time.sleep(2)
        
        # Demo session monitoring
        session_data = {
            'status': 'idle',
            'duration': 0,
            'cost': 0.0,
            'alert_pending': False
        }
        
        print("Demo loop starting...")
        print("Press buttons to interact!")
        
        for i in range(30):  # 30 iterations = ~1 minute demo
            # Simulate session progression
            if i > 2:
                session_data['status'] = 'active'
                session_data['duration'] = i - 2
                session_data['cost'] = (i - 2) * 0.015  # $0.015 per second simulation
                
                # Trigger alert every 10 seconds
                if (i - 2) % 10 == 0 and i > 12:
                    session_data['alert_pending'] = True
                    print("ALERT: Command approval needed!")
            
            # Update display
            display.update_session(session_data)
            
            # Check for button presses
            button_a, button_b = sensors.read_buttons()
            if button_a:
                print("Button A pressed - Alert acknowledged")
                session_data['alert_pending'] = False
            if button_b:
                print("Button B pressed - Manual refresh")
            
            # Memory management
            if i % 10 == 0:
                gc.collect()
            
            time.sleep(2)  # Update every 2 seconds
        
        # Demo completion
        display.show_ready("Demo Complete!")
        print("Claude Monitor demo finished successfully!")
        
    except Exception as e:
        print(f"Error in Claude Monitor: {e}")
        try:
            display.show_error(f"Error: {e}")
        except:
            print("Failed to show error on display")

if __name__ == "__main__":
    run_claude_monitor_demo()