#!/usr/bin/env python3
"""
Image to RGB565 converter for M5StickC Plus
Converts images to RGB565 little-endian format for MicroPython display
"""

import sys
import os
from PIL import Image
import struct

def rgb_to_rgb565(r, g, b):
    """Convert RGB888 to RGB565"""
    r = (r >> 3) & 0x1F
    g = (g >> 2) & 0x3F  
    b = (b >> 3) & 0x1F
    return (r << 11) | (g << 5) | b

def convert_image_to_rgb565(input_path, output_path, target_width=135, target_height=240):
    """Convert image to RGB565 format for M5StickC Plus"""
    
    print(f"Converting {input_path} to RGB565 format...")
    
    try:
        # Open and resize image
        with Image.open(input_path) as img:
            print(f"Original size: {img.size}")
            
            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize to target dimensions
            img_resized = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
            print(f"Resized to: {img_resized.size}")
            
            # Convert to RGB565
            rgb565_data = bytearray()
            
            for y in range(target_height):
                for x in range(target_width):
                    r, g, b = img_resized.getpixel((x, y))
                    rgb565 = rgb_to_rgb565(r, g, b)
                    
                    # Store as little endian (low byte first)
                    rgb565_data.append(rgb565 & 0xFF)        # Low byte
                    rgb565_data.append((rgb565 >> 8) & 0xFF) # High byte
            
            # Save RGB565 data
            with open(output_path, 'wb') as f:
                f.write(rgb565_data)
            
            print(f"Converted image saved as: {output_path}")
            print(f"RGB565 data size: {len(rgb565_data)} bytes")
            print(f"Expected size: {target_width * target_height * 2} bytes")
            
            return True
            
    except Exception as e:
        print(f"Error converting image: {e}")
        return False

def create_micropython_array(rgb565_file, output_py_file, array_name="image_data"):
    """Create MicroPython-compatible array file"""
    
    try:
        with open(rgb565_file, 'rb') as f:
            data = f.read()
        
        # Create Python file with byte array
        with open(output_py_file, 'w') as f:
            f.write(f'"""\n')
            f.write(f'RGB565 image data for MicroPython\n')
            f.write(f'Generated from {os.path.basename(rgb565_file)}\n')
            f.write(f'Size: {len(data)} bytes\n')
            f.write(f'"""\n\n')
            
            f.write(f'{array_name} = bytes([\n')
            
            # Write bytes in groups of 16 for readability
            for i in range(0, len(data), 16):
                chunk = data[i:i+16]
                hex_values = ', '.join(f'0x{b:02X}' for b in chunk)
                f.write(f'    {hex_values},\n')
            
            f.write('])\n\n')
            f.write(f'# Image dimensions\n')
            f.write(f'IMAGE_WIDTH = 135\n')
            f.write(f'IMAGE_HEIGHT = 240\n')
        
        print(f"MicroPython array saved as: {output_py_file}")
        return True
        
    except Exception as e:
        print(f"Error creating MicroPython array: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python convert_image_to_rgb565.py <input_image> [output_prefix]")
        print("Example: python convert_image_to_rgb565.py volcano.png volcano")
        sys.exit(1)
    
    input_image = sys.argv[1]
    output_prefix = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(os.path.basename(input_image))[0]
    
    if not os.path.exists(input_image):
        print(f"Error: Input file '{input_image}' not found")
        sys.exit(1)
    
    # Output files
    rgb565_file = f"{output_prefix}.rgb565"
    micropython_file = f"{output_prefix}_image.py"
    
    # Convert image
    if convert_image_to_rgb565(input_image, rgb565_file):
        # Create MicroPython array
        create_micropython_array(rgb565_file, micropython_file, f"{output_prefix}_data")
        print(f"\nConversion complete!")
        print(f"Files created:")
        print(f"  - {rgb565_file} (raw RGB565 data)")
        print(f"  - {micropython_file} (MicroPython array)")
    else:
        print("Conversion failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()