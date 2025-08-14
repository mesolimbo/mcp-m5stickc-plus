"""
Main entry point for M5StickC PLUS enhanced graphics demo
Features image display and La Cucaracha music
"""

print("M5StickC PLUS Enhanced Demo Starting...")
print("Loading enhanced graphics with image support...")

try:
    from demo_enhanced import main
    print("Enhanced demo module imported successfully!")
    main()
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure graphics_enhanced.py and demo_enhanced.py are uploaded")
except Exception as e:
    print(f"Error running enhanced demo: {e}")
    import time
    time.sleep(5)
    import machine
    machine.reset()