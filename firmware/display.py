import time
from machine import Pin, SPI
try:
    import st7789
except ImportError:
    print("Warning: st7789 driver not found, using mock display")
    st7789 = None

class DisplayManager:
    def __init__(self, brightness=50):
        self.brightness = brightness
        self.width = 135
        self.height = 240
        
        # Initialize display if driver available
        if st7789:
            self.init_hardware()
        else:
            print("Running in display mock mode")
            self.display = None
            
        # Display state
        self.current_screen = 'startup'
        self.last_update = 0
        self.blink_state = False
        
        # Colors (RGB565)
        self.colors = {
            'black': 0x0000,
            'white': 0xFFFF,
            'pale_green': 0x87E0,  # Pale green for main text
            'green': 0x07E0,
            'red': 0xF800,
            'blue': 0x001F,
            'yellow': 0xFFE0,
            'gray': 0x8410
        }
        
    def init_hardware(self):
        """Initialize M5StickC PLUS display hardware"""
        try:
            # M5StickC PLUS display pins
            self.spi = SPI(1, baudrate=40000000, sck=Pin(13), mosi=Pin(15))
            
            self.display = st7789.ST7789(
                self.spi,
                width=self.width,
                height=self.height,
                reset=Pin(18, Pin.OUT),
                cs=Pin(5, Pin.OUT),
                dc=Pin(23, Pin.OUT),
                backlight=Pin(12, Pin.OUT),
                rotation=3  # Landscape orientation
            )
            
            # Set backlight
            self.set_brightness(self.brightness)
            
            # Clear screen
            self.clear()
            
        except Exception as e:
            print(f"Display init error: {e}")
            self.display = None
    
    def set_brightness(self, brightness):
        """Set display brightness (0-100)"""
        if self.display and hasattr(self.display, 'backlight'):
            # Convert 0-100 to PWM duty cycle
            duty = int((brightness / 100) * 1023)
            self.display.backlight.duty(duty)
    
    def clear(self, color=None):
        """Clear screen with optional color"""
        if self.display:
            fill_color = color if color is not None else self.colors['black']
            self.display.fill(fill_color)
        else:
            print(f"DISPLAY: Clear screen ({color})")
    
    def show_text(self, text, x, y, color=None, size=1):
        """Display text at position"""
        if self.display:
            text_color = color if color is not None else self.colors['pale_green']
            # Note: This assumes st7789 has text method - may need adjustment
            self.display.text(text, x, y, text_color)
        else:
            print(f"DISPLAY: Text at ({x},{y}): {text}")
    
    def show_startup(self):
        """Show startup screen"""
        self.clear()
        self.show_text("Claude Monitor", 20, 50, self.colors['pale_green'])
        self.show_text("M5StickC PLUS", 25, 80, self.colors['gray'])
        self.show_text("Initializing...", 20, 110, self.colors['yellow'])
        self.refresh()
        self.current_screen = 'startup'
    
    def show_ready(self, ip_address):
        """Show ready screen with IP"""
        self.clear()
        self.show_text("Ready!", 45, 40, self.colors['green'])
        self.show_text(f"IP: {ip_address}", 10, 80, self.colors['pale_green'])
        self.show_text("Waiting for", 25, 110, self.colors['gray'])
        self.show_text("Claude...", 35, 130, self.colors['gray'])
        self.refresh()
        self.current_screen = 'ready'
    
    def show_error(self, message):
        """Show error message"""
        self.clear()
        self.show_text("ERROR", 45, 50, self.colors['red'])
        # Split long messages
        if len(message) > 12:
            mid = len(message) // 2
            space_pos = message.find(' ', mid-3, mid+3)
            if space_pos != -1:
                line1 = message[:space_pos]
                line2 = message[space_pos+1:]
            else:
                line1 = message[:12]
                line2 = message[12:]
            self.show_text(line1, 10, 90, self.colors['red'])
            self.show_text(line2, 10, 110, self.colors['red'])
        else:
            self.show_text(message, 20, 90, self.colors['red'])
        self.refresh()
        self.current_screen = 'error'
    
    def show_message(self, message, duration=2):
        """Show temporary message"""
        self.clear()
        self.show_text(message, 20, 100, self.colors['yellow'])
        self.refresh()
        time.sleep(duration)
        # Return to previous screen
        self.current_screen = 'message'
    
    def update(self, session_data):
        """Update main display with session data"""
        current_time = time.time()
        
        # Update display every second or if data changed significantly
        if current_time - self.last_update < 1:
            return
            
        self.clear()
        
        # Show session status
        status = session_data.get('status', 'idle')
        if status == 'active':
            self.show_text("ACTIVE", 40, 10, self.colors['green'])
        elif status == 'idle':
            self.show_text("IDLE", 50, 10, self.colors['gray'])
        elif status == 'server_offline':
            self.show_text("OFFLINE", 35, 10, self.colors['red'])
        else:
            self.show_text(status.upper(), 20, 10, self.colors['yellow'])
        
        # Show session duration
        duration = session_data.get('duration', 0)
        hours = duration // 3600
        minutes = (duration % 3600) // 60
        seconds = duration % 60
        
        if hours > 0:
            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            time_str = f"{minutes:02d}:{seconds:02d}"
            
        self.show_text("Duration:", 10, 40, self.colors['pale_green'])
        self.show_text(time_str, 30, 60, self.colors['white'])
        
        # Show estimated cost
        cost = session_data.get('cost', 0.0)
        cost_str = f"${cost:.2f}"
        self.show_text("Cost:", 10, 90, self.colors['pale_green'])
        self.show_text(cost_str, 50, 110, self.colors['white'])
        
        # Show alert indicator if pending
        if session_data.get('alert_pending'):
            # Blink alert indicator
            if int(current_time * 2) % 2:  # Blink every 0.5 seconds
                alert_type = session_data.get('alert_type', 'generic')
                if alert_type == 'command_approval':
                    self.show_text("⏳ APPROVE", 15, 140, self.colors['yellow'])
                elif alert_type == 'cost_threshold':
                    self.show_text("💰 COST", 25, 140, self.colors['red'])
                else:
                    self.show_text("🔔 ALERT", 25, 140, self.colors['yellow'])
        
        # Show audio status
        if not session_data.get('alerts_enabled', True):
            self.show_text("🔇", 110, 140, self.colors['gray'])
        
        # Show project name if available
        project = session_data.get('project_name')
        if project:
            # Truncate if too long
            if len(project) > 10:
                project = project[:10] + "..."
            self.show_text(project, 10, 170, self.colors['gray'])
        
        # Show connectivity indicator
        signal = session_data.get('wifi_signal')
        if signal is not None:
            if signal > -50:
                wifi_icon = "📶"
            elif signal > -70:
                wifi_icon = "📶"
            else:
                wifi_icon = "📶"
            self.show_text(wifi_icon, 110, 10, self.colors['pale_green'])
        
        self.refresh()
        self.last_update = current_time
        self.current_screen = 'main'
    
    def refresh(self):
        """Refresh display buffer"""
        if self.display and hasattr(self.display, 'show'):
            self.display.show()
        # Mock display just prints
    
    def sleep(self):
        """Put display to sleep"""
        if self.display:
            self.set_brightness(0)
        print("DISPLAY: Sleep mode")
    
    def wake(self):
        """Wake display from sleep"""
        if self.display:
            self.set_brightness(self.brightness)
        print("DISPLAY: Wake up")
