# Minimal Claude Monitor - Start with what works and build up slowly
import time
from machine import Pin, SPI, I2C

print("Minimal Claude Monitor Test")

def minimal_claude_monitor():
    # AXP192 setup (required for display power)
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    i2c.writeto_mem(0x34, 0x12, bytes([0xFF]))  # Enable LDOs
    i2c.writeto_mem(0x34, 0x96, bytes([0x84]))  # GPIO2 output
    i2c.writeto_mem(0x34, 0x95, bytes([0x02]))  # Backlight on
    time.sleep_ms(200)
    print("AXP192 configured")
    
    # SPI setup
    spi = SPI(1, baudrate=8000000, sck=Pin(13), mosi=Pin(15))
    reset = Pin(18, Pin.OUT, value=1)
    cs = Pin(5, Pin.OUT, value=1)
    dc = Pin(23, Pin.OUT, value=0)
    
    def cmd(c):
        cs.value(0); dc.value(0)
        spi.write(bytearray([c]))
        cs.value(1); time.sleep_ms(1)
    
    def data(d):
        cs.value(0); dc.value(1)
        spi.write(bytearray([d]))
        cs.value(1); time.sleep_ms(1)
    
    def fill_simple_area(x, y, w, h, color):
        """Use the EXACT coordinate method that worked in our tests"""
        # Apply M5StickC PLUS offsets: x+52, y+40
        col_start = x + 52
        col_end = x + w - 1 + 52
        row_start = y + 40  
        row_end = y + h - 1 + 40
        
        cmd(0x2A)  # Column Address Set
        data(col_start >> 8); data(col_start & 0xFF)
        data(col_end >> 8); data(col_end & 0xFF)
        
        cmd(0x2B)  # Row Address Set  
        data(row_start >> 8); data(row_start & 0xFF)
        data(row_end >> 8); data(row_end & 0xFF)
        
        cmd(0x2C)  # Memory Write
        
        cs.value(0); dc.value(1)
        color_bytes = bytearray([color >> 8, color & 0xFF])
        for _ in range(w * h):
            spi.write(color_bytes)
        cs.value(1)
    
    # Initialize display with EXACT same settings that worked
    print("Initializing ST7789...")
    reset.value(0); time.sleep_ms(50)
    reset.value(1); time.sleep_ms(200)
    
    cmd(0x01); time.sleep_ms(150)  # Software reset
    cmd(0x11); time.sleep_ms(120)  # Sleep out
    cmd(0x36); data(0x00)          # Rotation 0x00 (the one that worked!)
    cmd(0x3A); data(0x05)          # RGB565 pixel format
    cmd(0x21)                      # Display inversion on
    cmd(0x13)                      # Normal display mode
    cmd(0x29); time.sleep_ms(50)   # Display on
    
    print("Display initialized")
    
    # Step 1: Clear to black (like our working test)
    print("Step 1: Clear screen")
    fill_simple_area(0, 0, 135, 240, 0x0000)  # Black
    time.sleep(2)
    
    # Step 2: Simple "CLAUDE" title (green rectangle)
    print("Step 2: CLAUDE title")
    fill_simple_area(10, 30, 115, 25, 0x07E0)  # Green rectangle for "CLAUDE"
    time.sleep(3)
    
    # Step 3: "MONITOR" subtitle (blue rectangle)
    print("Step 3: MONITOR subtitle") 
    fill_simple_area(10, 60, 115, 25, 0x001F)  # Blue rectangle for "MONITOR"
    time.sleep(3)
    
    # Step 4: Demo session data simulation
    print("Step 4: Session simulation")
    
    for session_time in range(1, 21):  # 20 steps
        # Clear work area (keep title)
        fill_simple_area(0, 100, 135, 140, 0x0000)  # Clear lower area
        
        # Status bar (green = active)
        fill_simple_area(0, 0, 135, 15, 0x07E0)  # Green status
        
        # Duration bar (grows with time)
        duration_width = session_time * 6  # 6 pixels per time unit
        if duration_width > 125:
            duration_width = 125
        fill_simple_area(5, 110, duration_width, 20, 0x07FF)  # Cyan duration
        
        # Cost bar (grows slower)
        cost_width = session_time * 3  # 3 pixels per time unit  
        if cost_width > 125:
            cost_width = 125
        fill_simple_area(5, 140, cost_width, 15, 0xFFE0)  # Yellow cost
        
        # Alert every 5 time units
        if session_time % 5 == 0:
            fill_simple_area(5, 170, 125, 25, 0xF800)  # Red alert
            print(f"ALERT at time {session_time}")
        else:
            fill_simple_area(5, 170, 125, 25, 0x0000)  # No alert
        
        print(f"Session time: {session_time}, Duration: {duration_width}px, Cost: {cost_width}px")
        time.sleep(1.5)
    
    # Final state
    print("Demo complete - showing final state")
    fill_simple_area(5, 200, 125, 20, 0xFFFF)  # White "complete" bar
    
    print("Claude Monitor minimal test finished!")

minimal_claude_monitor()