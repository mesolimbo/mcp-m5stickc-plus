"""
Memory-efficient demo for M5StickC PLUS
Uses lite graphics module to avoid memory issues
"""

import time
import gc
from machine import Pin, PWM
from graphics_lite import M5DisplayLite, Colors, rgb565

class DemoManagerLite:
    """Lightweight demo manager"""
    
    def __init__(self):
        print("Initializing Lite Demo Manager...")
        
        # Initialize display using lite graphics module
        self.display = M5DisplayLite(brightness=True)
        
        # Initialize button
        self.button_a = Pin(37, Pin.IN, Pin.PULL_UP)
        self.button_pressed = False
        
        # Demo scenes list
        self.demos = [
            self.demo_hello,
            self.demo_colors,
            self.demo_shapes,
            self.demo_dusk_sky
        ]
        
        self.demo_names = [
            "Hello World",
            "Colors",
            "Shapes",
            "Dusk Sky"
        ]
        
        self.current_demo = 0
        
        print(f"Lite Demo Manager ready with {len(self.demos)} demos!")
    
    def run(self):
        """Main demo loop"""
        print("Starting lite demo loop...")
        
        # Show first demo
        self.demos[self.current_demo]()
        
        while True:
            try:
                # Check button press
                if self.button_a.value() == 0 and not self.button_pressed:
                    self.button_pressed = True
                    self.next_demo()
                    
                elif self.button_a.value() == 1 and self.button_pressed:
                    self.button_pressed = False
                
                time.sleep_ms(50)
                
                # Periodic memory cleanup
                if time.ticks_ms() % 5000 < 50:
                    gc.collect()
                    
            except Exception as e:
                print(f"Demo error: {e}")
                time.sleep(1)
    
    def next_demo(self):
        """Switch to next demo"""
        self.current_demo = (self.current_demo + 1) % len(self.demos)
        demo_name = self.demo_names[self.current_demo]
        print(f"Demo {self.current_demo + 1}: {demo_name}")
        self.demos[self.current_demo]()
    
    def demo_hello(self):
        """Hello World demo"""
        print("Demo: Hello World")
        
        self.display.clear(Colors.BLACK)
        
        # Title bar
        self.display.rect(0, 0, 135, 25, Colors.BLUE, filled=True)
        self.display.text(15, 8, "HELLO WORLD!", Colors.WHITE)
        
        # Main content
        self.display.text(10, 40, "M5STICKC PLUS", Colors.PALE_GREEN)
        self.display.text(20, 60, "MICROPYTHON", Colors.YELLOW)
        self.display.text(5, 80, "LITE GRAPHICS", Colors.CYAN)
        
        # Info
        self.display.text(5, 110, "MEMORY SAFE", Colors.WHITE)
        self.display.text(5, 130, "NO FRAMEBUFFER", Colors.ORANGE)
        
        # Instructions
        self.display.rect(0, 160, 135, 35, Colors.DARK_BLUE, filled=True)
        self.display.text(5, 170, "PRESS BUTTON A", Colors.WHITE)
        self.display.text(15, 185, "FOR NEXT DEMO", Colors.WHITE)
        
        # Footer
        self.display.rect(0, 215, 135, 25, Colors.GREEN, filled=True)
        self.display.text(35, 222, "WORKING!", Colors.WHITE)
    
    def demo_colors(self):
        """Color demo"""
        print("Demo: Colors")
        
        self.display.clear(Colors.BLACK)
        
        # Title
        self.display.rect(0, 0, 135, 22, Colors.MAGENTA, filled=True)
        self.display.text(25, 7, "COLORS", Colors.WHITE)
        
        # Color bars
        colors = [
            ("RED", Colors.RED, 30),
            ("GREEN", Colors.GREEN, 45),
            ("BLUE", Colors.BLUE, 60),
            ("YELLOW", Colors.YELLOW, 75),
            ("CYAN", Colors.CYAN, 90),
            ("WHITE", Colors.WHITE, 105)
        ]
        
        for name, color, y in colors:
            self.display.text(5, y, name, Colors.WHITE)
            self.display.rect(50, y, 80, 12, color, filled=True)
        
        # Custom colors
        self.display.text(5, 125, "CUSTOM:", Colors.WHITE)
        
        # Simple gradient using rectangles
        for i in range(10):
            r = int(255 * (i / 9))
            g = int(255 * (1 - i / 9))
            color = rgb565(r, g, 128)
            self.display.rect(5 + i * 12, 140, 12, 15, color, filled=True)
        
        self.display.text(20, 165, "BEAUTIFUL!", Colors.PALE_GREEN)
    
    def demo_shapes(self):
        """Shapes demo"""
        print("Demo: Shapes")
        
        self.display.clear(Colors.BLACK)
        
        # Title
        self.display.rect(0, 0, 135, 22, Colors.GREEN, filled=True)
        self.display.text(35, 7, "SHAPES", Colors.WHITE)
        
        # Rectangles
        self.display.text(5, 30, "RECTANGLES:", Colors.WHITE)
        self.display.rect(5, 45, 20, 15, Colors.RED, filled=True)
        self.display.rect(30, 45, 20, 15, Colors.YELLOW, filled=True)
        self.display.rect(55, 45, 20, 15, Colors.BLUE, filled=True)
        self.display.rect(80, 45, 20, 15, Colors.CYAN, filled=False)
        self.display.rect(105, 45, 20, 15, Colors.MAGENTA, filled=False)
        
        # Lines
        self.display.text(5, 70, "LINES:", Colors.WHITE)
        self.display.line(5, 85, 130, 85, Colors.WHITE)
        self.display.line(5, 90, 130, 100, Colors.RED)
        self.display.line(130, 90, 5, 100, Colors.BLUE)
        
        # Pattern
        self.display.text(5, 110, "PATTERN:", Colors.WHITE)
        for i in range(0, 60, 4):
            self.display.line(5 + i, 125, 5, 125 + i//2, Colors.ORANGE)
        
        for i in range(0, 40, 3):
            self.display.line(70, 125 + i, 70 + i, 125, Colors.PURPLE)
        
        self.display.text(15, 180, "GEOMETRIC!", Colors.PALE_GREEN)
    
    def demo_dusk_sky(self):
        """Peaceful dusk sky with music"""
        print("Demo: Dusk Sky")
        
        # Initialize buzzer
        try:
            buzzer = PWM(Pin(2), freq=440, duty=0)
            buzzer_ok = True
        except:
            buzzer = None
            buzzer_ok = False
        
        # Create sky gradient using horizontal lines
        for y in range(25, 200):
            gradient_pos = (y - 25) / 175.0
            
            if gradient_pos < 0.4:
                # Upper sky: deep blue to purple
                r = int(20 + gradient_pos * 80)
                g = int(10 + gradient_pos * 40)
                b = int(80 + gradient_pos * 80)
            elif gradient_pos < 0.7:
                # Mid sky: purple to pink
                local_pos = (gradient_pos - 0.4) / 0.3
                r = int(100 + local_pos * 80)
                g = int(50 + local_pos * 60)
                b = int(160 - local_pos * 80)
            else:
                # Lower sky: pink to orange
                local_pos = (gradient_pos - 0.7) / 0.3
                r = int(180 + local_pos * 50)
                g = int(110 - local_pos * 30)
                b = int(80 - local_pos * 50)
            
            # Clamp values
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            
            color = rgb565(r, g, b)
            self.display.line(0, y, 135, y, color)
        
        # Title
        self.display.text(25, 5, "PEACEFUL DUSK", Colors.WHITE)
        
        # Horizon
        self.display.line(0, 200, 135, 200, rgb565(100, 50, 20))
        
        # Ground
        self.display.rect(0, 201, 135, 39, rgb565(40, 25, 10), filled=True)
        
        # Simple stars (fixed positions for memory efficiency)
        stars = [
            (20, 50), (45, 35), (70, 60), (95, 40), (110, 55),
            (15, 80), (35, 75), (60, 85), (85, 70), (120, 90),
            (25, 110), (50, 105), (80, 120), (100, 115), (125, 130),
            (10, 140), (40, 135), (65, 150), (90, 145), (115, 160)
        ]
        
        # Music notes (C major scale)
        melody = [523, 587, 659, 698, 784, 880, 987, 1047]
        note_index = 0
        
        # Animation loop
        for frame in range(100):  # 10 seconds at 100ms per frame
            # Animate stars (simple twinkling)
            for i, (x, y) in enumerate(stars):
                if (frame + i * 7) % 20 < 10:  # Each star blinks at different time
                    brightness = 255
                else:
                    brightness = 100
                
                star_color = rgb565(brightness, brightness, brightness - 20)
                self.display.pixel(x, y, star_color)
                
                # Bright stars get a cross pattern
                if brightness > 200 and (frame + i * 7) % 20 < 5:
                    if x > 0:
                        self.display.pixel(x - 1, y, star_color)
                    if x < 134:
                        self.display.pixel(x + 1, y, star_color)
                    if y > 25:
                        self.display.pixel(x, y - 1, star_color)
                    if y < 199:
                        self.display.pixel(x, y + 1, star_color)
            
            # Play soft music
            if buzzer_ok and frame % 15 == 0:  # New note every 1.5 seconds
                buzzer.duty(0)  # Stop previous note
                time.sleep_ms(50)
                
                # Play next note
                buzzer.freq(melody[note_index])
                buzzer.duty(30)  # Soft volume
                note_index = (note_index + 1) % len(melody)
            
            time.sleep_ms(100)
        
        # Stop music
        if buzzer_ok:
            buzzer.duty(0)
        
        # Final message
        self.display.rect(20, 100, 95, 40, rgb565(30, 30, 60), filled=True)
        self.display.text(25, 110, "PEACEFUL", Colors.WHITE)
        self.display.text(35, 125, "NIGHT", Colors.WHITE)


def main():
    """Main entry point"""
    print("Starting Lite Graphics Demo!")
    
    # Create and run lite demo manager
    demo_manager = DemoManagerLite()
    demo_manager.run()


if __name__ == "__main__":
    main()