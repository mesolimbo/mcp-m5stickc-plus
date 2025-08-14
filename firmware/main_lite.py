"""
Main entry point for M5StickC PLUS lite graphics demo
Uses memory-efficient graphics to avoid allocation errors
"""

print("M5StickC PLUS Lite Demo Starting...")
print("Using memory-efficient graphics...")

try:
    from demo_lite import main
    print("Lite demo module imported successfully!")
    main()
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure graphics_lite.py and demo_lite.py are uploaded")
except Exception as e:
    print(f"Error running lite demo: {e}")
    import time
    time.sleep(5)
    import machine
    machine.reset()