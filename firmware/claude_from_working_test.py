# Claude Monitor built from EXACT working coordinate test
import time
from machine import Pin, SPI, I2C

print("Claude Monitor - Using Proven Coordinate Method")

def claude_monitor_from_working_test():
    # AXP192 setup (EXACT same as working test)
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    i2c.writeto_mem(0x34, 0x12, bytes([0xFF]))  # Enable LDOs
    i2c.writeto_mem(0x34, 0x96, bytes([0x84]))  # GPIO2 output
    i2c.writeto_mem(0x34, 0x95, bytes([0x02]))  # Backlight on
    time.sleep_ms(200)
    print("AXP192 configured")
    
    # SPI setup (EXACT same as working test)
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
    
    def set_window_correct(x_start, y_start, x_end, y_end):
        """EXACT method from working coordinate test - DO NOT CHANGE"""
        # M5StickC PLUS ST7789V2 offsets: x_start=52, y_start=40 for rotation 0
        x_offset = 52
        y_offset = 40
        
        # Apply offsets to coordinates
        col_start = x_start + x_offset
        col_end = x_end + x_offset
        row_start = y_start + y_offset  
        row_end = y_end + y_offset
        
        cmd(0x2A)  # Column Address Set
        data(col_start >> 8); data(col_start & 0xFF)
        data(col_end >> 8); data(col_end & 0xFF)
        
        cmd(0x2B)  # Row Address Set  
        data(row_start >> 8); data(row_start & 0xFF)
        data(row_end >> 8); data(row_end & 0xFF)
        
        cmd(0x2C)  # Memory Write
    
    def fill_area(x, y, w, h, color):
        """EXACT method from working coordinate test - DO NOT CHANGE"""
        set_window_correct(x, y, x + w - 1, y + h - 1)
        
        cs.value(0); dc.value(1)
        color_bytes = bytearray([color >> 8, color & 0xFF])
        for _ in range(w * h):
            spi.write(color_bytes)
        cs.value(1)
    
    # Initialize display (EXACT same as working test)
    print("Initializing ST7789...")
    reset.value(0); time.sleep_ms(50)
    reset.value(1); time.sleep_ms(200)
    
    cmd(0x01); time.sleep_ms(150)  # Software reset
    cmd(0x11); time.sleep_ms(120)  # Sleep out
    cmd(0x36); data(0x00)          # Memory access control (Correct landscape rotation)
    cmd(0x3A); data(0x05)          # RGB565 pixel format
    cmd(0x21)                      # Display inversion on
    cmd(0x13)                      # Normal display mode
    cmd(0x29); time.sleep_ms(50)   # Display on
    
    print("Display initialized")
    
    # CLAUDE MONITOR VERSION - Using EXACT working test pattern
    print("Starting Claude Monitor display...")
    
    # Step 1: Full screen black (like working test)
    print("Step 1: Clear screen black")
    fill_area(0, 0, 135, 240, 0x0000)  # Black - full 135x240 area
    time.sleep(2)
    
    # Step 2: "CLAUDE" title bar (green, like working test green areas)
    print("Step 2: CLAUDE title")
    fill_area(0, 0, 135, 30, 0x07E0)  # Green - full width title
    time.sleep(2)
    
    # Step 3: "MONITOR" subtitle (blue, like working test blue areas)
    print("Step 3: MONITOR subtitle")  
    fill_area(0, 35, 135, 25, 0x001F)  # Blue - full width subtitle
    time.sleep(2)
    
    # Step 4: Session data simulation (like working test quadrants)
    print("Step 4: Session simulation")
    
    for i in range(20):  # 20 iterations like working test
        # Clear data area (keep titles)
        fill_area(0, 70, 135, 170, 0x0000)  # Clear data area
        
        # Session status (green for active, like working test)
        if i > 2:
            fill_area(10, 80, 115, 15, 0x07E0)  # Active - green
        else:
            fill_area(10, 80, 115, 15, 0x001F)  # Starting - blue
        
        # Duration bar (cyan, growing like working test)
        duration_width = min(i * 5, 115)  # Grow with time
        if duration_width > 0:
            fill_area(10, 105, duration_width, 20, 0x07FF)  # Cyan duration
        
        # Cost bar (yellow, growing slower like working test)
        cost_width = min(i * 3, 115)  # Grow slower
        if cost_width > 0:
            fill_area(10, 135, cost_width, 15, 0xFFE0)  # Yellow cost
        
        # Alert indicator (red flash every 5 iterations, like working test)
        if i % 5 == 0 and i > 0:
            fill_area(10, 160, 115, 25, 0xF800)  # Red alert
            print(f"ALERT at iteration {i}")
        else:
            fill_area(10, 160, 115, 25, 0x0000)  # No alert
        
        # Session stats (dots, like working test)
        sessions = min(i // 3, 10)
        for dot in range(sessions):
            fill_area(10 + dot * 11, 195, 8, 8, 0xFFE0)  # Yellow dots
        
        # Bottom status bar (white, like working test borders)
        fill_area(0, 220, 135, 20, 0xFFFF)  # White status
        
        print(f"Claude session step {i}: {duration_width}px duration, {cost_width}px cost")
        time.sleep(1)
    
    print("Claude Monitor test complete!")
    print("This shows what real session tracking will look like")

claude_monitor_from_working_test()