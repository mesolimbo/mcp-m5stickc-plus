"""
Working Volcano Demo - Efficient Image Loading
Uses optimized image format that actually works on MicroPython
"""

import time
import gc
from machine import Pin, PWM
from graphics import M5Display, Colors, rgb565

def main():
    print("Starting Working Volcano Demo!")
    
    # Initialize display
    display = M5Display(brightness=True)
    
    # Initialize button
    button_a = Pin(37, Pin.IN, Pin.PULL_UP)
    
    # Initialize buzzer
    try:
        buzzer = PWM(Pin(2), freq=440, duty=0)
        has_buzzer = True
    except:
        buzzer = None
        has_buzzer = False
    
    # Show welcome screen
    display.clear(Colors.BLACK)
    display.rect(0, 0, 135, 25, Colors.RED, filled=True)
    display.text(5, 8, "VOLCANO DEMO", Colors.WHITE, Colors.RED)
    
    display.text(5, 35, "EFFICIENT IMAGE", Colors.CYAN)
    display.text(5, 55, "135 X 240 RGB565", Colors.YELLOW)
    
    free_mem = gc.mem_free()
    display.text(5, 80, f"FREE: {free_mem}", Colors.GREEN)
    
    display.rect(0, 110, 135, 60, Colors.BLUE, filled=True)
    display.text(5, 120, "PRESS BUTTON A", Colors.WHITE, Colors.BLUE)
    display.text(5, 135, "TO LOAD IMAGE", Colors.WHITE, Colors.BLUE)
    display.text(5, 150, "AND PLAY MUSIC", Colors.WHITE, Colors.BLUE)
    
    display.show()
    
    print("Waiting for button press...")
    
    # Wait for button press
    while button_a.value() == 1:
        time.sleep_ms(50)
    
    print("Button pressed! Loading image...")
    
    # Try to load efficient image
    try:
        display.clear(Colors.BLACK)
        display.text(30, 110, "LOADING...", Colors.YELLOW)
        display.show()
        
        # Import and load the efficient image
        from efficient_volcano import get_volcano_data, WIDTH, HEIGHT
        
        print("Getting volcano data...")
        volcano_data = get_volcano_data()
        print(f"Loaded {len(volcano_data)} bytes")
        
        # Clear and render
        display.clear(Colors.BLACK)
        display.text(30, 110, "RENDERING...", Colors.CYAN)
        display.show()
        
        # Draw the image
        display.draw_bitmap(0, 0, WIDTH, HEIGHT, volcano_data)
        
        # Add overlay
        display.rect(0, 0, 135, 20, Colors.BLACK, filled=True)
        display.text(5, 5, "EFFICIENT VOLCANO", Colors.YELLOW)
        
        display.rect(0, 220, 135, 20, Colors.BLACK, filled=True)
        display.text(5, 225, "135X240 RGB565", Colors.CYAN)
        
        display.show()
        
        print("Image rendered successfully!")
        
        # Play La Cucaracha if buzzer available
        if has_buzzer:
            print("Playing La Cucaracha...")
            
            melody = [523, 523, 523, 659, 698, 698, 659, 659, 587, 587, 523, 0,
                     523, 523, 523, 659, 698, 698, 659, 659, 587, 523]
            durations = [2, 2, 2, 4, 4, 2, 2, 2, 2, 2, 4, 2,
                        2, 2, 2, 4, 4, 2, 2, 2, 2, 4]
            
            for freq, duration in zip(melody, durations):
                if freq > 0:
                    buzzer.freq(freq)
                    buzzer.duty(100)
                else:
                    buzzer.duty(0)
                
                time.sleep_ms(duration * 300)
                buzzer.duty(0)
                time.sleep_ms(50)
            
            print("Music finished!")
        
        # Success message
        time.sleep(1)
        display.rect(20, 90, 95, 60, Colors.GREEN, filled=True)
        display.text(25, 105, "SUCCESS!", Colors.WHITE, Colors.GREEN)
        display.text(25, 125, "EFFICIENT", Colors.WHITE, Colors.GREEN)
        display.text(25, 140, "IMAGE WORKS", Colors.WHITE, Colors.GREEN)
        display.show()
        
    except ImportError as e:
        print(f"Could not import image: {e}")
        show_error(display, "NO IMAGE FILE")
        
    except MemoryError as e:
        print(f"Memory error: {e}")
        show_error(display, "OUT OF MEMORY")
        
    except Exception as e:
        print(f"Error: {e}")
        show_error(display, "RENDER ERROR")
    
    finally:
        # Cleanup
        if buzzer:
            buzzer.duty(0)
        gc.collect()
        print(f"Final memory: {gc.mem_free()}")

def show_error(display, message):
    """Show error message"""
    display.clear(Colors.RED)
    display.text(5, 100, "ERROR:", Colors.WHITE, Colors.RED)
    display.text(5, 120, message, Colors.WHITE, Colors.RED)
    display.text(5, 140, "CHECK CONSOLE", Colors.WHITE, Colors.RED)
    display.show()

if __name__ == "__main__":
    main()