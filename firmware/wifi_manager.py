import network
import time
import socket
import gc

class WiFiManager:
    def __init__(self, ssid, password, timeout=15):
        self.ssid = ssid
        self.password = password
        self.timeout = timeout
        self.wlan = network.WLAN(network.STA_IF)
        self.connected = False
        
    def connect(self):
        """Connect to WiFi network"""
        print(f"Connecting to WiFi: {self.ssid}")
        
        if not self.wlan.active():
            self.wlan.active(True)
            
        if self.wlan.isconnected():
            print("Already connected")
            self.connected = True
            return True
            
        self.wlan.connect(self.ssid, self.password)
        
        # Wait for connection
        start_time = time.time()
        while not self.wlan.isconnected() and (time.time() - start_time) < self.timeout:
            print(".", end="")
            time.sleep(1)
            
        if self.wlan.isconnected():
            print(f"\nConnected! IP: {self.get_ip()}")
            self.connected = True
            return True
        else:
            print("\nConnection failed")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from WiFi"""
        if self.wlan.isconnected():
            self.wlan.disconnect()
        self.connected = False
        
    def is_connected(self):
        """Check if still connected"""
        connected = self.wlan.isconnected()
        self.connected = connected
        return connected
        
    def get_ip(self):
        """Get current IP address"""
        if self.wlan.isconnected():
            return self.wlan.ifconfig()[0]
        return None
        
    def get_signal_strength(self):
        """Get WiFi signal strength (RSSI)"""
        if self.wlan.isconnected():
            # Scan for our connected network
            networks = self.wlan.scan()
            for net in networks:
                if net[0].decode() == self.ssid:
                    return net[3]  # RSSI value
        return None
    
    def http_get(self, url, timeout=10):
        """Simple HTTP GET request"""
        if not self.is_connected():
            return None
            
        try:
            # Parse URL
            if url.startswith('http://'):
                url = url[7:]
            elif url.startswith('https://'):
                print("HTTPS not supported, use HTTP")
                return None
                
            if '/' in url:
                host, path = url.split('/', 1)
                path = '/' + path
            else:
                host = url
                path = '/'
                
            if ':' in host:
                host, port = host.split(':')
                port = int(port)
            else:
                port = 80
            
            # Create socket
            addr = socket.getaddrinfo(host, port)[0][-1]
            s = socket.socket()
            s.settimeout(timeout)
            
            # Connect and send request
            s.connect(addr)
            request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
            s.send(request.encode())
            
            # Read response
            response = b''
            while True:
                try:
                    data = s.recv(1024)
                    if not data:
                        break
                    response += data
                except OSError:
                    break
                    
            s.close()
            
            # Parse response
            response_str = response.decode('utf-8')
            if '\r\n\r\n' in response_str:
                header, body = response_str.split('\r\n\r\n', 1)
                if '200 OK' in header:
                    return body
                else:
                    print(f"HTTP Error: {header.split()[1]} {header.split()[2]}")
                    return None
            else:
                return None
                
        except Exception as e:
            print(f"HTTP GET error: {e}")
            return None
        finally:
            gc.collect()
    
    def http_post(self, url, data, content_type="application/json", timeout=10):
        """Simple HTTP POST request"""
        if not self.is_connected():
            return None
            
        try:
            # Parse URL
            if url.startswith('http://'):
                url = url[7:]
            elif url.startswith('https://'):
                print("HTTPS not supported, use HTTP")
                return None
                
            if '/' in url:
                host, path = url.split('/', 1)
                path = '/' + path
            else:
                host = url
                path = '/'
                
            if ':' in host:
                host, port = host.split(':')
                port = int(port)
            else:
                port = 80
            
            # Prepare data
            if isinstance(data, dict):
                import json
                data = json.dumps(data)
            data_bytes = data.encode('utf-8')
            
            # Create socket
            addr = socket.getaddrinfo(host, port)[0][-1]
            s = socket.socket()
            s.settimeout(timeout)
            
            # Connect and send request
            s.connect(addr)
            request = f"POST {path} HTTP/1.1\r\n"
            request += f"Host: {host}\r\n"
            request += f"Content-Type: {content_type}\r\n"
            request += f"Content-Length: {len(data_bytes)}\r\n"
            request += "Connection: close\r\n\r\n"
            
            s.send(request.encode())
            s.send(data_bytes)
            
            # Read response
            response = b''
            while True:
                try:
                    chunk = s.recv(1024)
                    if not chunk:
                        break
                    response += chunk
                except OSError:
                    break
                    
            s.close()
            
            # Parse response
            response_str = response.decode('utf-8')
            if '\r\n\r\n' in response_str:
                header, body = response_str.split('\r\n\r\n', 1)
                if '200 OK' in header:
                    return body
                else:
                    print(f"HTTP Error: {header.split()[1]} {header.split()[2]}")
                    return None
            else:
                return None
                
        except Exception as e:
            print(f"HTTP POST error: {e}")
            return None
        finally:
            gc.collect()
    
    def ping(self, host, timeout=5):
        """Simple connectivity test"""
        try:
            addr = socket.getaddrinfo(host, 80)[0][-1]
            s = socket.socket()
            s.settimeout(timeout)
            start = time.ticks_ms()
            s.connect(addr)
            s.close()
            duration = time.ticks_diff(time.ticks_ms(), start)
            return duration
        except:
            return None
