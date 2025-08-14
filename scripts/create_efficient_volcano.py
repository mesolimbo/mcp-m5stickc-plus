#!/usr/bin/env python3
"""
Create highly efficient volcano image using MicroPython best practices
Store as compressed bytes like the C++ library does
"""

def create_volcano_bitmap():
    """Create volcano as single bytearray (more memory efficient)"""
    width, height = 135, 240
    
    def rgb_to_rgb565(r, g, b):
        """Convert RGB888 to RGB565"""
        r = (r >> 3) & 0x1F
        g = (g >> 2) & 0x3F  
        b = (b >> 3) & 0x1F
        return (r << 11) | (g << 5) | b
    
    print(f"Generating efficient volcano ({width}x{height})...")
    
    # Pre-calculate all pixels
    pixels = []
    
    for y in range(height):
        for x in range(width):
            if y < 80:
                # Sky
                blue = 120 + int(80 * (80 - y) / 80)
                r, g, b = 60, 120, min(255, blue)
            elif y < 200:
                # Mountain area
                peak_x = width // 2
                dist = abs(x - peak_x)
                mountain_width = (y - 80) * 0.8
                
                if dist < mountain_width:
                    if y < 130 and dist < 20:
                        # Lava
                        intensity = 255 - int(dist * 6)
                        r, g, b = intensity, intensity // 3, 0
                    else:
                        # Rock
                        rock = 60 + int((200 - y) / 4)
                        r, g, b = rock, rock - 10, rock - 20
                else:
                    # Sky continuation
                    blue = 100 + int(50 * (200 - y) / 120)
                    r, g, b = 80, 120, min(255, blue)
            else:
                # Vegetation
                green = 80 + int((x + y) % 30)
                r, g, b = 20, green, 30
            
            # Convert to RGB565 and store as little-endian bytes
            rgb565 = rgb_to_rgb565(max(0, min(255, r)), 
                                 max(0, min(255, g)), 
                                 max(0, min(255, b)))
            
            pixels.append(rgb565 & 0xFF)         # Low byte
            pixels.append((rgb565 >> 8) & 0xFF)  # High byte
    
    return bytes(pixels)

def create_minimal_image_file(image_data, filename):
    """Create minimal image file"""
    
    with open(filename, 'w') as f:
        f.write('# Efficient volcano image\n')
        f.write('VOLCANO_DATA = (\n')
        
        # Write in compact hex format
        for i in range(0, len(image_data), 16):
            chunk = image_data[i:i+16]
            hex_str = ''.join(f'\\x{b:02x}' for b in chunk)
            f.write(f'    b"{hex_str}"\n')
        
        f.write(')\n\n')
        f.write('def get_volcano_data():\n')
        f.write('    return b"".join(VOLCANO_DATA)\n\n')
        f.write('WIDTH = 135\n')
        f.write('HEIGHT = 240\n')
    
    print(f"Created efficient {filename}: {len(image_data)} bytes")

def main():
    print("Creating efficient volcano image...")
    
    # Generate image
    volcano_data = create_volcano_bitmap()
    
    # Save efficiently
    create_minimal_image_file(volcano_data, "efficient_volcano.py")
    
    print(f"Efficient volcano created: {len(volcano_data)} bytes")
    print("This should load much faster on MicroPython!")

if __name__ == "__main__":
    main()