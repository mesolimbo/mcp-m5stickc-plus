"""
Enhanced demo for M5StickC PLUS with image display
Replaces dusk scene with volcano image and La Cucaracha music
"""

import time
import gc
import math
from machine import Pin, PWM
from graphics_enhanced import M5DisplayEnhanced, Colors, rgb565, hsv_to_rgb565, create_volcano_image

class DemoManagerEnhanced:
    """Enhanced demo manager with image support"""
    
    def __init__(self):
        print("Initializing Enhanced Demo Manager...")
        
        # Initialize display using enhanced graphics module
        self.display = M5DisplayEnhanced(brightness=True)
        
        # Initialize button
        self.button_a = Pin(37, Pin.IN, Pin.PULL_UP)
        self.button_pressed = False
        
        # Demo scenes list
        self.scenes = [
            WelcomeScene(self.display),
            ColorPaletteScene(self.display),
            ShapesScene(self.display),
            AnimationScene(self.display),
            InteractiveScene(self.display),
            RainbowScene(self.display),
            VolcanoScene(self.display),  # Replaces dusk scene
        ]
        
        self.current_scene = 0
        
        print(f"Enhanced Demo Manager ready with {len(self.scenes)} scenes!")
    
    def run(self):
        """Main demo loop"""
        print("Starting enhanced demo loop...")
        
        # Show first scene
        self.scenes[self.current_scene].render()
        
        while True:
            try:
                # Check button press
                if self.button_a.value() == 0 and not self.button_pressed:
                    self.button_pressed = True
                    self.next_scene()
                    
                elif self.button_a.value() == 1 and self.button_pressed:
                    self.button_pressed = False
                
                # Let current scene update if needed
                if hasattr(self.scenes[self.current_scene], 'update'):
                    self.scenes[self.current_scene].update()
                
                time.sleep_ms(50)
                
                # Periodic memory cleanup
                if time.ticks_ms() % 10000 < 50:
                    gc.collect()
                    
            except Exception as e:
                print(f"Demo error: {e}")
                time.sleep(1)
    
    def next_scene(self):
        """Switch to next demo scene"""
        self.current_scene = (self.current_scene + 1) % len(self.scenes)
        scene_name = self.scenes[self.current_scene].__class__.__name__
        print(f"Switching to scene {self.current_scene + 1}: {scene_name}")
        self.scenes[self.current_scene].render()


class DemoScene:
    """Base class for demo scenes"""
    
    def __init__(self, display):
        self.display = display
    
    def render(self):
        """Render the scene (override in subclasses)"""
        pass
    
    def update(self):
        """Update the scene (optional, for animated scenes)"""
        pass


class WelcomeScene(DemoScene):
    """Welcome/Hello World scene"""
    
    def render(self):
        print("Rendering: Welcome Scene")
        
        # Clear screen
        self.display.clear(Colors.BLACK)
        
        # Title bar
        self.display.rect(0, 0, 135, 25, Colors.BLUE, filled=True)
        self.display.text(5, 8, "ENHANCED DEMO", Colors.WHITE)
        
        # Main content
        self.display.text(5, 40, "M5STICKC PLUS", Colors.PALE_GREEN)
        self.display.text(15, 60, "MICROPYTHON", Colors.YELLOW)
        self.display.text(5, 80, "WITH IMAGES!", Colors.CYAN)
        
        # Features
        self.display.text(5, 110, "FEATURES:", Colors.WHITE)
        self.display.text(5, 130, "STRIP RENDERING", Colors.ORANGE)
        self.display.text(5, 150, "IMAGE DISPLAY", Colors.MAGENTA)
        
        # Instructions
        self.display.rect(0, 175, 135, 35, Colors.DARK_BLUE, filled=True)
        self.display.text(5, 185, "PRESS BUTTON A", Colors.WHITE)
        self.display.text(15, 200, "FOR NEXT DEMO", Colors.WHITE)
        
        # Footer
        self.display.rect(0, 220, 135, 20, Colors.GREEN, filled=True)
        self.display.text(25, 225, "ENHANCED!", Colors.WHITE)


class ColorPaletteScene(DemoScene):
    """Color showcase scene"""
    
    def render(self):
        print("Rendering: Color Palette Scene")
        
        self.display.clear(Colors.BLACK)
        
        # Title
        self.display.rect(0, 0, 135, 22, Colors.MAGENTA, filled=True)
        self.display.text(15, 7, "COLOR PALETTE", Colors.WHITE)
        
        # Primary colors
        colors = [
            ("RED", Colors.RED, 30),
            ("GREEN", Colors.GREEN, 45),
            ("BLUE", Colors.BLUE, 60),
            ("YELLOW", Colors.YELLOW, 75),
            ("CYAN", Colors.CYAN, 90),
            ("MAGENTA", Colors.MAGENTA, 105),
        ]
        
        for name, color, y in colors:
            self.display.text(5, y, name, Colors.WHITE)
            self.display.rect(50, y, 80, 12, color, filled=True)
        
        # Custom RGB colors
        self.display.text(5, 125, "CUSTOM RGB:", Colors.WHITE)
        
        # Create gradient
        for i in range(120):
            r = int(255 * (i / 120))
            g = int(255 * (1 - i / 120))
            b = 128
            color = rgb565(r, g, b)
            self.display.line(5 + i, 140, 5 + i, 150, color)
        
        # HSV rainbow
        self.display.text(5, 160, "HSV RAINBOW:", Colors.WHITE)
        for i in range(120):
            hue = i * 3  # 0 to 360 degrees
            color = hsv_to_rgb565(hue, 1.0, 1.0)
            self.display.line(5 + i, 175, 5 + i, 185, color)
        
        self.display.text(15, 200, "BEAUTIFUL!", Colors.PALE_GREEN)


class ShapesScene(DemoScene):
    """Geometric shapes demonstration"""
    
    def render(self):
        print("Rendering: Shapes Scene")
        
        self.display.clear(Colors.BLACK)
        
        # Title
        self.display.rect(0, 0, 135, 22, Colors.GREEN, filled=True)
        self.display.text(25, 7, "SHAPES DEMO", Colors.WHITE)
        
        # Rectangles
        self.display.text(5, 30, "RECTANGLES:", Colors.WHITE)
        self.display.rect(5, 45, 20, 15, Colors.RED, filled=True)
        self.display.rect(30, 45, 20, 15, Colors.YELLOW, filled=True)
        self.display.rect(55, 45, 20, 15, Colors.BLUE, filled=True)
        self.display.rect(80, 45, 20, 15, Colors.CYAN, filled=False)  # Outline
        self.display.rect(105, 45, 20, 15, Colors.MAGENTA, filled=False)  # Outline
        
        # Lines
        self.display.text(5, 70, "LINES:", Colors.WHITE)
        self.display.line(5, 85, 130, 85, Colors.WHITE)
        self.display.line(5, 90, 130, 100, Colors.RED)
        self.display.line(130, 90, 5, 100, Colors.BLUE)
        
        # Pattern
        self.display.text(5, 110, "PATTERN:", Colors.WHITE)
        for i in range(0, 60, 4):
            self.display.line(5 + i, 125, 5, 125 + i//2, Colors.ORANGE)
            self.display.line(70 + i//2, 125, 70, 125 + i, Colors.PURPLE)
        
        self.display.text(15, 180, "GEOMETRIC!", Colors.PALE_GREEN)


class AnimationScene(DemoScene):
    """Animation demonstration"""
    
    def render(self):
        print("Rendering: Animation Scene")
        
        # Clear and setup
        self.display.clear(Colors.BLACK)
        
        # Title
        self.display.rect(0, 0, 135, 22, Colors.CYAN, filled=True)
        self.display.text(20, 7, "ANIMATION!", Colors.BLACK)
        
        # Moving dot
        self.display.text(5, 30, "MOVING DOT:", Colors.WHITE)
        for x in range(0, 100, 3):
            # Clear previous
            if x > 0:
                self.display.rect(x - 3, 45, 8, 8, Colors.BLACK, filled=True)
            
            # Draw new
            self.display.rect(x, 45, 8, 8, Colors.RED, filled=True)
            time.sleep_ms(50)
        
        # Blinking text
        self.display.text(5, 80, "BLINKING:", Colors.WHITE)
        for i in range(8):
            if i % 2:
                self.display.rect(5, 95, 125, 15, Colors.MAGENTA, filled=True)
                self.display.text(25, 100, "FLASH!", Colors.WHITE)
            else:
                self.display.rect(5, 95, 125, 15, Colors.BLACK, filled=True)
            
            time.sleep_ms(300)
        
        # Final message
        self.display.rect(0, 140, 135, 30, Colors.GREEN, filled=True)
        self.display.text(10, 150, "ANIMATION", Colors.WHITE)
        self.display.text(20, 165, "COMPLETE!", Colors.WHITE)


class InteractiveScene(DemoScene):
    """Interactive demonstration with real-time feedback"""
    
    def render(self):
        print("Rendering: Interactive Scene")
        
        self.display.clear(Colors.BLACK)
        
        # Title
        self.display.rect(0, 0, 135, 22, Colors.YELLOW, filled=True)
        self.display.text(15, 7, "INTERACTIVE", Colors.BLACK)
        
        # Instructions
        self.display.text(5, 30, "PRESS BUTTON A", Colors.WHITE)
        self.display.text(5, 45, "TO CONTINUE!", Colors.WHITE)
        
        # Initialize button
        button_a = Pin(37, Pin.IN, Pin.PULL_UP)
        
        # Start interactive loop
        for count in range(100):
            # Clear dynamic area
            self.display.rect(5, 70, 125, 100, Colors.BLACK, filled=True)
            
            # Counter
            self.display.text(5, 70, f"COUNT: {count:03d}", Colors.CYAN)
            
            # Button status
            if button_a.value() == 0:  # Pressed
                self.display.rect(5, 90, 125, 15, Colors.RED, filled=True)
                self.display.text(5, 95, "BUTTON: PRESSED", Colors.WHITE)
            else:
                self.display.rect(5, 90, 125, 15, Colors.GREEN, filled=True)
                self.display.text(5, 95, "BUTTON: RELEASED", Colors.WHITE)
            
            # Progress bar
            progress = count
            self.display.text(5, 115, "PROGRESS:", Colors.WHITE)
            self.display.rect(5, 130, 100, 10, Colors.DARK_BLUE, filled=True)  # Background
            self.display.rect(5, 130, progress, 10, Colors.BLUE, filled=True)  # Progress
            self.display.text(110, 130, f"{progress}%", Colors.WHITE)
            
            time.sleep_ms(100)
            
            # Exit if button pressed
            if button_a.value() == 0:
                break
        
        # Completion message
        self.display.rect(0, 150, 135, 90, Colors.PURPLE, filled=True)
        self.display.text(10, 165, "INTERACTIVE", Colors.WHITE)
        self.display.text(20, 180, "COMPLETE!", Colors.WHITE)
        self.display.text(15, 200, "PRESS A TO", Colors.WHITE)
        self.display.text(20, 215, "CONTINUE", Colors.WHITE)


class RainbowScene(DemoScene):
    """Rainbow and gradient effects"""
    
    def render(self):
        print("Rendering: Rainbow Scene")
        
        self.display.clear(Colors.BLACK)
        
        # Title
        self.display.rect(0, 0, 135, 22, Colors.WHITE, filled=True)
        self.display.text(30, 7, "RAINBOW", Colors.BLACK)
        
        # HSV Rainbow bars
        self.display.text(5, 30, "HSV COLORS:", Colors.WHITE)
        
        # Horizontal rainbow stripes
        for y in range(50, 150, 10):
            for x in range(120):
                hue = x * 3  # 0 to 360 degrees
                color = hsv_to_rgb565(hue, 1.0, 1.0)
                self.display.line(5 + x, y, 5 + x, y + 8, color)
        
        # Gradient bars
        self.display.text(5, 160, "GRADIENTS:", Colors.WHITE)
        
        # Red to Blue gradient
        for x in range(120):
            r = int(255 * (1 - x / 120))
            b = int(255 * (x / 120))
            color = rgb565(r, 0, b)
            self.display.line(5 + x, 175, 5 + x, 185, color)
        
        # Green to Yellow gradient
        for x in range(120):
            g = 255
            r = int(255 * (x / 120))
            color = rgb565(r, g, 0)
            self.display.line(5 + x, 190, 5 + x, 200, color)
        
        self.display.text(20, 215, "COLORFUL!", Colors.PALE_GREEN)


class VolcanoScene(DemoScene):
    """Volcano image with La Cucaracha music"""
    
    def __init__(self, display):
        super().__init__(display)
        
        # Initialize buzzer for La Cucaracha
        try:
            self.buzzer = PWM(Pin(2), freq=440, duty=0)
            self.buzzer_available = True
            print("Buzzer initialized for volcano scene")
        except:
            self.buzzer = None
            self.buzzer_available = False
            print("Buzzer not available for volcano scene")
        
        # La Cucaracha melody (frequencies in Hz)
        # Classic Mexican folk song
        self.la_cucaracha = [
            523,  # C5
            523,  # C5
            523,  # C5
            659,  # E5
            698,  # F5
            698,  # F5
            659,  # E5
            659,  # E5
            587,  # D5
            587,  # D5
            523,  # C5
            523,  # C5 (pause)
            523,  # C5
            523,  # C5
            523,  # C5
            659,  # E5
            698,  # F5
            698,  # F5
            659,  # E5
            659,  # E5
            587,  # D5
            523,  # C5
        ]
        
        # Note durations (in 100ms units)
        self.note_durations = [
            2, 2, 2, 4, 4, 2, 2, 2, 2, 2, 4, 2,  # First part
            2, 2, 2, 4, 4, 2, 2, 2, 2, 4        # Second part
        ]
        
        self.melody_index = 0
        self.last_note_time = 0
    
    def render(self):
        """Render volcano image with La Cucaracha"""
        print("Rendering: Volcano Scene with La Cucaracha")
        
        # Show loading message
        self.display.clear(Colors.BLACK)
        self.display.text(25, 100, "LOADING", Colors.WHITE)
        self.display.text(25, 120, "VOLCANO...", Colors.WHITE)
        
        # Create volcano image
        print("Creating volcano image...")
        volcano_image = create_volcano_image()
        
        # Display the volcano image
        print("Displaying volcano image...")
        self.display.display_image(volcano_image, 0, 0, 135, 240)
        
        # Add title overlay
        self.display.rect(0, 0, 135, 25, Colors.BLACK, filled=True)
        self.display.text(15, 8, "VOLCANO VIEW", Colors.WHITE)
        
        # Add music indicator
        self.display.rect(0, 215, 135, 25, Colors.BLACK, filled=True)
        self.display.text(10, 220, "LA CUCARACHA", Colors.YELLOW)
        
        # Play La Cucaracha
        self.play_la_cucaracha()
        
        # Final message
        self.display.rect(20, 100, 95, 40, rgb565(0, 0, 0), filled=True)
        self.display.text(30, 110, "BEAUTIFUL", Colors.WHITE)
        self.display.text(30, 125, "VOLCANO!", Colors.WHITE)
    
    def play_la_cucaracha(self):
        """Play La Cucaracha melody"""
        if not self.buzzer_available:
            print("No buzzer available, skipping music")
            time.sleep(3)  # Just wait a bit instead
            return
        
        print("Playing La Cucaracha...")
        
        for i, (freq, duration) in enumerate(zip(self.la_cucaracha, self.note_durations)):
            # Play note
            self.buzzer.freq(freq)
            self.buzzer.duty(100)  # Medium volume
            
            # Note duration
            note_time = duration * 200  # 200ms per unit
            time.sleep_ms(note_time)
            
            # Small gap between notes
            self.buzzer.duty(0)
            time.sleep_ms(50)
        
        # Stop buzzer
        self.buzzer.duty(0)
        print("La Cucaracha finished!")


def main():
    """Main entry point"""
    print("Starting Enhanced Graphics Demo!")
    
    # Create and run enhanced demo manager
    demo_manager = DemoManagerEnhanced()
    demo_manager.run()


if __name__ == "__main__":
    main()