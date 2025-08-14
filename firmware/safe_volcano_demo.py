"""
Memory-safe volcano demo for M5StickC Plus
Uses smaller images and proper memory management
"""

import time
import gc
from machine import Pin
from graphics import M5Display, Colors

class SafeVolcanoDemo:
    """Memory-safe volcano demo"""
    
    def __init__(self):
        print("Initializing Safe Volcano Demo...")
        
        # Force garbage collection
        gc.collect()
        print(f"Free memory: {gc.mem_free()} bytes")
        
        # Initialize display
        self.display = M5Display(brightness=True)
        
        # Try to load small volcano image
        try:
            from small_volcano_image import small_volcano, SMALL_WIDTH, SMALL_HEIGHT
            self.volcano_image = small_volcano
            self.image_width = SMALL_WIDTH
            self.image_height = SMALL_HEIGHT
            self.has_image = True
            print(f"Small volcano image loaded: {SMALL_WIDTH}x{SMALL_HEIGHT}")
            print(f"Image size: {len(small_volcano)} bytes")
        except ImportError as e:
            self.has_image = False
            print(f"Could not load volcano image: {e}")
        except MemoryError as e:
            self.has_image = False
            print(f"Not enough memory for image: {e}")
        
        # Initialize button
        self.button_a = Pin(37, Pin.IN, Pin.PULL_UP)
        
        # Force another garbage collection
        gc.collect()
        print(f"Free memory after init: {gc.mem_free()} bytes")
    
    def show_info_screen(self):
        """Show demo information"""
        self.display.clear(Colors.BLACK)
        
        # Title
        self.display.rect(0, 0, 135, 25, Colors.GREEN, filled=True)
        self.display.text(5, 8, "VOLCANO DEMO", Colors.WHITE, Colors.GREEN)
        
        # Memory info
        free_mem = gc.mem_free()
        self.display.text(5, 35, "MEMORY INFO:", Colors.WHITE)
        self.display.text(5, 55, f"FREE: {free_mem}", Colors.CYAN)
        
        # Image status
        if self.has_image:
            self.display.text(5, 75, "IMAGE: LOADED", Colors.GREEN)
            self.display.text(5, 95, f"SIZE: {self.image_width}X{self.image_height}", Colors.YELLOW)
        else:
            self.display.text(5, 75, "IMAGE: NONE", Colors.RED)
            self.display.text(5, 95, "USING SIMPLE", Colors.YELLOW)
        
        # Instructions
        self.display.rect(0, 120, 135, 60, Colors.BLUE, filled=True)
        self.display.text(5, 130, "PRESS BUTTON A", Colors.WHITE, Colors.BLUE)
        self.display.text(5, 145, "TO SHOW VOLCANO", Colors.WHITE, Colors.BLUE)
        self.display.text(5, 160, "RENDERING", Colors.WHITE, Colors.BLUE)
        
        # Footer
        self.display.rect(0, 200, 135, 40, Colors.PURPLE, filled=True)
        self.display.text(5, 210, "MEMORY SAFE", Colors.WHITE, Colors.PURPLE)
        self.display.text(5, 225, "VERSION", Colors.WHITE, Colors.PURPLE)
        
        self.display.show()
        
        # Wait for button press
        print("Waiting for button press...")
        while self.button_a.value() == 1:
            time.sleep_ms(50)
        
        # Debounce
        time.sleep_ms(200)
    
    def render_volcano(self):
        """Render volcano using available method"""
        print("Rendering volcano...")
        
        # Force garbage collection before rendering
        gc.collect()
        print(f"Free memory before render: {gc.mem_free()} bytes")
        
        if self.has_image:
            self.render_with_image()
        else:
            self.render_simple()
        
        # Force garbage collection after rendering
        gc.collect()
        print(f"Free memory after render: {gc.mem_free()} bytes")
    
    def render_with_image(self):
        """Render using bitmap image with scaling"""
        print("Rendering with bitmap image...")
        
        try:
            self.display.clear(Colors.BLACK)
            
            # Calculate position to center the image
            start_x = (135 - self.image_width) // 2
            start_y = (240 - self.image_height) // 2
            
            # Draw the small volcano image
            self.display.draw_bitmap(start_x, start_y, 
                                   self.image_width, self.image_height, 
                                   self.volcano_image)
            
            # Add title
            self.display.rect(0, 0, 135, 22, Colors.BLACK, filled=True)
            self.display.text(15, 5, "BITMAP VOLCANO", Colors.YELLOW)
            
            # Add info
            self.display.rect(0, 218, 135, 22, Colors.BLACK, filled=True)
            self.display.text(5, 222, f"{self.image_width}X{self.image_height} RGB565", Colors.CYAN)
            
            self.display.show()
            
        except MemoryError as e:
            print(f"Memory error during bitmap render: {e}")
            self.render_simple()
    
    def render_simple(self):
        """Simple volcano rendering for low memory"""
        print("Rendering simple volcano...")
        
        self.display.clear(Colors.BLACK)
        
        # Simple sky
        for y in range(0, 80, 4):  # Skip lines to save time
            self.display.line(0, y, 135, y, Colors.BLUE)
        
        # Simple mountain triangle
        peak_x = 67
        peak_y = 50
        base_y = 160
        
        # Draw mountain sides
        for y in range(peak_y, base_y, 2):
            width = (y - peak_y) * 2
            left_x = max(0, peak_x - width)
            right_x = min(135, peak_x + width)
            
            # Mountain color
            rock_color = Colors.GRAY
            if y < 100:
                rock_color = Colors.DARK_RED  # Lava area
            
            self.display.line(left_x, y, right_x, y, rock_color)
        
        # Simple ground
        for y in range(160, 240, 3):
            self.display.line(0, y, 135, y, Colors.DARK_GREEN)
        
        # Title
        self.display.rect(0, 0, 135, 22, Colors.BLACK, filled=True)
        self.display.text(20, 5, "SIMPLE VOLCANO", Colors.WHITE)
        
        # Info
        self.display.rect(0, 218, 135, 22, Colors.BLACK, filled=True)
        self.display.text(5, 222, "LOW MEMORY MODE", Colors.ORANGE)
        
        self.display.show()
    
    def show_completion(self):
        """Show completion message"""
        self.display.clear(Colors.BLACK)
        
        # Success
        self.display.rect(0, 0, 135, 240, Colors.GREEN, filled=True)
        
        self.display.text(20, 60, "DEMO", Colors.WHITE, Colors.GREEN)
        self.display.text(15, 80, "COMPLETE!", Colors.WHITE, Colors.GREEN)
        
        # Status
        if self.has_image:
            self.display.text(5, 120, "BITMAP RENDERING", Colors.WHITE, Colors.GREEN)
            self.display.text(15, 140, "SUCCESSFUL", Colors.WHITE, Colors.GREEN)
        else:
            self.display.text(5, 120, "SIMPLE RENDERING", Colors.WHITE, Colors.GREEN)
            self.display.text(15, 140, "SUCCESSFUL", Colors.WHITE, Colors.GREEN)
        
        # Memory status
        free_mem = gc.mem_free()
        self.display.text(5, 180, f"FINAL MEMORY:", Colors.WHITE, Colors.GREEN)
        self.display.text(5, 200, f"{free_mem} BYTES", Colors.WHITE, Colors.GREEN)
        
        self.display.show()
        time.sleep(3)
    
    def run(self):
        """Run the safe demo"""
        print("Starting Safe Volcano Demo!")
        
        try:
            # Show info
            self.show_info_screen()
            
            # Render volcano
            self.render_volcano()
            time.sleep(3)
            
            # Show completion
            self.show_completion()
            
            print("Safe demo completed successfully!")
            
        except Exception as e:
            print(f"Demo error: {e}")
            
            # Emergency simple display
            try:
                self.display.clear(Colors.RED)
                self.display.text(5, 100, "ERROR OCCURRED", Colors.WHITE, Colors.RED)
                self.display.text(5, 120, "CHECK CONSOLE", Colors.WHITE, Colors.RED)
                self.display.show()
            except:
                print("Could not display error on screen")
        
        finally:
            # Final cleanup
            gc.collect()
            print(f"Final free memory: {gc.mem_free()} bytes")

def main():
    """Main entry point"""
    demo = SafeVolcanoDemo()
    demo.run()

if __name__ == "__main__":
    main()