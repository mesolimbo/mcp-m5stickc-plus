# Real display manager for M5StickC PLUS LCD
import time
from machine import Pin, SPI
from st7789_driver import ST7789

class RealDisplayManager:
    def __init__(self, brightness=50):
        self.brightness = brightness
        self.width = 135
        self.height = 240
        
        # RGB565 colors - define before init_hardware
        self.colors = {
            'black': 0x0000,
            'white': 0xFFFF,
            'pale_green': 0x87E0,  # Pale green
            'green': 0x07E0,
            'red': 0xF800,
            'blue': 0x001F,
            'yellow': 0xFFE0,
            'gray': 0x8410
        }
        
        # Display state
        self.current_screen = 'startup'
        self.last_update = 0
        
        # Initialize display
        self.init_hardware()
        
        print("RealDisplayManager initialized")
    
    def init_hardware(self):
        """Initialize M5StickC PLUS display hardware"""
        try:
            # M5StickC PLUS SPI pins
            self.spi = SPI(
                1, 
                baudrate=40000000, 
                sck=Pin(13),   # SCK
                mosi=Pin(15),  # MOSI/SDA
                polarity=0,
                phase=0
            )
            
            # Create display instance
            self.display = ST7789(
                self.spi,
                width=self.width,
                height=self.height,
                reset=Pin(18, Pin.OUT),     # RST
                cs=Pin(5, Pin.OUT),         # CS
                dc=Pin(23, Pin.OUT),        # DC
                backlight=Pin(12, Pin.OUT), # BL
                rotation=3  # Landscape for M5StickC PLUS
            )
            
            # Set initial brightness
            self.set_brightness(self.brightness)
            
            # Clear screen
            self.clear()
            
            print("M5StickC PLUS display initialized successfully")
            
        except Exception as e:
            print(f"Display init error: {e}")
            self.display = None
            raise
    
    def set_brightness(self, brightness):
        """Set display brightness (0-100)"""
        if self.display:
            self.display.brightness(brightness)
            self.brightness = brightness
    
    def clear(self, color=None):
        """Clear screen with color"""
        if self.display:
            fill_color = color if color is not None else self.colors['black']
            self.display.fill(fill_color)
        print(f"DISPLAY: Clear screen")
    
    def show_text(self, text, x, y, color=None, size=1):
        """Display text at position"""
        if self.display:
            text_color = color if color is not None else self.colors['pale_green']
            self.display.text(text, x, y, text_color, size)
        print(f"DISPLAY: Text at ({x},{y}): {text}")
    
    def show_startup(self):
        """Show startup screen"""
        print("DISPLAY: Showing startup screen")
        self.clear()
        
        # Title
        self.show_text("CLAUDE", 35, 40, self.colors['pale_green'], 2)
        self.show_text("MONITOR", 25, 70, self.colors['pale_green'], 2)
        
        # Subtitle
        self.show_text("M5StickC PLUS", 15, 110, self.colors['gray'])
        self.show_text("Starting...", 25, 130, self.colors['yellow'])
        
        self.current_screen = 'startup'
    
    def show_ready(self, ip_address):
        """Show ready screen with IP"""
        print(f"DISPLAY: Showing ready screen - IP: {ip_address}")
        self.clear()
        
        self.show_text("READY!", 35, 30, self.colors['green'], 2)
        
        # Show IP (truncate if too long)
        ip_text = ip_address if len(ip_address) <= 15 else ip_address[:15]
        self.show_text(ip_text, 10, 80, self.colors['pale_green'])
        
        self.show_text("Waiting for", 20, 110, self.colors['gray'])
        self.show_text("Claude...", 30, 130, self.colors['gray'])
        
        self.current_screen = 'ready'
    
    def show_error(self, message):
        """Show error message"""
        print(f"DISPLAY: Showing error - {message}")
        self.clear()
        
        self.show_text("ERROR", 40, 30, self.colors['red'], 2)
        
        # Show message (split if too long)
        if len(message) > 16:
            mid = len(message) // 2
            space_pos = message.find(' ', mid-3, mid+3)
            if space_pos != -1:
                line1 = message[:space_pos]
                line2 = message[space_pos+1:]
            else:
                line1 = message[:16]
                line2 = message[16:32]  # Limit second line too
            
            self.show_text(line1, 5, 80, self.colors['red'])
            self.show_text(line2, 5, 100, self.colors['red'])
        else:
            self.show_text(message, 10, 80, self.colors['red'])
        
        self.current_screen = 'error'
    
    def show_message(self, message, duration=2):
        """Show temporary message"""
        print(f"DISPLAY: Showing message - {message}")
        self.clear()
        
        self.show_text(message, 20, 100, self.colors['yellow'], 2)
        time.sleep(duration)
        
        self.current_screen = 'message'
    
    def update(self, session_data):
        """Update main display with session data"""
        current_time = time.time()
        
        # Update display every 2 seconds
        if current_time - self.last_update < 2:
            return
        
        print("DISPLAY: Updating session display")
        self.clear()
        
        # Show session status at top
        status = session_data.get('status', 'idle')
        if status == 'active':
            self.show_text("ACTIVE", 40, 5, self.colors['green'])
        elif status == 'idle':
            self.show_text("IDLE", 50, 5, self.colors['gray'])
        elif status == 'server_offline':
            self.show_text("OFFLINE", 35, 5, self.colors['red'])
        else:
            self.show_text(status.upper(), 20, 5, self.colors['yellow'])
        
        # Show session duration
        duration = session_data.get('duration', 0)
        hours = duration // 3600
        minutes = (duration % 3600) // 60
        seconds = duration % 60
        
        if hours > 0:
            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            time_str = f"{minutes:02d}:{seconds:02d}"
        
        self.show_text("Time:", 5, 40, self.colors['pale_green'])
        self.show_text(time_str, 10, 60, self.colors['white'], 2)
        
        # Show estimated cost
        cost = session_data.get('cost', 0.0)
        cost_str = f"${cost:.2f}"
        
        self.show_text("Cost:", 5, 100, self.colors['pale_green'])
        self.show_text(cost_str, 10, 120, self.colors['white'], 2)
        
        # Show alert indicator if pending
        if session_data.get('alert_pending'):
            alert_type = session_data.get('alert_type', 'generic')
            if int(current_time * 2) % 2:  # Blink every 0.5 seconds
                if alert_type == 'command_approval':
                    self.show_text("! APPROVE !", 10, 160, self.colors['yellow'])
                elif alert_type == 'cost_threshold':
                    self.show_text("$ COST $", 20, 160, self.colors['red'])
                else:
                    self.show_text("! ALERT !", 15, 160, self.colors['yellow'])
        
        # Show audio status
        if not session_data.get('alerts_enabled', True):
            self.show_text("MUTE", 5, 180, self.colors['gray'])
        
        # Show project name if available
        project = session_data.get('project_name')
        if project:
            # Truncate if too long
            if len(project) > 16:
                project = project[:16] + "..."
            self.show_text(project, 5, 200, self.colors['gray'])
        
        self.last_update = current_time
        self.current_screen = 'main'
    
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
