class Config:
    """Configuration for M5StickC PLUS Claude Monitor"""
    
    # WiFi Settings - Load from credentials.txt (not in git)
    WIFI_SSID = None
    WIFI_PASSWORD = None
    
    # MCP Server Settings - Load from credentials.txt
    SERVER_HOST = None
    SERVER_PORT = 8080
    
    # Device Settings
    DEVICE_NAME = "claude-monitor"
    UPDATE_INTERVAL = 5  # Seconds between server updates
    
    # Display Settings
    BRIGHTNESS = 50  # 0-100
    SHOW_COST = True
    CURRENCY = "USD"
    
    # Alert Settings
    QUIET_TONE_FREQUENCY = 800  # Hz
    TONE_DURATION = 100  # milliseconds
    TONE_VOLUME = 10  # 0-100
    ALERT_TIMEOUT = 300  # seconds
    BLINK_RATE = 2  # blinks per second
    
    # Hardware Settings
    BUTTON_DEBOUNCE_MS = 50
    SLEEP_TIMEOUT = 300  # seconds of inactivity before sleep
    
    # Debug Settings
    DEBUG_MODE = False
    VERBOSE_LOGGING = False
    
    def __init__(self):
        """Initialize config and load credentials"""
        self.load_credentials()
    
    def load_credentials(self, filename='credentials.txt'):
        """Load WiFi credentials and server info from separate file"""
        try:
            with open(filename, 'r') as f:
                lines = f.read().strip().split('\n')
                for line in lines:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        
                        if key == 'WIFI_SSID':
                            self.WIFI_SSID = value
                        elif key == 'WIFI_PASSWORD':
                            self.WIFI_PASSWORD = value
                        elif key == 'SERVER_HOST':
                            self.SERVER_HOST = value
                        elif key == 'SERVER_PORT':
                            self.SERVER_PORT = int(value)
                        elif key == 'DEVICE_NAME':
                            self.DEVICE_NAME = value
                            
        except Exception as e:
            print(f"Warning: Could not load credentials from {filename}: {e}")
            print("Please copy credentials.sample.txt to credentials.txt and configure")
    
    def validate(self):
        """Validate configuration values"""
        errors = []
        
        # WiFi validation
        if not self.WIFI_SSID or self.WIFI_SSID == 'your-network-name':
            errors.append("WIFI_SSID must be set in credentials.txt")
            
        if not self.WIFI_PASSWORD or self.WIFI_PASSWORD == 'your-wifi-password':
            errors.append("WIFI_PASSWORD must be set in credentials.txt")
        
        # Server validation
        if not self.SERVER_HOST or self.SERVER_HOST == '192.168.1.100':
            errors.append("SERVER_HOST must be configured in credentials.txt")
            
        # Range validations
        if not 0 <= self.BRIGHTNESS <= 100:
            errors.append("BRIGHTNESS must be between 0-100")
            
        if not 0 <= self.TONE_VOLUME <= 100:
            errors.append("TONE_VOLUME must be between 0-100")
            
        if self.UPDATE_INTERVAL < 1:
            errors.append("UPDATE_INTERVAL must be at least 1 second")
            
        return errors
