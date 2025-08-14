#!/usr/bin/env python3
"""
Create full-size volcano image like the C++ library does
Using the same approach as M5StickCPLUS.fakeWinXP
"""

def create_full_volcano_image():
    """Create a full 135x240 volcano bitmap"""
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
            bitmap_data[index] = rgb565 & 0xFF        # Low byte (little endian)
            bitmap_data[index + 1] = (rgb565 >> 8) & 0xFF  # High byte
    
    print(f"Generating full volcano image ({width}x{height})...")
    
    # Enhanced sky with clouds
    for y in range(80):
        for x in range(width):
            # Base sky color with gradient
            blue_base = 120 + int(80 * (80 - y) / 80)
            
            # Add cloud-like variations
            cloud_factor = 1.0
            if (x + y * 2) % 30 < 8:
                cloud_factor = 1.3  # Lighter areas (clouds)
            elif (x * 2 + y) % 25 < 5:
                cloud_factor = 0.8  # Darker areas (cloud shadows)
            
            sky_r = min(255, int(60 * cloud_factor))
            sky_g = min(255, int(120 * cloud_factor))
            sky_b = min(255, int(blue_base * cloud_factor))
            
            set_pixel(x, y, sky_r, sky_g, sky_b)
    
    # Detailed volcano mountain
    peak_x = width // 2
    peak_y = 40
    for y in range(80, 200):
        for x in range(width):
            dist_from_peak = abs(x - peak_x)
            mountain_width = (y - 80) * 0.8
            
            if dist_from_peak < mountain_width:
                # Inside mountain
                height_factor = (y - peak_y) / 160.0
                
                if y < 130 and dist_from_peak < 20:
                    # Lava crater area with variation
                    lava_intensity = 255 - int(dist_from_peak * 6)
                    lava_variation = int((x + y) % 40)
                    
                    # Hot lava colors
                    lava_r = max(200, lava_intensity - lava_variation // 4)
                    lava_g = max(50, (lava_intensity // 3) - lava_variation // 6)
                    lava_b = max(0, lava_variation // 8)
                    
                    set_pixel(x, y, lava_r, lava_g, lava_b)
                else:
                    # Mountain slopes with realistic rock texture
                    base_rock = 60 + int((200 - y) / 4)
                    
                    # Add rock texture variation
                    rock_variation = int((x * 3 + y * 2) % 50)
                    texture_factor = 0.8 + (rock_variation / 100.0)
                    
                    # Rock colors with brown/gray tones
                    rock_r = int(base_rock * texture_factor)
                    rock_g = int((base_rock - 15) * texture_factor)
                    rock_b = int((base_rock - 25) * texture_factor)
                    
                    # Add some reddish tint near lava areas
                    if y < 160 and dist_from_peak < 30:
                        rock_r = min(255, rock_r + 20)
                    
                    set_pixel(x, y, rock_r, rock_g, rock_b)
            else:
                # Background sky/atmosphere
                blue_intensity = 100 + int(50 * (200 - y) / 120)
                atm_r = 80 + int((200 - y) / 8)
                atm_g = 120 + int((200 - y) / 6)
                atm_b = min(255, blue_intensity)
                
                set_pixel(x, y, atm_r, atm_g, atm_b)
    
    # Rich foreground vegetation
    for y in range(200, height):
        for x in range(width):
            # Multiple layers of vegetation
            vegetation_depth = (y - 200) / 40.0
            
            # Base green with variations
            green_base = 80 + int((x + y) % 40)
            green_variation = int((x * 2 + y) % 30)
            
            # Different vegetation types
            if (x + y * 3) % 15 < 5:
                # Darker vegetation (shadows, dense areas)
                veg_r = 15 + green_variation // 4
                veg_g = green_base - 10
                veg_b = 25 + green_variation // 6
            elif (x * 2 + y) % 20 < 7:
                # Lighter vegetation (sunlit areas)
                veg_r = 30 + green_variation // 3
                veg_g = green_base + 15
                veg_b = 35 + green_variation // 4
            else:
                # Normal vegetation
                veg_r = 20 + green_variation // 5
                veg_g = green_base
                veg_b = 30 + green_variation // 5
            
            # Add distance haze effect
            haze_factor = 1.0 - (vegetation_depth * 0.3)
            veg_r = int(veg_r * haze_factor)
            veg_g = int(veg_g * haze_factor)
            veg_b = int(veg_b * haze_factor)
            
            set_pixel(x, y, veg_r, veg_g, veg_b)
    
    return bitmap_data

def create_optimized_micropython_file(bitmap_data, filename):
    """Create optimized MicroPython file - split into chunks to avoid memory issues"""
    
    chunk_size = 8192  # 8KB chunks
    num_chunks = (len(bitmap_data) + chunk_size - 1) // chunk_size
    
    with open(filename, 'w') as f:
        f.write('"""\n')
        f.write('Full volcano image data in RGB565 format\n')
        f.write('Optimized for M5StickC Plus MicroPython\n')
        f.write('"""\n\n')
        
        f.write('# Image assembled from chunks to avoid memory issues\n')
        f.write('def get_volcano_image():\n')
        f.write('    """Assemble image data from chunks"""\n')
        f.write('    chunks = [\n')
        
        # Write each chunk
        for i in range(num_chunks):
            start_idx = i * chunk_size
            end_idx = min(start_idx + chunk_size, len(bitmap_data))
            chunk = bitmap_data[start_idx:end_idx]
            
            f.write(f'        # Chunk {i + 1}/{num_chunks}\n')
            f.write('        bytes([\n')
            
            # Write chunk data in compact format
            for j in range(0, len(chunk), 20):
                line_data = chunk[j:j+20]
                hex_values = ','.join(f'{b}' for b in line_data)
                f.write(f'            {hex_values},\n')
            
            f.write('        ]),\n')
        
        f.write('    ]\n')
        f.write('    \n')
        f.write('    # Combine all chunks\n')
        f.write('    result = bytearray()\n')
        f.write('    for chunk in chunks:\n')
        f.write('        result.extend(chunk)\n')
        f.write('    return result\n\n')
        
        f.write('# Image dimensions\n')
        f.write('VOLCANO_WIDTH = 135\n')
        f.write('VOLCANO_HEIGHT = 240\n\n')
        
        f.write('# For compatibility\n')
        f.write('def load_volcano_data():\n')
        f.write('    """Load volcano image data when needed"""\n')
        f.write('    return get_volcano_image()\n')
    
    print(f"Created optimized {filename} with {len(bitmap_data)} bytes in {num_chunks} chunks")

def main():
    # Generate full-size volcano image
    print("Creating full-size volcano image like C++ library...")
    volcano_bitmap = create_full_volcano_image()
    
    # Save as optimized MicroPython file
    create_optimized_micropython_file(volcano_bitmap, "volcano_full_image.py")
    
    # Also save raw binary
    with open("volcano_full.rgb565", "wb") as f:
        f.write(volcano_bitmap)
    
    print("Full volcano image created successfully!")
    print(f"Size: {len(volcano_bitmap)} bytes ({len(volcano_bitmap)//1024}KB)")
    print("Files: volcano_full_image.py, volcano_full.rgb565")

if __name__ == "__main__":
    main()