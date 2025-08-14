"""
Enhanced Volcano Demo with Image Rendering
Demonstrates the new bitmap image capabilities in the graphics library
"""

import time
import gc
from machine import Pin, PWM
from graphics import M5Display, Colors
from volcano_image import volcano_image, IMAGE_WIDTH, IMAGE_HEIGHT

class VolcanoImageDemo:
    """Enhanced volcano demo using actual image rendering"""
    
    def __init__(self):
        print("Initializing Volcano Image Demo...")
        
        # Initialize display
        self.display = M5Display(brightness=True)
        
        # Initialize buzzer for La Cucaracha
        try:
            self.buzzer = PWM(Pin(2), freq=440, duty=0)
            self.buzzer_available = True
            print("Buzzer initialized")
        except:
            self.buzzer = None
            self.buzzer_available = False
            print("Buzzer not available")
        
        # Initialize button
        self.button_a = Pin(37, Pin.IN, Pin.PULL_UP)
        
        # La Cucaracha melody
        self.la_cucaracha = [
            523, 523, 523, 659, 698, 698, 659, 659, 587, 587, 523, 0,
            523, 523, 523, 659, 698, 698, 659, 659, 587, 523
        ]
        
        self.note_durations = [
            2, 2, 2, 4, 4, 2, 2, 2, 2, 2, 4, 2,
            2, 2, 2, 4, 4, 2, 2, 2, 2, 4
        ]
        
        print("Volcano Image Demo ready!")
    
    def show_welcome_screen(self):
        """Show welcome screen explaining the demo"""
        self.display.clear(Colors.BLACK)
        
        # Title
        self.display.rect(0, 0, 135, 25, Colors.ORANGE, filled=True)
        self.display.text(10, 8, "IMAGE DEMO", Colors.WHITE, Colors.ORANGE)
        
        # Info
        self.display.text(5, 35, "ENHANCED VOLCANO", Colors.CYAN)
        self.display.text(5, 55, "WITH BITMAP", Colors.YELLOW)
        self.display.text(5, 75, "RENDERING!", Colors.GREEN)
        
        # Features
        self.display.text(5, 105, "FEATURES:", Colors.WHITE)
        self.display.text(5, 125, "* RGB565 IMAGES", Colors.PALE_GREEN)
        self.display.text(5, 145, "* LA CUCARACHA", Colors.PALE_GREEN)
        self.display.text(5, 165, "* TRANSITIONS", Colors.PALE_GREEN)
        
        # Instructions
        self.display.rect(0, 190, 135, 50, Colors.BLUE, filled=True)
        self.display.text(5, 200, "PRESS BUTTON A", Colors.WHITE, Colors.BLUE)
        self.display.text(5, 215, "TO START DEMO", Colors.WHITE, Colors.BLUE)
        
        self.display.show()
        
        # Wait for button press
        while self.button_a.value() == 1:
            time.sleep_ms(50)
        
        # Debounce
        time.sleep_ms(200)
    
    def show_image_with_transition(self):
        """Show volcano image with transition effect"""
        print("Rendering volcano image with transition...")
        
        # Clear screen
        self.display.clear(Colors.BLACK)
        
        # Transition effect - reveal image line by line
        for reveal_y in range(0, IMAGE_HEIGHT, 4):
            # Clear the display area for this section
            for y in range(reveal_y, min(reveal_y + 4, IMAGE_HEIGHT)):
                for x in range(IMAGE_WIDTH):
                    # Calculate pixel position in image data
                    pixel_index = (y * IMAGE_WIDTH + x) * 2
                    
                    # Extract RGB565 color (little endian)
                    low_byte = volcano_image[pixel_index]
                    high_byte = volcano_image[pixel_index + 1]
                    color = (high_byte << 8) | low_byte
                    
                    # Set pixel on display
                    self.display.pixel(x, y, color)
            
            # Show progressive reveal
            self.display.show()
            time.sleep_ms(50)  # Control speed of reveal
        
        # Add title overlay
        self.display.rect(0, 0, 135, 22, Colors.BLACK, filled=True)
        self.display.text(15, 5, "VOLCANO IMAGE", Colors.YELLOW)
        
        # Add status at bottom
        self.display.rect(0, 218, 135, 22, Colors.BLACK, filled=True)
        self.display.text(5, 222, "RGB565 BITMAP", Colors.CYAN)
        
        self.display.show()
    
    def show_image_with_bitmap_function(self):
        """Demonstrate using the draw_bitmap function"""
        print("Using draw_bitmap function...")
        
        # Clear and draw using bitmap function
        self.display.clear(Colors.BLACK)
        
        # Use the new draw_bitmap function
        self.display.draw_bitmap(0, 0, IMAGE_WIDTH, IMAGE_HEIGHT, volcano_image)
        
        # Add overlay text
        self.display.rect(0, 0, 135, 22, Colors.BLACK, filled=True)
        self.display.text(5, 5, "DRAW_BITMAP()", Colors.GREEN)
        
        self.display.rect(0, 218, 135, 22, Colors.BLACK, filled=True)
        self.display.text(15, 222, "NEW FUNCTION", Colors.ORANGE)
        
        self.display.show()
    
    def show_scaled_images(self):
        """Demonstrate image scaling"""
        print("Demonstrating image scaling...")
        
        # Create a smaller test image (32x32)
        small_width, small_height = 32, 32
        small_image = bytearray(small_width * small_height * 2)
        
        # Generate a simple pattern
        for y in range(small_height):
            for x in range(small_width):
                # Create a colorful gradient pattern
                r = int(255 * x / small_width)
                g = int(255 * y / small_height)
                b = 128
                
                # Convert to RGB565
                rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
                
                index = (y * small_width + x) * 2
                small_image[index] = rgb565 & 0xFF
                small_image[index + 1] = (rgb565 >> 8) & 0xFF
        
        # Clear screen
        self.display.clear(Colors.BLACK)
        
        # Title
        self.display.rect(0, 0, 135, 20, Colors.PURPLE, filled=True)
        self.display.text(20, 5, "SCALING DEMO", Colors.WHITE, Colors.PURPLE)
        
        # Show different scales
        self.display.text(5, 25, "1X:", Colors.WHITE)
        self.display.draw_bitmap(25, 25, small_width, small_height, small_image)
        
        self.display.text(5, 65, "2X:", Colors.WHITE)
        self.display.draw_bitmap_scaled(25, 65, small_width, small_height, small_image, 2, 2)
        
        # Note about scaling
        self.display.text(5, 200, "BITMAP SCALING", Colors.CYAN)
        self.display.text(5, 215, "DEMONSTRATION", Colors.CYAN)
        
        self.display.show()
        time.sleep(3)
    
    def play_la_cucaracha(self):
        """Play La Cucaracha with visual feedback"""
        if not self.buzzer_available:
            print("No buzzer available")
            return
        
        print("Playing La Cucaracha with visuals...")
        
        # Show music visualization
        for i, (freq, duration) in enumerate(zip(self.la_cucaracha, self.note_durations)):
            # Visual feedback
            note_height = int(freq / 20) if freq > 0 else 0
            note_color = Colors.YELLOW if freq > 0 else Colors.BLACK
            
            # Clear previous note visualization
            self.display.rect(100, 50, 30, 140, Colors.BLACK, filled=True)
            
            # Draw current note
            if note_height > 0:
                self.display.rect(105, 190 - note_height, 20, note_height, note_color, filled=True)
            
            # Show note info
            self.display.rect(0, 218, 135, 22, Colors.BLACK, filled=True)
            if freq > 0:
                self.display.text(5, 222, f"NOTE: {freq}HZ", Colors.WHITE)
            else:
                self.display.text(5, 222, "REST", Colors.WHITE)
            
            self.display.show()
            
            # Play note
            if freq > 0:
                self.buzzer.freq(freq)
                self.buzzer.duty(100)
            else:
                self.buzzer.duty(0)
            
            # Note duration
            note_time = duration * 300
            time.sleep_ms(note_time)
            
            # Small gap
            self.buzzer.duty(0)
            time.sleep_ms(50)
        
        # Stop buzzer
        self.buzzer.duty(0)
        print("Music finished!")
    
    def show_completion_screen(self):
        """Show completion screen"""
        self.display.clear(Colors.BLACK)
        
        # Success banner
        self.display.rect(0, 0, 135, 240, Colors.GREEN, filled=True)
        
        # Text
        self.display.text(15, 60, "IMAGE DEMO", Colors.WHITE, Colors.GREEN)
        self.display.text(20, 80, "COMPLETE!", Colors.WHITE, Colors.GREEN)
        
        self.display.text(5, 120, "GRAPHICS LIBRARY", Colors.WHITE, Colors.GREEN)
        self.display.text(5, 140, "NOW SUPPORTS:", Colors.WHITE, Colors.GREEN)
        self.display.text(5, 160, "* RGB565 IMAGES", Colors.WHITE, Colors.GREEN)
        self.display.text(5, 180, "* BITMAP SCALING", Colors.WHITE, Colors.GREEN)
        
        self.display.show()
        time.sleep(3)
    
    def run(self):
        """Run the complete demo"""
        print("Starting Enhanced Volcano Image Demo!")
        
        try:
            # Welcome screen
            self.show_welcome_screen()
            
            # Demo sequence
            self.show_image_with_transition()
            time.sleep(2)
            
            self.show_image_with_bitmap_function()
            time.sleep(2)
            
            self.show_scaled_images()
            
            # Play music with volcano background
            self.show_image_with_bitmap_function()
            self.play_la_cucaracha()
            
            # Completion
            self.show_completion_screen()
            
            print("Demo completed successfully!")
            
        except Exception as e:
            print(f"Demo error: {e}")
        finally:
            # Cleanup
            if self.buzzer:
                self.buzzer.duty(0)
            gc.collect()

def main():
    """Main entry point"""
    demo = VolcanoImageDemo()
    demo.run()

if __name__ == "__main__":
    main()