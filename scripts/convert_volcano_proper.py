#!/usr/bin/env python3
"""
Convert volcano image to RGB565 using the proper method from the cheatsheet
Stream by scanline approach - no large memory allocation
"""

from PIL import Image
import sys
import os

def convert_image_to_rgb565_file(input_path, output_path, width=135, height=240):
    """Convert image to RGB565 file using proper scanline streaming method"""
    
    print(f"Converting {input_path} to RGB565 scanline format...")
    
    try:
        # Open and process image
        with Image.open(input_path) as img:
            print(f"Original size: {img.size}")
            
            # Convert to RGB
            img = img.convert('RGB')
            
            # Calculate aspect ratios
            img_ratio = img.size[0] / img.size[1]  # width/height
            target_ratio = width / height
            
            print(f"Original aspect ratio: {img_ratio:.2f}")
            print(f"Target aspect ratio: {target_ratio:.2f}")
            
            if img_ratio > target_ratio:
                # Image is wider than target, crop width
                new_width = int(img.size[1] * target_ratio)
                left = (img.size[0] - new_width) // 2
                img = img.crop((left, 0, left + new_width, img.size[1]))
                print(f"Cropped to: {img.size}")
            elif img_ratio < target_ratio:
                # Image is taller than target, crop height  
                new_height = int(img.size[0] / target_ratio)
                top = (img.size[1] - new_height) // 2
                img = img.crop((0, top, img.size[0], top + new_height))
                print(f"Cropped to: {img.size}")
            
            # Now resize to exact target size (should maintain aspect ratio)
            img = img.resize((width, height), Image.Resampling.LANCZOS)
            print(f"Final size: {img.size}")
            
            # Create RGB565 file for scanline streaming
            with open(output_path, 'wb') as f:
                for y in range(height):
                    for x in range(width):
                        r, g, b = img.getpixel((x, y))
                        
                        # Convert to RGB565
                        rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
                        
                        # Write as big-endian (high byte first) - CONFIRMED correct for M5StickC Plus
                        f.write(bytes(((rgb565 >> 8) & 0xFF, rgb565 & 0xFF)))
            
            file_size = os.path.getsize(output_path)
            print(f"RGB565 file created: {output_path}")
            print(f"File size: {file_size} bytes ({file_size//1024}KB)")
            print(f"Expected size: {width * height * 2} bytes")
            
            return True
            
    except Exception as e:
        print(f"Error converting image: {e}")
        return False

def main():
    # Convert the volcano image properly
    input_image = "photos/volcano.png"
    output_file = "volcano_scanline.rgb565"
    
    if not os.path.exists(input_image):
        print(f"Error: {input_image} not found")
        return
    
    success = convert_image_to_rgb565_file(input_image, output_file)
    
    if success:
        print("\nConversion successful!")
        print("This file can now be streamed scanline-by-scanline to avoid memory issues")
    else:
        print("Conversion failed!")

if __name__ == "__main__":
    main()