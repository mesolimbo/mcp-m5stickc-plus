"""
Demo scenes for M5StickC PLUS
Imports graphics module to render different demonstration pages
"""

import time
import gc
import math
import urandom
from machine import Pin, PWM
from graphics import M5Display, Colors, rgb565, hsv_to_rgb565

class DemoManager:
    """Manages demo scenes and navigation"""
    
    def __init__(self):
        print("Initializing Demo Manager...")
        
        # Initialize display using graphics module (no byte swapping for big-endian RGB565)
        self.display = M5Display(brightness=True, swap_bytes=False)
        
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
            VolcanoScene(self.display),
        ]
        
        self.current_scene = 0
        
        print(f"Demo Manager ready with {len(self.scenes)} scenes!")
    
    def run(self):
        """Main demo loop"""
        print("Starting demo loop...")
        
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
                
                time.sleep(0.05)
                
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
        self.display.text(10, 8, "MODULAR DEMO", Colors.WHITE, Colors.BLUE)
        
        # Main content
        self.display.text(5, 40, "M5STICKC PLUS", Colors.PALE_GREEN)
        self.display.text(15, 60, "MICROPYTHON", Colors.YELLOW)
        self.display.text(5, 80, "GRAPHICS MODULE", Colors.CYAN)
        
        # Module info
        self.display.text(5, 110, "USING IMPORTS:", Colors.WHITE)
        self.display.text(5, 130, "GRAPHICS.PY", Colors.ORANGE)
        self.display.text(5, 150, "DEMO.PY", Colors.MAGENTA)
        
        # Instructions
        self.display.rect(0, 175, 135, 35, Colors.DARK_BLUE, filled=True)
        self.display.text(5, 185, "PRESS BUTTON A", Colors.WHITE, Colors.DARK_BLUE)
        self.display.text(15, 200, "FOR NEXT DEMO", Colors.WHITE, Colors.DARK_BLUE)
        
        # Footer
        self.display.rect(0, 220, 135, 20, Colors.GREEN, filled=True)
        self.display.text(20, 225, "MODULAR!", Colors.WHITE, Colors.GREEN)
        
        self.display.show()


class ColorPaletteScene(DemoScene):
    """Color showcase scene"""
    
    def render(self):
        print("Rendering: Color Palette Scene")
        
        self.display.clear(Colors.BLACK)
        
        # Title
        self.display.rect(0, 0, 135, 22, Colors.MAGENTA, filled=True)
        self.display.text(15, 7, "COLOR PALETTE", Colors.WHITE, Colors.MAGENTA)
        
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
        
        self.display.show()


class ShapesScene(DemoScene):
    """Geometric shapes demonstration"""
    
    def render(self):
        print("Rendering: Shapes Scene")
        
        self.display.clear(Colors.BLACK)
        
        # Title
        self.display.rect(0, 0, 135, 22, Colors.GREEN, filled=True)
        self.display.text(25, 7, "SHAPES DEMO", Colors.WHITE, Colors.GREEN)
        
        # Rectangles
        self.display.text(5, 30, "RECTANGLES:", Colors.WHITE)
        self.display.rect(5, 45, 20, 15, Colors.RED, filled=True)
        self.display.rect(30, 45, 20, 15, Colors.YELLOW, filled=True)
        self.display.rect(55, 45, 20, 15, Colors.BLUE, filled=True)
        self.display.rect(80, 45, 20, 15, Colors.CYAN, filled=False)  # Outline
        self.display.rect(105, 45, 20, 15, Colors.MAGENTA, filled=False)  # Outline
        
        # Circles
        self.display.text(5, 70, "CIRCLES:", Colors.WHITE)
        self.display.circle(20, 90, 8, Colors.RED, filled=True)
        self.display.circle(40, 90, 8, Colors.GREEN, filled=True)
        self.display.circle(60, 90, 8, Colors.BLUE, filled=True)
        self.display.circle(80, 90, 8, Colors.YELLOW, filled=False)  # Outline
        self.display.circle(100, 90, 8, Colors.CYAN, filled=False)  # Outline
        
        # Lines
        self.display.text(5, 110, "LINES:", Colors.WHITE)
        self.display.line(5, 125, 50, 125, Colors.WHITE)  # Horizontal
        self.display.line(60, 125, 60, 145, Colors.RED)    # Vertical
        self.display.line(70, 125, 90, 145, Colors.GREEN)  # Diagonal
        self.display.line(100, 125, 120, 135, Colors.BLUE) # Slope
        
        # Pattern
        self.display.text(5, 155, "PATTERN:", Colors.WHITE)
        for i in range(0, 60, 4):
            self.display.line(5 + i, 170, 5, 170 + i//2, Colors.ORANGE)
            self.display.line(70 + i//2, 170, 70, 170 + i, Colors.PURPLE)
        
        self.display.text(15, 200, "GEOMETRIC!", Colors.PALE_GREEN)
        
        self.display.show()


class AnimationScene(DemoScene):
    """Animation demonstration"""
    
    def __init__(self, display):
        super().__init__(display)
        self.animation_step = 0
    
    def render(self):
        print("Rendering: Animation Scene")
        
        # Clear and setup
        self.display.clear(Colors.BLACK)
        
        # Title
        self.display.rect(0, 0, 135, 22, Colors.CYAN, filled=True)
        self.display.text(20, 7, "ANIMATION!", Colors.BLACK, Colors.CYAN)
        
        # Moving dot
        self.display.text(5, 30, "MOVING DOT:", Colors.WHITE)
        for x in range(0, 100, 3):
            # Clear previous
            if x > 0:
                self.display.rect(x - 3, 45, 8, 8, Colors.BLACK, filled=True)
            
            # Draw new
            self.display.rect(x, 45, 8, 8, Colors.RED, filled=True)
            self.display.show()
            time.sleep(0.05)
        
        # Expanding circles
        self.display.text(5, 70, "EXPANDING:", Colors.WHITE)
        for radius in range(1, 20):
            # Clear area
            self.display.rect(50, 80, 40, 40, Colors.BLACK, filled=True)
            
            # Draw circle
            self.display.circle(70, 100, radius, Colors.YELLOW, filled=False)
            self.display.show()
            time.sleep(0.1)
        
        # Blinking text
        self.display.text(5, 130, "BLINKING:", Colors.WHITE)
        for i in range(8):
            if i % 2:
                self.display.rect(5, 145, 125, 15, Colors.MAGENTA, filled=True)
                self.display.text(25, 150, "FLASH!", Colors.WHITE, Colors.MAGENTA)
            else:
                self.display.rect(5, 145, 125, 15, Colors.BLACK, filled=True)
            
            self.display.show()
            time.sleep(0.3)
        
        # Final message
        self.display.rect(0, 170, 135, 30, Colors.GREEN, filled=True)
        self.display.text(10, 180, "ANIMATION", Colors.WHITE, Colors.GREEN)
        self.display.text(20, 195, "COMPLETE!", Colors.WHITE, Colors.GREEN)
        self.display.show()


class InteractiveScene(DemoScene):
    """Interactive demonstration with real-time feedback"""
    
    def __init__(self, display):
        super().__init__(display)
        self.counter = 0
        self.button_a = Pin(37, Pin.IN, Pin.PULL_UP)
    
    def render(self):
        print("Rendering: Interactive Scene")
        
        self.display.clear(Colors.BLACK)
        
        # Title
        self.display.rect(0, 0, 135, 22, Colors.YELLOW, filled=True)
        self.display.text(15, 7, "INTERACTIVE", Colors.BLACK, Colors.YELLOW)
        
        # Instructions
        self.display.text(5, 30, "PRESS BUTTON A", Colors.WHITE)
        self.display.text(5, 45, "TO CONTINUE!", Colors.WHITE)
        
        # Start interactive loop
        for count in range(100):
            # Clear dynamic area
            self.display.rect(5, 70, 125, 100, Colors.BLACK, filled=True)
            
            # Counter
            self.display.text(5, 70, f"COUNT: {count:03d}", Colors.CYAN)
            
            # Button status
            if self.button_a.value() == 0:  # Pressed
                self.display.rect(5, 90, 125, 15, Colors.RED, filled=True)
                self.display.text(5, 95, "BUTTON: PRESSED", Colors.WHITE, Colors.RED)
            else:
                self.display.rect(5, 90, 125, 15, Colors.GREEN, filled=True)
                self.display.text(5, 95, "BUTTON: RELEASED", Colors.WHITE, Colors.GREEN)
            
            # Progress bar
            progress = count
            self.display.text(5, 115, "PROGRESS:", Colors.WHITE)
            self.display.rect(5, 130, 100, 10, Colors.DARK_BLUE, filled=True)  # Background
            self.display.rect(5, 130, progress, 10, Colors.BLUE, filled=True)  # Progress
            self.display.text(110, 130, f"{progress}%", Colors.WHITE)
            
            # Live update
            self.display.show()
            time.sleep(0.1)
            
            # Exit if button pressed
            if self.button_a.value() == 0:
                break
        
        # Completion
        self.display.rect(0, 150, 135, 90, Colors.PURPLE, filled=True)
        self.display.text(10, 165, "INTERACTIVE", Colors.WHITE, Colors.PURPLE)
        self.display.text(20, 180, "COMPLETE!", Colors.WHITE, Colors.PURPLE)
        self.display.text(15, 200, "PRESS A TO", Colors.WHITE, Colors.PURPLE)
        self.display.text(20, 215, "CONTINUE", Colors.WHITE, Colors.PURPLE)
        self.display.show()


class RainbowScene(DemoScene):
    """Rainbow and gradient effects"""
    
    def render(self):
        print("Rendering: Rainbow Scene")
        
        self.display.clear(Colors.BLACK)
        
        # Title
        self.display.rect(0, 0, 135, 22, Colors.WHITE, filled=True)
        self.display.text(30, 7, "RAINBOW", Colors.BLACK, Colors.WHITE)
        
        # HSV Rainbow spiral
        self.display.text(5, 30, "HSV SPIRAL:", Colors.WHITE)
        center_x, center_y = 67, 80
        for angle in range(0, 720, 5):  # Two full rotations
            import math
            radius = angle / 20
            hue = angle % 360
            
            x = int(center_x + radius * math.cos(math.radians(angle)))
            y = int(center_y + radius * math.sin(math.radians(angle)))
            
            color = hsv_to_rgb565(hue, 1.0, 1.0)
            if 0 <= x < 135 and 0 <= y < 240:
                self.display.pixel(x, y, color)
        
        # Gradient bars
        self.display.text(5, 130, "GRADIENTS:", Colors.WHITE)
        
        # Red to Blue gradient
        for x in range(120):
            r = int(255 * (1 - x / 120))
            b = int(255 * (x / 120))
            color = rgb565(r, 0, b)
            self.display.line(5 + x, 145, 5 + x, 155, color)
        
        # Green to Yellow gradient
        for x in range(120):
            g = 255
            r = int(255 * (x / 120))
            color = rgb565(r, g, 0)
            self.display.line(5 + x, 160, 5 + x, 170, color)
        
        # Circular rainbow
        self.display.text(5, 180, "CIRCLE:", Colors.WHITE)
        for angle in range(0, 360, 2):
            import math
            radius = 15
            hue = angle
            
            x = int(67 + radius * math.cos(math.radians(angle)))
            y = int(205 + radius * math.sin(math.radians(angle)))
            
            color = hsv_to_rgb565(hue, 1.0, 1.0)
            if 0 <= x < 135 and 0 <= y < 240:
                self.display.circle(x, y, 2, color, filled=True)
        
        self.display.show()


class VolcanoScene(DemoScene):
    """Volcano scene with La Cucaracha music and RGB565 scanline streaming"""
    
    def __init__(self, display):
        super().__init__(display)
        
        # Check for RGB565 portrait volcano file
        self.volcano_file = '/volcano-portrait.rgb565'
        self.has_image = self._check_volcano_file()
        if self.has_image:
            print("RGB565 portrait volcano available for scanline streaming")
        else:
            print("No volcano file found, using procedural rendering")
        
        # Initialize buzzer for La Cucaracha
        try:
            self.buzzer = PWM(Pin(2), freq=440, duty=0)
            self.buzzer_available = True
            print("Buzzer initialized for volcano scene")
        except:
            self.buzzer = None
            self.buzzer_available = False
            print("Buzzer not available for volcano scene")
    
    def _check_volcano_file(self):
        """Check if volcano RGB565 file exists"""
        try:
            with open(self.volcano_file, 'rb') as f:
                # Just check if file exists and has correct size
                f.seek(0, 2)  # Seek to end
                size = f.tell()
                expected_size = 135 * 240 * 2  # RGB565 format
                return size == expected_size
        except:
            return False
        
        # La Cucaracha melody (frequencies in Hz)
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
            0,    # Rest
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
        
        # Note durations (in 200ms units)
        self.note_durations = [
            2, 2, 2, 4, 4, 2, 2, 2, 2, 2, 4, 2,  # First part
            2, 2, 2, 4, 4, 2, 2, 2, 2, 4        # Second part
        ]
    
    def render(self):
        """Render volcano scene with La Cucaracha"""
        print("Rendering: Volcano Scene")
        
        if self.has_image:
            # Use RGB565 scanline streaming
            print("Using RGB565 scanline streaming")
            self.display.clear(Colors.BLACK)
            
            # Show loading message briefly
            self.display.rect(30, 110, 75, 20, Colors.BLUE, filled=True)
            self.display.text(35, 115, "LOADING...", Colors.WHITE, Colors.BLUE)
            self.display.show()
            time.sleep(0.5)
            
            # Stream the portrait volcano image
            success = self.display.draw_rgb565_file(self.volcano_file)
            
            if success:
                print("Portrait volcano streamed successfully!")
                
                # DON'T call display.show() or any other display operations
                # The image is already on screen from scanline streaming
                # Any additional writes could overwrite the streamed image
                
                # Immediate delay to prevent any system interference
                time.sleep(2)
                print("Volcano should be visible now...")
            else:
                print("Failed to stream volcano image")
                # Fall through to procedural rendering
            
        else:
            # Fallback to procedural rendering
            print("Using procedural volcano rendering")
            self.display.clear(Colors.BLACK)
            
            # Draw sky gradient
            for y in range(60):
                blue_intensity = 100 + int(100 * (60 - y) / 60)
                sky_color = rgb565(50, 100, min(255, blue_intensity))
                self.display.line(0, y, 135, y, sky_color)
            
            # Draw volcano mountain
            peak_x = 67
            for y in range(60, 180):
                for x in range(135):
                    dist_from_peak = abs(x - peak_x)
                    mountain_width = (y - 60) * 0.8
                    
                    if dist_from_peak < mountain_width:
                        if y < 120 and dist_from_peak < 15:
                            # Lava area
                            lava_intensity = 255 - int(dist_from_peak * 8)
                            volcano_color = rgb565(lava_intensity, lava_intensity // 3, 0)
                        else:
                            # Mountain slopes
                            rock_intensity = 60 + int((180 - y) / 4)
                            volcano_color = rgb565(rock_intensity, rock_intensity - 10, rock_intensity - 20)
                        
                        self.display.pixel(x, y, volcano_color)
                    else:
                        # Sky continuation
                        blue_intensity = 100 + int(50 * (180 - y) / 120)
                        sky_color = rgb565(80, 120, min(255, blue_intensity))
                        self.display.pixel(x, y, sky_color)
            
            # Draw foreground vegetation
            for y in range(180, 240):
                for x in range(135):
                    green_base = 80 + int((x + y) % 30)
                    vegetation_color = rgb565(20, green_base, 30)
                    self.display.pixel(x, y, vegetation_color)
            
            # Add title
            self.display.rect(0, 0, 135, 20, Colors.BLACK, filled=True)
            self.display.text(20, 5, "PROCEDURAL", Colors.WHITE)
            
            # Add music title
            self.display.rect(0, 220, 135, 20, Colors.BLACK, filled=True)
            self.display.text(10, 225, "LA CUCARACHA", Colors.YELLOW)
        
        # Show the volcano scene and play music
        self.display.show()
        time.sleep(2)
        self.play_la_cucaracha()
        
        # Extended display time for volcano viewing
        if self.has_image:
            print("Volcano on display for 60 seconds...")
            time.sleep(60)  # Full 60 seconds as requested
        
        # Clear screen completely before exit
        self.display.clear(Colors.BLACK)
        
        # Simple completion message
        self.display.rect(30, 110, 75, 30, Colors.GREEN, filled=True)
        self.display.text(35, 118, "VOLCANO", Colors.WHITE, Colors.GREEN)
        self.display.text(35, 128, "DONE!", Colors.WHITE, Colors.GREEN)
        self.display.show()
        
        time.sleep(1)
    
    def play_la_cucaracha(self):
        """Play La Cucaracha melody"""
        if not self.buzzer_available:
            print("No buzzer available for La Cucaracha")
            time.sleep(3)
            return
        
        print("Playing La Cucaracha...")
        
        for i, (freq, duration) in enumerate(zip(self.la_cucaracha, self.note_durations)):
            if freq > 0:  # Play note
                self.buzzer.freq(freq)
                self.buzzer.duty(100)  # Medium volume
            else:  # Rest
                self.buzzer.duty(0)
            
            # Note duration
            note_time = duration * 0.3  # 300ms per unit converted to seconds
            time.sleep(note_time)
            
            # Small gap between notes
            self.buzzer.duty(0)
            time.sleep(0.05)  # 50ms converted to seconds
        
        # Stop buzzer
        self.buzzer.duty(0)
        print("La Cucaracha finished!")


def main():
    """Main entry point"""
    print("Starting Modular Graphics Demo!")
    
    # Create and run demo manager
    demo_manager = DemoManager()
    demo_manager.run()


if __name__ == "__main__":
    main()