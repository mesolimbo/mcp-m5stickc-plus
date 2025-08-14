#!/usr/bin/env python3
"""
Create tiny test image to prove RGB565 rendering works
"""

def create_tiny_test_image():
    """Create a small 32x32 test pattern"""
    width, height = 32, 32
    
    def rgb_to_rgb565(r, g, b):
        r = (r >> 3) & 0x1F
        g = (g >> 2) & 0x3F  
        b = (b >> 3) & 0x1F
        return (r << 11) | (g << 5) | b
    
    pixels = []
    
    for y in range(height):
        for x in range(width):
            # Create a simple gradient pattern
            r = int(255 * x / width)
            g = int(255 * y / height)  
            b = 128
            
            rgb565 = rgb_to_rgb565(r, g, b)
            pixels.append(rgb565 & 0xFF)
            pixels.append((rgb565 >> 8) & 0xFF)
    
    return bytes(pixels)

def create_test_file(image_data, filename):
    with open(filename, 'w') as f:
        f.write('# Tiny test image\n')
        f.write('TEST_DATA = b"')
        f.write(''.join(f'\\x{b:02x}' for b in image_data))
        f.write('"\n\n')
        f.write('WIDTH = 32\n')
        f.write('HEIGHT = 32\n')
    
    print(f"Created {filename}: {len(image_data)} bytes")

def main():
    test_data = create_tiny_test_image()
    create_test_file(test_data, "tiny_test_image.py")

if __name__ == "__main__":
    main()