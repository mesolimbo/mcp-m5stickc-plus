import esp
import gc

esp.osdebug(None)  # Turn off vendor O/S debugging messages
gc.collect()  # Clean up memory

print("M5StickC PLUS - Claude Session Monitor")
print("Booting...")

# Skip WebREPL to avoid errors
print("Skipping WebREPL setup...")

# Auto-start main application
print("Starting main application...")
try:
    import main
    main.main()
except Exception as e:
    print(f"Failed to start main: {e}")
    import sys
    sys.print_exception(e)
