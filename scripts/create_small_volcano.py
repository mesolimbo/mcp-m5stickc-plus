#!/usr/bin/env python3
"""
Create a small, memory-efficient volcano image for M5StickC Plus
"""

def create_small_volcano_image():
    """Create a smaller volcano bitmap (68x120 - quarter size)"""
    width, height = 68, 120  # Half the original dimensions
    
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
    
    print(f"Generating small volcano image ({width}x{height})...")
    
    # Sky gradient (reduced)
    for y in range(40):
        blue_intensity = 120 + int(80 * (40 - y) / 40)
        for x in range(width):
            set_pixel(x, y, 60, 120, min(255, blue_intensity))
    
    # Volcano mountain (simplified)
    peak_x = width // 2
    for y in range(40, 100):
        for x in range(width):
            dist_from_peak = abs(x - peak_x)
            mountain_width = (y - 40) * 0.6
            
            if dist_from_peak < mountain_width:
                if y < 70 and dist_from_peak < 8:
                    # Lava area
                    lava_intensity = 240 - int(dist_from_peak * 10)
                    set_pixel(x, y, lava_intensity, lava_intensity // 4, 0)
                else:
                    # Mountain slopes
                    rock_intensity = 70 + int((100 - y) / 3)
                    set_pixel(x, y, rock_intensity, rock_intensity - 15, rock_intensity - 25)
            else:
                # Sky continuation
                blue_intensity = 100 + int(40 * (100 - y) / 60)
                set_pixel(x, y, 90, 130, min(255, blue_intensity))
    
    # Foreground vegetation (simplified)
    for y in range(100, height):
        for x in range(width):
            green_base = 90 + int((x + y) % 20)
            set_pixel(x, y, 30, green_base, 40)
    
    return bitmap_data

def create_compact_micropython_file(bitmap_data, filename, array_name="small_volcano"):
    """Create compact MicroPython file with image data"""
    
    with open(filename, 'w') as f:
        f.write('# Small volcano image (memory optimized)\n')
        f.write(f'{array_name} = bytes([\n')
        
        # Write bytes more compactly
        for i in range(0, len(bitmap_data), 20):
            chunk = bitmap_data[i:i+20]
            hex_values = ','.join(f'{b}' for b in chunk)  # Use decimal for compactness
            f.write(f'{hex_values},\n')
        
        f.write('])\n')
        f.write('SMALL_WIDTH = 68\n')
        f.write('SMALL_HEIGHT = 120\n')
    
    print(f"Created compact {filename} with {len(bitmap_data)} bytes")

def main():
    # Generate smaller volcano image
    small_volcano_bitmap = create_small_volcano_image()
    
    # Save as compact MicroPython file
    create_compact_micropython_file(small_volcano_bitmap, "small_volcano_image.py")
    
    print("Small volcano image created successfully!")
    print(f"Size: {len(small_volcano_bitmap)} bytes (vs original 64800 bytes)")

if __name__ == "__main__":
    main()