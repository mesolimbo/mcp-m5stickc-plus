#!/usr/bin/env python3
"""
Simple image to RGB565 converter using only built-in Python libraries
Demonstrates the concept - in practice you'd use proper image tools
"""

def create_sample_volcano_image():
    """Create a simple volcano bitmap using procedural generation"""
    width, height = 135, 240
    
    # Create RGB565 bitmap data
    bitmap_data = bytearray(width * height * 2)
    
    def rgb_to_rgb565(r, g, b):
        """Convert RGB888 to RGB565"""
        r = (r >> 3) & 0x1F
        g = (g >> 2) & 0x3F  
        b = (b >> 3) & 0x1F
        return (r << 11) | (g << 5) | b
    
    def set_pixel(x, y, r, g, b):
        """Set pixel in bitmap"""
        if 0 <= x < width and 0 <= y < height:
            rgb565 = rgb_to_rgb565(r, g, b)
            index = (y * width + x) * 2
            bitmap_data[index] = rgb565 & 0xFF        # Low byte
            bitmap_data[index + 1] = (rgb565 >> 8) & 0xFF  # High byte
    
    print("Generating sample volcano image...")
    
    # Sky gradient
    for y in range(80):
        blue_intensity = 100 + int(100 * (80 - y) / 80)
        for x in range(width):
            set_pixel(x, y, 50, 100, min(255, blue_intensity))
    
    # Volcano mountain
    peak_x = width // 2
    for y in range(80, 200):
        for x in range(width):
            dist_from_peak = abs(x - peak_x)
            mountain_width = (y - 80) * 0.8
            
            if dist_from_peak < mountain_width:
                if y < 140 and dist_from_peak < 15:
                    # Lava area
                    lava_intensity = 255 - int(dist_from_peak * 8)
                    set_pixel(x, y, lava_intensity, lava_intensity // 3, 0)
                else:
                    # Mountain slopes
                    rock_intensity = 60 + int((200 - y) / 4)
                    set_pixel(x, y, rock_intensity, rock_intensity - 10, rock_intensity - 20)
            else:
                # Sky continuation
                blue_intensity = 100 + int(50 * (200 - y) / 120)
                set_pixel(x, y, 80, 120, min(255, blue_intensity))
    
    # Foreground vegetation
    for y in range(200, height):
        for x in range(width):
            green_base = 80 + int((x + y) % 30)
            set_pixel(x, y, 20, green_base, 30)
    
    return bitmap_data

def create_micropython_file(bitmap_data, filename, array_name="volcano_image"):
    """Create MicroPython file with image data"""
    
    with open(filename, 'w') as f:
        f.write('"""\n')
        f.write('Volcano image data in RGB565 format\n')
        f.write('Generated for M5StickC Plus MicroPython graphics\n')
        f.write('"""\n\n')
        
        f.write(f'{array_name} = bytes([\n')
        
        # Write bytes in readable format
        for i in range(0, len(bitmap_data), 16):
            chunk = bitmap_data[i:i+16]
            hex_values = ', '.join(f'0x{b:02X}' for b in chunk)
            f.write(f'    {hex_values},\n')
        
        f.write('])\n\n')
        f.write('# Image dimensions\n')
        f.write('IMAGE_WIDTH = 135\n')
        f.write('IMAGE_HEIGHT = 240\n')
    
    print(f"Created {filename} with {len(bitmap_data)} bytes of image data")

def main():
    # Generate sample volcano image
    volcano_bitmap = create_sample_volcano_image()
    
    # Save as MicroPython file
    create_micropython_file(volcano_bitmap, "volcano_image.py")
    
    # Also save raw binary
    with open("volcano.rgb565", "wb") as f:
        f.write(volcano_bitmap)
    
    print("Sample volcano image created successfully!")
    print("Files: volcano_image.py, volcano.rgb565")

if __name__ == "__main__":
    main()