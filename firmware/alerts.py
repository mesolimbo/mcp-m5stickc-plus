import time
from machine import Pin, PWM

class AlertManager:
    def __init__(self):
        # Initialize buzzer (Pin 2 for M5StickC PLUS)
        try:
            self.buzzer = PWM(Pin(2), freq=800, duty=0)
            self.buzzer_available = True
        except Exception as e:
            print(f"Buzzer not available: {e}")
            self.buzzer_available = False
            self.buzzer = None
        
        # Alert state
        self.enabled = True
        self.current_alert = None
        self.alert_start_time = 0
        
        # Alert patterns (frequency, duration_ms, pause_ms, repetitions)
        self.patterns = {
            'command_approval': (800, 100, 200, 3),
            'cost_threshold': (600, 50, 100, 5),
            'session_milestone': (1000, 150, 300, 2),
            'server_offline': (400, 200, 500, 1),
            'generic': (800, 100, 200, 2)
        }
    
    def set_enabled(self, enabled):
        """Enable or disable audio alerts"""
        self.enabled = enabled
        if not enabled and self.buzzer_available:
            self.buzzer.duty(0)  # Stop any current sound
    
    def trigger_alert(self, alert_type='generic'):
        """Trigger an alert with specified type"""
        if not self.enabled:
            print(f"ALERT (silent): {alert_type}")
            return
            
        pattern = self.patterns.get(alert_type, self.patterns['generic'])
        frequency, duration, pause, reps = pattern
        
        self.current_alert = {
            'type': alert_type,
            'pattern': pattern,
            'rep_count': 0,
            'state': 'tone',  # 'tone' or 'pause'
            'start_time': time.ticks_ms()
        }
        
        print(f"ALERT: {alert_type} - {reps} beeps at {frequency}Hz")
        
        if self.buzzer_available:
            self.play_pattern()
        else:
            # Mock alert for testing without buzzer
            print(f"BEEP: {frequency}Hz for {duration}ms x{reps}")
    
    def play_pattern(self):
        """Play the current alert pattern (non-blocking)"""
        if not self.current_alert or not self.buzzer_available:
            return
            
        pattern = self.current_alert['pattern']
        frequency, duration, pause, max_reps = pattern
        
        current_time = time.ticks_ms()
        elapsed = time.ticks_diff(current_time, self.current_alert['start_time'])
        
        if self.current_alert['state'] == 'tone':
            # Start/continue tone
            self.buzzer.freq(frequency)
            self.buzzer.duty(512)  # 50% duty cycle
            
            if elapsed >= duration:
                # End tone, start pause
                self.buzzer.duty(0)
                self.current_alert['state'] = 'pause'
                self.current_alert['start_time'] = current_time
                
        elif self.current_alert['state'] == 'pause':
            # In pause between tones
            if elapsed >= pause:
                self.current_alert['rep_count'] += 1
                
                if self.current_alert['rep_count'] >= max_reps:
                    # Pattern complete
                    self.current_alert = None
                else:
                    # Start next tone
                    self.current_alert['state'] = 'tone'
                    self.current_alert['start_time'] = current_time
    
    def update(self):
        """Update alert state - call this regularly in main loop"""
        if self.current_alert:
            self.play_pattern()
    
    def acknowledge_alert(self):
        """Stop current alert (user acknowledged)"""
        if self.current_alert:
            self.current_alert = None
            if self.buzzer_available:
                self.buzzer.duty(0)
            print("Alert acknowledged")
    
    def stop_all(self):
        """Stop all alerts immediately"""
        self.current_alert = None
        if self.buzzer_available:
            self.buzzer.duty(0)
    
    def test_all_patterns(self):
        """Test all alert patterns for debugging"""
        print("Testing all alert patterns...")
        for alert_type in self.patterns.keys():
            print(f"Testing {alert_type}...")
            self.trigger_alert(alert_type)
            
            # Wait for pattern to complete
            timeout = 5000  # 5 seconds max per pattern
            start = time.ticks_ms()
            while self.current_alert and time.ticks_diff(time.ticks_ms(), start) < timeout:
                self.update()
                time.sleep_ms(10)
                
            time.sleep(1)  # Pause between patterns
    
    def cleanup(self):
        """Clean up resources"""
        if self.buzzer_available:
            self.buzzer.duty(0)
            self.buzzer.deinit()
