import gc
import time
import json
from machine import Pin, SPI, I2C, PWM
from display import DisplayManager
from wifi_manager import WiFiManager
from alerts import AlertManager
from sensors import SensorManager

try:
    from config import Config
except ImportError:
    print("Warning: config.py not found, using defaults")
    class Config:
        WIFI_SSID = "your-network"
        WIFI_PASSWORD = "your-password"
        SERVER_HOST = "192.168.1.50"
        SERVER_PORT = 8080
        UPDATE_INTERVAL = 5
        BRIGHTNESS = 50

class M5StickClaudeMonitor:
    def __init__(self):
        print("Initializing M5StickC PLUS Claude Monitor...")
        self.config = Config()
        
        # Initialize hardware managers
        self.display = DisplayManager(brightness=self.config.BRIGHTNESS)
        self.wifi = WiFiManager(self.config.WIFI_SSID, self.config.WIFI_PASSWORD)
        self.alerts = AlertManager()
        self.sensors = SensorManager()
        
        # State tracking
        self.session_data = {
            'duration': 0,
            'cost': 0.0,
            'status': 'idle',
            'alerts_enabled': True,
            'last_update': 0
        }
        
        self.running = True
        
    def start(self):
        """Main application loop"""
        print("Starting Claude Monitor...")
        
        # Show startup screen
        self.display.show_startup()
        
        # Connect to WiFi
        if not self.wifi.connect():
            self.display.show_error("WiFi Failed")
            return
            
        # Show ready screen
        self.display.show_ready(self.wifi.get_ip())
        time.sleep(2)
        
        # Main loop
        last_server_check = 0
        while self.running:
            try:
                current_time = time.time()
                
                # Check sensors (buttons, etc.)
                self.handle_sensors()
                
                # Update from server every N seconds
                if current_time - last_server_check >= self.config.UPDATE_INTERVAL:
                    self.update_from_server()
                    last_server_check = current_time
                
                # Update display
                self.display.update(self.session_data)
                
                # Handle alerts
                if self.session_data.get('alert_pending'):
                    self.alerts.trigger_alert(self.session_data['alert_type'])
                
                time.sleep(0.1)  # Small delay to prevent busy waiting
                gc.collect()  # Periodic garbage collection
                
            except KeyboardInterrupt:
                print("Stopping...")
                self.running = False
            except Exception as e:
                print(f"Error in main loop: {e}")
                self.display.show_error(str(e))
                time.sleep(1)
    
    def handle_sensors(self):
        """Handle button presses and other sensor input"""
        button_a, button_b = self.sensors.read_buttons()
        
        if button_a:  # Main button - toggle audio alerts
            self.session_data['alerts_enabled'] = not self.session_data['alerts_enabled']
            self.alerts.set_enabled(self.session_data['alerts_enabled'])
            status = "enabled" if self.session_data['alerts_enabled'] else "disabled"
            self.display.show_message(f"Audio {status}", 1)
            
        if button_b:  # Side button - acknowledge current alert
            if self.session_data.get('alert_pending'):
                self.session_data['alert_pending'] = False
                self.alerts.acknowledge_alert()
    
    def update_from_server(self):
        """Get latest session data from MCP server"""
        try:
            # Try to get session data from server
            url = f"http://{self.config.SERVER_HOST}:{self.config.SERVER_PORT}/api/session"
            response = self.wifi.http_get(url, timeout=5)
            
            if response:
                data = json.loads(response)
                self.session_data.update(data)
                self.session_data['last_update'] = time.time()
            else:
                # Server not responding
                if self.session_data['status'] != 'server_offline':
                    self.session_data['status'] = 'server_offline'
                    self.display.show_message("Server Offline", 2)
                    
        except Exception as e:
            print(f"Server update error: {e}")
            self.session_data['status'] = 'error'
    
    def test_mode(self):
        """Run in test mode with mock data for development"""
        print("Running in TEST MODE")
        self.display.show_startup()
        time.sleep(2)
        
        # Simulate session data
        test_data = {
            'duration': 1250,  # 20:50
            'cost': 2.35,
            'status': 'active',
            'alerts_enabled': True,
            'alert_pending': False,
            'project_name': 'mcp-server'
        }
        
        counter = 0
        while True:
            try:
                # Simulate changing data
                test_data['duration'] += 1
                test_data['cost'] += 0.001
                
                # Simulate alert every 30 seconds
                if counter % 300 == 0:  # Every 30 seconds at 0.1s intervals
                    test_data['alert_pending'] = True
                    test_data['alert_type'] = 'command_approval'
                
                self.handle_sensors()
                self.display.update(test_data)
                
                if test_data.get('alert_pending'):
                    self.alerts.trigger_alert(test_data['alert_type'])
                
                time.sleep(0.1)
                counter += 1
                gc.collect()
                
            except KeyboardInterrupt:
                break

def main():
    """Entry point"""
    monitor = M5StickClaudeMonitor()
    
    # Check if we should run in test mode
    # Hold button A during startup for test mode
    test_pin = Pin(37, Pin.IN)
    if not test_pin.value():  # Button pressed (active low)
        monitor.test_mode()
    else:
        monitor.start()

if __name__ == "__main__":
    main()
