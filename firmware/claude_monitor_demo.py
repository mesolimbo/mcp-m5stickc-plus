# Claude Monitor Demo - WiFi Detection and Setup
import time
import network
from machine import Pin, SPI, I2C, reset

print("Claude Monitor Demo v1.0")

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
        self.MAGENTA = 0xF81F
        
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
    
    def show_claude_monitor_startup(self):
        """Show Claude Monitor branded startup"""
        self.clear_screen()
        
        # "CLAUDE" title in green
        self.fill_area(10, 30, 115, 25, self.GREEN)
        
        # "MONITOR" subtitle in blue
        self.fill_area(10, 60, 115, 25, self.BLUE)
        
        # Version bar in white
        self.fill_area(10, 90, 115, 15, self.WHITE)
        
        # Status "Initializing..." in cyan
        self.fill_area(10, 120, 115, 20, self.CYAN)
        
        # Progress bar animation
        for i in range(5):
            width = 20 + i * 20
            self.fill_area(10, 160, width, 15, self.YELLOW)
            time.sleep(0.5)
        
        print("CLAUDE MONITOR startup displayed")
    
    def show_wifi_scan(self, networks_found):
        """Show WiFi scanning results"""
        self.clear_screen()
        
        # Title
        self.fill_area(5, 10, 125, 20, self.CYAN)  # "WiFi Scan"
        
        # Network count indicator
        for i in range(min(networks_found, 8)):
            self.fill_area(5 + i * 15, 40, 10, 10, self.GREEN)
        
        # Scanning animation
        self.fill_area(5, 70, 125, 20, self.YELLOW)
        
        print(f"WiFi networks found: {networks_found}")
    
    def show_demo_session(self, demo_step):
        """Show demo Claude session data"""
        self.clear_screen()
        
        # Status bar
        if demo_step > 2:
            self.fill_area(0, 0, 135, 15, self.GREEN)  # Active
        else:
            self.fill_area(0, 0, 135, 15, self.BLUE)   # Starting
        
        # Session duration (growing bar)
        if demo_step > 0:
            duration_width = min(demo_step * 15, 125)
            self.fill_area(5, 25, duration_width, 20, self.CYAN)
        
        # Cost indicator
        if demo_step > 1:
            cost = demo_step * 0.02
            cost_width = min(int(cost * 500), 125)
            self.fill_area(5, 55, cost_width, 15, self.YELLOW)
        
        # Alert simulation (every 5 steps)
        if demo_step % 5 == 0 and demo_step > 5:
            self.fill_area(5, 80, 125, 30, self.RED)
            print("DEMO ALERT: Command approval needed!")
        
        # Session stats
        sessions = demo_step // 3
        for i in range(min(sessions, 8)):
            self.fill_area(5 + i * 15, 130, 10, 10, self.GREEN)
        
        # Commands run
        commands = demo_step * 2
        if commands > 0:
            cmd_height = min(commands, 40)
            self.fill_area(5, 180 - cmd_height, 15, cmd_height, self.MAGENTA)
        
        # Bottom info bar
        self.fill_area(0, 220, 135, 20, self.WHITE)
        
        print(f"Demo session step {demo_step}: Duration bar, cost ${demo_step * 0.02:.2f}")

def run_claude_monitor_demo():
    """Run Claude Monitor demo without WiFi requirements"""
    print("Starting Claude Monitor Demo...")
    
    # Initialize display
    display = M5StickDisplay()
    
    # Buttons
    button_a = Pin(37, Pin.IN)  # Large button
    button_b = Pin(39, Pin.IN)  # Small button
    
    # Show branded startup
    print("Phase 1: Startup")
    display.show_claude_monitor_startup()
    time.sleep(3)
    
    # WiFi scanning demo
    print("Phase 2: WiFi Scan")
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    try:
        networks = wlan.scan()
        display.show_wifi_scan(len(networks))
        print(f"Found {len(networks)} WiFi networks:")
        for i, net in enumerate(networks[:5]):  # Show first 5
            ssid = net[0].decode('utf-8') if net[0] else "Hidden"
            print(f"  {i+1}. {ssid} (Signal: {net[3]} dBm)")
    except:
        display.show_wifi_scan(0)
        print("WiFi scan failed")
    
    time.sleep(4)
    
    # Demo Claude session monitoring
    print("Phase 3: Claude Session Demo")
    print("This simulates what you'll see during actual Claude Code sessions...")
    
    demo_step = 0
    last_update = time.time()
    
    while demo_step < 30:  # 30-step demo
        current_time = time.time()
        
        # Update every 2 seconds or on button press
        if (current_time - last_update > 2) or button_a.value() == 0 or button_b.value() == 0:
            
            # Show demo session data
            display.show_demo_session(demo_step)
            
            # Button feedback
            if button_a.value() == 0:
                print("Button A: Alert acknowledged (in real system)")
                time.sleep(0.3)
            if button_b.value() == 0:
                print("Button B: Manual refresh (in real system)")
                time.sleep(0.3)
            
            demo_step += 1
            last_update = current_time
        
        time.sleep(0.1)
    
    # Demo complete
    print("Demo complete!")
    display.clear_screen()
    display.fill_area(20, 100, 95, 40, self.GREEN)  # "DEMO COMPLETE"
    
    print("\nThis was a simulation of Claude Monitor functionality.")
    print("To see real session data:")
    print("1. Configure WiFi credentials in firmware")
    print("2. Start MCP server on your PC") 
    print("3. Use Claude Code - the M5StickC will track real sessions!")

if __name__ == "__main__":
    run_claude_monitor_demo()