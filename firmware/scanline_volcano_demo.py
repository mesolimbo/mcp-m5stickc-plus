"""
Scanline Volcano Demo - Proper Implementation
Uses the cheatsheet's scanline streaming method for minimal RAM usage
"""

import time
import gc
from machine import Pin, PWM
from graphics import M5Display, Colors

def main():
    print("Starting Scanline Volcano Demo!")
    print("Using proper scanline streaming from cheatsheet")
    
    # Initialize display
    display = M5Display(brightness=True)
    
    # Initialize button
    button_a = Pin(37, Pin.IN, Pin.PULL_UP)
    
    # Initialize buzzer
    try:
        buzzer = PWM(Pin(2), freq=440, duty=0)
        has_buzzer = True
        print("Buzzer available")
    except:
        buzzer = None
        has_buzzer = False
        print("No buzzer")
    
    # Show welcome screen
    display.clear(Colors.BLACK)
    display.rect(0, 0, 135, 25, Colors.ORANGE, filled=True)
    display.text(5, 8, "SCANLINE DEMO", Colors.WHITE, Colors.ORANGE)
    
    display.text(5, 35, "CHEATSHEET METHOD", Colors.CYAN)
    display.text(5, 55, "STREAM BY SCANLINE", Colors.YELLOW)
    display.text(5, 75, "MINIMAL RAM USAGE", Colors.GREEN)
    
    # Memory info
    free_mem = gc.mem_free()
    display.text(5, 105, f"FREE RAM: {free_mem}", Colors.WHITE)
    display.text(5, 125, f"NEED: ~{135*2} BYTES", Colors.PALE_GREEN)
    
    # Instructions  
    display.rect(0, 150, 135, 50, Colors.BLUE, filled=True)
    display.text(5, 160, "PRESS BUTTON A", Colors.WHITE, Colors.BLUE)
    display.text(5, 175, "TO STREAM IMAGE", Colors.WHITE, Colors.BLUE)
    display.text(5, 190, "SCANLINE BY LINE", Colors.WHITE, Colors.BLUE)
    
    # Footer
    display.rect(0, 220, 135, 20, Colors.PURPLE, filled=True)
    display.text(10, 225, "MEMORY EFFICIENT", Colors.WHITE, Colors.PURPLE)
    
    display.show()
    
    print("Waiting for button press...")
    
    # Wait for button press
    while button_a.value() == 1:
        time.sleep_ms(50)
    
    print("Button pressed! Starting scanline streaming...")
    
    # Show loading screen
    display.clear(Colors.BLACK)
    display.text(20, 100, "STREAMING...", Colors.YELLOW)
    display.text(10, 120, "SCANLINE BY LINE", Colors.CYAN)
    display.show()
    
    # Force garbage collection before streaming
    gc.collect()
    mem_before = gc.mem_free()
    print(f"Memory before streaming: {mem_before} bytes")
    
    # Try scanline streaming
    try:
        # Stream the volcano image using scanline method
        success = display.draw_rgb565_file('/volcano_scanline.rgb565')
        
        if success:
            print("Scanline streaming successful!")
            
            # Add title overlay using framebuffer
            display.rect(0, 0, 135, 20, Colors.BLACK, filled=True)
            display.text(5, 5, "SCANLINE VOLCANO", Colors.YELLOW)
            
            display.rect(0, 220, 135, 20, Colors.BLACK, filled=True) 
            display.text(5, 225, "STREAMED LIVE!", Colors.CYAN)
            
            # Update overlay only (not full screen)
            display.set_window(0, 0, 135, 20)
            display.write(display.framebuffer[0:135*20*2])
            
            display.set_window(0, 220, 135, 20)
            display.write(display.framebuffer[220*135*2:(220+20)*135*2])
            
            # Check memory usage
            mem_after = gc.mem_free()
            print(f"Memory after streaming: {mem_after} bytes")
            print(f"Memory used: {mem_before - mem_after} bytes")
            
            # Play La Cucaracha if available
            if has_buzzer:
                print("Playing La Cucaracha with scanline image...")
                
                melody = [523, 523, 523, 659, 698, 698, 659, 659, 587, 587, 523, 0,
                         523, 523, 523, 659, 698, 698, 659, 659, 587, 523]
                durations = [2, 2, 2, 4, 4, 2, 2, 2, 2, 2, 4, 2,
                            2, 2, 2, 4, 4, 2, 2, 2, 2, 4]
                
                for i, (freq, duration) in enumerate(zip(melody, durations)):
                    # Show progress bar using scanline updates
                    progress = int((i / len(melody)) * 135)
                    
                    # Update just the progress bar scanline
                    progress_data = bytearray(135 * 2)
                    for x in range(135):
                        color = Colors.YELLOW if x < progress else Colors.BLACK
                        progress_data[x*2] = color & 0xFF
                        progress_data[x*2 + 1] = (color >> 8) & 0xFF
                    
                    display.set_window(0, 200, 135, 1)
                    display.write(progress_data)
                    
                    # Play note
                    if freq > 0:
                        buzzer.freq(freq)
                        buzzer.duty(100)
                    else:
                        buzzer.duty(0)
                    
                    time.sleep_ms(duration * 300)
                    buzzer.duty(0)
                    time.sleep_ms(50)
                
                print("Music finished!")
            
            # Success message overlay
            time.sleep(1)
            success_data = bytearray(85 * 40 * 2)  # Small overlay
            green565 = Colors.GREEN
            for i in range(0, len(success_data), 2):
                success_data[i] = green565 & 0xFF
                success_data[i + 1] = (green565 >> 8) & 0xFF
            
            display.set_window(25, 90, 85, 40)
            display.write(success_data)
            
            # Add text using framebuffer method
            display.text(30, 100, "SUCCESS!", Colors.WHITE, Colors.GREEN)
            display.text(25, 115, "SCANLINE", Colors.WHITE, Colors.GREEN)
            display.text(25, 125, "STREAMING!", Colors.WHITE, Colors.GREEN)
            
            # Update text overlay
            display.set_window(25, 90, 85, 40)
            for row in range(40):
                line_start = ((90 + row) * 135 + 25) * 2
                line_data = display.framebuffer[line_start:line_start + 85*2]
                display.set_window(25, 90 + row, 85, 1)
                display.write(line_data)
            
        else:
            raise Exception("Scanline streaming failed")
            
    except Exception as e:
        print(f"Error during scanline streaming: {e}")
        
        # Show error
        display.clear(Colors.RED)
        display.text(5, 80, "SCANLINE ERROR:", Colors.WHITE, Colors.RED)
        display.text(5, 100, str(e)[:20], Colors.WHITE, Colors.RED) 
        display.text(5, 120, "FILE NOT FOUND?", Colors.WHITE, Colors.RED)
        display.text(5, 140, "CHECK UPLOAD", Colors.WHITE, Colors.RED)
        display.show()
    
    finally:
        # Cleanup
        if buzzer:
            buzzer.duty(0)
        
        gc.collect()
        final_mem = gc.mem_free()
        print(f"Final memory: {final_mem} bytes")
        print("Scanline demo completed!")

if __name__ == "__main__":
    main()