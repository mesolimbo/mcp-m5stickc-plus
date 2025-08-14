"""
Proper Volcano Demo - Full Size Image Rendering
Matches the C++ library approach with full 135x240 images
"""

import time
import gc
from machine import Pin, PWM
from graphics import M5Display, Colors, rgb565

class ProperVolcanoDemo:
    """Proper volcano demo with full-size image like C++ library"""
    
    def __init__(self):
        print("Initializing Proper Volcano Demo...")
        
        # Initialize display
        self.display = M5Display(brightness=True)
        
        # Initialize button
        self.button_a = Pin(37, Pin.IN, Pin.PULL_UP)
        
        # Initialize buzzer for La Cucaracha
        try:
            self.buzzer = PWM(Pin(2), freq=440, duty=0)
            self.buzzer_available = True
            print("Buzzer initialized")
        except:
            self.buzzer = None
            self.buzzer_available = False
            print("Buzzer not available")
        
        # La Cucaracha melody
        self.la_cucaracha = [
            523, 523, 523, 659, 698, 698, 659, 659, 587, 587, 523, 0,
            523, 523, 523, 659, 698, 698, 659, 659, 587, 523
        ]
        
        self.note_durations = [
            2, 2, 2, 4, 4, 2, 2, 2, 2, 2, 4, 2,
            2, 2, 2, 4, 4, 2, 2, 2, 2, 4
        ]
        
        print("Proper Volcano Demo ready!")
    
    def load_volcano_image(self):
        """Load volcano image data when needed"""
        try:
            print("Loading full volcano image...")
            from volcano_full_image import get_volcano_image, VOLCANO_WIDTH, VOLCANO_HEIGHT
            
            # Load image data
            volcano_data = get_volcano_image()
            print(f"Loaded {len(volcano_data)} bytes of image data")
            
            return volcano_data, VOLCANO_WIDTH, VOLCANO_HEIGHT, True
            
        except ImportError as e:
            print(f"Volcano image module not found: {e}")
            return None, 135, 240, False
        except MemoryError as e:
            print(f"Not enough memory for full image: {e}")
            return None, 135, 240, False
        except Exception as e:
            print(f"Error loading volcano image: {e}")
            return None, 135, 240, False
    
    def show_welcome_screen(self):
        """Show welcome screen"""
        self.display.clear(Colors.BLACK)
        
        # Title bar
        self.display.rect(0, 0, 135, 25, Colors.RED, filled=True)
        self.display.text(5, 8, "VOLCANO DEMO", Colors.WHITE, Colors.RED)
        
        # Info
        self.display.text(5, 35, "FULL SIZE IMAGE", Colors.CYAN)
        self.display.text(5, 55, "135 X 240 PIXELS", Colors.YELLOW)
        self.display.text(5, 75, "RGB565 FORMAT", Colors.GREEN)
        
        # Memory status
        free_mem = gc.mem_free()
        self.display.text(5, 105, "FREE MEMORY:", Colors.WHITE)
        self.display.text(5, 125, f"{free_mem} BYTES", Colors.PALE_GREEN)
        
        # Instructions
        self.display.rect(0, 150, 135, 50, Colors.BLUE, filled=True)
        self.display.text(5, 160, "PRESS BUTTON A", Colors.WHITE, Colors.BLUE)
        self.display.text(5, 175, "TO LOAD AND", Colors.WHITE, Colors.BLUE)
        self.display.text(5, 190, "DISPLAY IMAGE", Colors.WHITE, Colors.BLUE)
        
        # Footer
        self.display.rect(0, 220, 135, 20, Colors.PURPLE, filled=True)
        self.display.text(15, 225, "LIKE C++ LIB", Colors.WHITE, Colors.PURPLE)
        
        self.display.show()
        
        # Wait for button press
        print("Waiting for button press...")
        while self.button_a.value() == 1:
            time.sleep_ms(50)
        
        # Debounce
        time.sleep_ms(200)
    
    def render_volcano_image(self, volcano_data, width, height):
        """Render the full volcano image"""
        print("Rendering full volcano image...")
        
        # Clear screen
        self.display.clear(Colors.BLACK)
        
        # Show loading message
        self.display.text(30, 110, "RENDERING...", Colors.YELLOW)
        self.display.show()
        
        # Force garbage collection before rendering
        gc.collect()
        print(f"Free memory before render: {gc.mem_free()} bytes")
        
        try:
            # Use the draw_bitmap function to render the full image
            self.display.draw_bitmap(0, 0, width, height, volcano_data)
            
            # Add overlay title
            self.display.rect(0, 0, 135, 20, Colors.BLACK, filled=True)
            self.display.text(10, 5, "FULL VOLCANO", Colors.YELLOW)
            
            # Add info at bottom
            self.display.rect(0, 220, 135, 20, Colors.BLACK, filled=True)
            self.display.text(5, 225, "135X240 RGB565", Colors.CYAN)
            
            self.display.show()
            print("Full volcano image rendered successfully!")
            
            return True
            
        except Exception as e:
            print(f"Error rendering volcano: {e}")
            
            # Show error
            self.display.clear(Colors.RED)
            self.display.text(5, 100, "RENDER ERROR:", Colors.WHITE, Colors.RED)
            self.display.text(5, 120, str(e)[:20], Colors.WHITE, Colors.RED)
            self.display.show()
            
            return False
    
    def render_fallback_volcano(self):
        """Fallback volcano rendering"""
        print("Rendering fallback volcano...")
        
        self.display.clear(Colors.BLACK)
        
        # Enhanced procedural volcano
        # Sky
        for y in range(0, 80, 2):
            blue = 100 + int(100 * (80 - y) / 80)
            sky_color = rgb565(60, 120, min(255, blue))
            self.display.line(0, y, 135, y, sky_color)
        
        # Mountain
        peak_x = 67
        for y in range(80, 200):
            for x in range(0, 135, 2):  # Skip pixels for speed
                dist = abs(x - peak_x)
                width = (y - 80) * 0.8
                
                if dist < width:
                    if y < 130 and dist < 15:
                        # Lava
                        intensity = 255 - int(dist * 8)
                        color = rgb565(intensity, intensity // 3, 0)
                    else:
                        # Rock
                        rock = 60 + int((200 - y) / 4)
                        color = rgb565(rock, rock - 10, rock - 20)
                    
                    self.display.pixel(x, y, color)
        
        # Vegetation
        for y in range(200, 240, 2):
            for x in range(0, 135, 2):
                green = 80 + int((x + y) % 30)
                color = rgb565(20, green, 30)
                self.display.pixel(x, y, color)
        
        # Title
        self.display.rect(0, 0, 135, 20, Colors.BLACK, filled=True)
        self.display.text(15, 5, "FALLBACK", Colors.WHITE)
        
        self.display.show()
    
    def play_la_cucaracha(self):
        """Play La Cucaracha melody"""
        if not self.buzzer_available:
            print("No buzzer available")
            time.sleep(3)
            return
        
        print("Playing La Cucaracha...")
        
        for i, (freq, duration) in enumerate(zip(self.la_cucaracha, self.note_durations)):
            # Show progress
            progress = int((i / len(self.la_cucaracha)) * 120)
            self.display.rect(5, 210, 125, 8, Colors.BLACK, filled=True)
            self.display.rect(5, 210, progress, 8, Colors.YELLOW, filled=True)
            self.display.show()
            
            # Play note
            if freq > 0:
                self.buzzer.freq(freq)
                self.buzzer.duty(100)
            else:
                self.buzzer.duty(0)
            
            time.sleep_ms(duration * 300)
            
            # Gap between notes
            self.buzzer.duty(0)
            time.sleep_ms(50)
        
        # Stop buzzer
        self.buzzer.duty(0)
        print("Music finished!")
    
    def show_completion(self):
        """Show completion screen"""
        self.display.clear(Colors.GREEN)
        
        self.display.text(25, 80, "VOLCANO", Colors.WHITE, Colors.GREEN)
        self.display.text(15, 100, "DEMO COMPLETE", Colors.WHITE, Colors.GREEN)
        
        self.display.text(5, 130, "FULL SIZE IMAGE", Colors.WHITE, Colors.GREEN)
        self.display.text(5, 150, "RENDERING WORKS", Colors.WHITE, Colors.GREEN)
        
        self.display.text(5, 180, "LIKE C++ LIBRARY", Colors.WHITE, Colors.GREEN)
        
        self.display.show()
        time.sleep(3)
    
    def run(self):
        """Run the complete demo"""
        print("Starting Proper Volcano Demo!")
        
        try:
            # Welcome screen
            self.show_welcome_screen()
            
            # Try to load and render full image
            volcano_data, width, height, has_image = self.load_volcano_image()
            
            if has_image and volcano_data:
                # Render full image
                success = self.render_volcano_image(volcano_data, width, height)
                
                if success:
                    # Play music with image displayed
                    time.sleep(2)
                    self.play_la_cucaracha()
                else:
                    # Fallback if rendering failed
                    self.render_fallback_volcano()
                    time.sleep(2)
            else:
                # No image available, use fallback
                self.render_fallback_volcano()
                time.sleep(2)
            
            # Completion
            self.show_completion()
            
            print("Proper volcano demo completed!")
            
        except Exception as e:
            print(f"Demo error: {e}")
            
            # Emergency display
            try:
                self.display.clear(Colors.RED)
                self.display.text(5, 100, "DEMO ERROR", Colors.WHITE, Colors.RED)
                self.display.text(5, 120, "CHECK CONSOLE", Colors.WHITE, Colors.RED)
                self.display.show()
            except:
                pass
        
        finally:
            # Cleanup
            if self.buzzer:
                self.buzzer.duty(0)
            gc.collect()
            print(f"Final free memory: {gc.mem_free()} bytes")

def main():
    """Main entry point"""
    demo = ProperVolcanoDemo()
    demo.run()

if __name__ == "__main__":
    main()