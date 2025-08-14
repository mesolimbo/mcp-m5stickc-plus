#!/usr/bin/env python3
"""
Convert portrait volcano to RGB565 with correct endianness
Flexible script to test both byte orders
"""

from PIL import Image
import sys
import os

def convert_to_rgb565(input_path, output_path, width=135, height=240, little_endian=True):
    """Convert image to RGB565 with selectable endianness"""
    
    endian_str = "little-endian" if little_endian else "big-endian"
    print(f"Converting {input_path} to RGB565 ({endian_str})...")
    
    try:
        with Image.open(input_path) as img:
            print(f"Original size: {img.size}")
            
            # Convert to RGB
            img = img.convert('RGB')
            
            # Calculate aspect ratios for smart cropping
            img_ratio = img.size[0] / img.size[1]
            target_ratio = width / height
            
            print(f"Original aspect ratio: {img_ratio:.2f}")
            print(f"Target aspect ratio: {target_ratio:.2f}")
            
            if abs(img_ratio - target_ratio) > 0.1:  # Need cropping
                if img_ratio > target_ratio:
                    # Image wider than target, crop width
                    new_width = int(img.size[1] * target_ratio)
                    left = (img.size[0] - new_width) // 2
                    img = img.crop((left, 0, left + new_width, img.size[1]))
                    print(f"Cropped width to: {img.size}")
                else:
                    # Image taller than target, crop height
                    new_height = int(img.size[0] / target_ratio)
                    top = (img.size[1] - new_height) // 2
                    img = img.crop((0, top, img.size[0], top + new_height))
                    print(f"Cropped height to: {img.size}")
            
            # Resize to exact target size
            img = img.resize((width, height), Image.Resampling.LANCZOS)
            print(f"Final size: {img.size}")
            
            # Convert to RGB565 and save
            with open(output_path, 'wb') as f:
                for y in range(height):
                    for x in range(width):
                        r, g, b = img.getpixel((x, y))
                        
                        # Convert to RGB565
                        rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
                        
                        # Write bytes in selected endianness
                        if little_endian:
                            # Little-endian: low byte first
                            f.write(bytes((rgb565 & 0xFF, (rgb565 >> 8) & 0xFF)))
                        else:
                            # Big-endian: high byte first  
                            f.write(bytes(((rgb565 >> 8) & 0xFF, rgb565 & 0xFF)))
            
            file_size = os.path.getsize(output_path)
            print(f"RGB565 file created: {output_path}")
            print(f"File size: {file_size} bytes ({file_size//1024}KB)")
            print(f"Endianness: {endian_str}")
            return True
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    # Convert your portrait volcano in both endianness formats
    input_image = "photos/volcano-portrait.gif"  # Your improved image
    
    print("=== Converting Portrait Volcano ===")
    print()
    
    if not os.path.exists(input_image):
        print(f"Error: {input_image} not found")
        return
    
    # Create both versions for testing
    print("1. Creating LITTLE-ENDIAN version...")
    success1 = convert_to_rgb565(input_image, "volcano-portrait-le.rgb565", little_endian=True)
    
    print("\n2. Creating BIG-ENDIAN version...")  
    success2 = convert_to_rgb565(input_image, "volcano-portrait-be.rgb565", little_endian=False)
    
    if success1 and success2:
        print("\n✅ Both versions created successfully!")
        print("\nFiles created:")
        print("  - volcano-portrait-le.rgb565 (little-endian)")
        print("  - volcano-portrait-be.rgb565 (big-endian)")
        print("\nTest both on your device to see which has correct colors.")
    else:
        print("❌ Conversion failed!")

if __name__ == "__main__":
    main()