import time
import gc
from display import DisplayManager
from alerts import AlertManager
from sensors import SensorManager

def test_display():
    """Test display functionality"""
    print("\n=== Testing Display ===")
    display = DisplayManager(brightness=70)
    
    # Test startup screen
    print("Testing startup screen...")
    display.show_startup()
    time.sleep(2)
    
    # Test ready screen
    print("Testing ready screen...")
    display.show_ready("192.168.1.100")
    time.sleep(2)
    
    # Test error screen
    print("Testing error screen...")
    display.show_error("WiFi Failed")
    time.sleep(2)
    
    # Test message
    print("Testing message screen...")
    display.show_message("Audio disabled", 1)
    
    # Test main session display
    print("Testing session display...")
    test_session_data = {
        'status': 'active',
        'duration': 1847,  # 30:47
        'cost': 3.25,
        'alerts_enabled': True,
        'alert_pending': True,
        'alert_type': 'command_approval',
        'project_name': 'mcp-server',
        'wifi_signal': -45
    }
    
    for i in range(10):
        test_session_data['duration'] += 1
        test_session_data['cost'] += 0.01
        display.update(test_session_data)
        time.sleep(1)
    
    print("Display test complete!")

def test_alerts():
    """Test alert system"""
    print("\n=== Testing Alerts ===")
    alerts = AlertManager()
    
    # Test all alert types
    test_types = ['command_approval', 'cost_threshold', 'session_milestone', 'server_offline']
    
    for alert_type in test_types:
        print(f"Testing {alert_type} alert...")
        alerts.trigger_alert(alert_type)
        
        # Let the alert play for a few seconds
        for _ in range(50):  # 5 seconds at 0.1s intervals
            alerts.update()
            time.sleep(0.1)
        
        alerts.acknowledge_alert()
        time.sleep(1)
    
    # Test disable/enable
    print("Testing alert disable/enable...")
    alerts.set_enabled(False)
    alerts.trigger_alert('command_approval')
    time.sleep(1)
    
    alerts.set_enabled(True)
    alerts.trigger_alert('command_approval')
    time.sleep(2)
    alerts.acknowledge_alert()
    
    alerts.cleanup()
    print("Alert test complete!")

def test_sensors():
    """Test sensor input"""
    print("\n=== Testing Sensors ===")
    sensors = SensorManager()
    
    print("Press buttons A and B to test (wait 10 seconds or press both to continue)...")
    
    start_time = time.time()
    both_pressed = False
    
    while time.time() - start_time < 10 and not both_pressed:
        button_a, button_b = sensors.read_buttons()
        
        if button_a:
            print("Button A pressed! (Main button)")
            
        if button_b:
            print("Button B pressed! (Side button)")
            
        # Check if both held
        if sensors.is_button_held('a') and sensors.is_button_held('b'):
            both_pressed = True
            print("Both buttons held - continuing...")
            
        time.sleep(0.1)
    
    print("Sensor test complete!")

def test_mock_session():
    """Test complete mock session"""
    print("\n=== Testing Mock Session ===")
    
    # Initialize all components
    display = DisplayManager(brightness=50)
    alerts = AlertManager()
    sensors = SensorManager()
    
    # Show startup
    display.show_startup()
    time.sleep(2)
    
    # Show ready (no WiFi needed for test)
    display.show_ready("TEST.MODE")
    time.sleep(2)
    
    # Mock session data
    session_data = {
        'status': 'active',
        'duration': 0,
        'cost': 0.0,
        'alerts_enabled': True,
        'alert_pending': False,
        'project_name': 'firmware-test'
    }
    
    print("Mock session running... Press Button A to toggle audio, B to ack alerts")
    print("Both buttons together to exit")
    
    alert_counter = 0
    
    try:
        while True:
            # Simulate session progress
            session_data['duration'] += 1
            session_data['cost'] += 0.002
            
            # Trigger alert every 15 seconds
            if session_data['duration'] % 15 == 0:
                session_data['alert_pending'] = True
                session_data['alert_type'] = ['command_approval', 'cost_threshold'][alert_counter % 2]
                alerts.trigger_alert(session_data['alert_type'])
                alert_counter += 1
            
            # Check buttons
            button_a, button_b = sensors.read_buttons()
            
            if button_a:  # Toggle audio
                session_data['alerts_enabled'] = not session_data['alerts_enabled']
                alerts.set_enabled(session_data['alerts_enabled'])
                status = "enabled" if session_data['alerts_enabled'] else "disabled"
                display.show_message(f"Audio {status}", 1)
            
            if button_b:  # Acknowledge alert
                if session_data['alert_pending']:
                    session_data['alert_pending'] = False
                    alerts.acknowledge_alert()
            
            # Exit if both buttons held
            if sensors.is_button_held('a') and sensors.is_button_held('b'):
                print("\nExiting mock session...")
                break
            
            # Update components
            display.update(session_data)
            alerts.update()
            
            time.sleep(1)
            gc.collect()
            
    except KeyboardInterrupt:
        print("\nMock session interrupted")
    
    # Cleanup
    alerts.cleanup()
    print("Mock session test complete!")

def run_all_tests():
    """Run all firmware tests"""
    print("M5StickC PLUS Firmware Test Suite")
    print("==================================\n")
    
    tests = [
        ("Display", test_display),
        ("Alerts", test_alerts), 
        ("Sensors", test_sensors),
        ("Mock Session", test_mock_session)
    ]
    
    for test_name, test_func in tests:
        try:
            print(f"\n>>> Running {test_name} test...")
            test_func()
            print(f">>> {test_name} test PASSED")
        except Exception as e:
            print(f">>> {test_name} test FAILED: {e}")
        
        # Small pause between tests
        time.sleep(1)
    
    print("\n=== All Tests Complete ===")

if __name__ == "__main__":
    # Check if specific test requested
    import sys
    
    if len(sys.argv) > 1:
        test_name = sys.argv[1].lower()
        if test_name == 'display':
            test_display()
        elif test_name == 'alerts':
            test_alerts()
        elif test_name == 'sensors':
            test_sensors()
        elif test_name == 'session':
            test_mock_session()
        else:
            print(f"Unknown test: {test_name}")
            print("Available tests: display, alerts, sensors, session")
    else:
        # Run all tests
        run_all_tests()
