# Minimal main.py to test display
print("Starting minimal main.py")

try:
    # Try to import and test display
    print("Testing display...")
    
    # For now, just print - display driver might not be available
    print("M5StickC PLUS is alive!")
    print("If you see this, basic Python is working")
    
    import time
    counter = 0
    while True:
        counter += 1
        print(f"Loop {counter}")
        time.sleep(2)
        if counter > 10:
            break
            
    print("Minimal test complete")
    
except Exception as e:
    print(f"Error in minimal main: {e}")
    import time
    time.sleep(5)
