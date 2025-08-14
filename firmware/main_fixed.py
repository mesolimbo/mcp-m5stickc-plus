"""
Main entry point for M5StickC PLUS demo
Uses original working framebuffer approach
"""

print("M5StickC PLUS Demo Starting...")
print("Using original framebuffer graphics...")

try:
    from demo import main
    print("Demo module imported successfully!")
    main()
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure graphics.py and demo.py are uploaded")
except Exception as e:
    print(f"Error running demo: {e}")
    import time
    time.sleep(5)
    import machine
    machine.reset()