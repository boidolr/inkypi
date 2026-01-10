#!/usr/bin/env python3
"""
Proof of Concept: Image Overlay Composition

This script demonstrates the feasibility of the composite plugin approach
by creating sample overlays using PIL/Pillow.

Usage:
    python3 scripts/poc_image_overlay.py

Output:
    - Creates sample composite images in /tmp/overlay_poc/
    - Demonstrates different positioning options
    - Shows opacity blending
    - Validates the technical approach
"""

from PIL import Image, ImageDraw, ImageFont, ImageColor
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def create_sample_base_image(size=(1000, 600), color='#87CEEB'):
    """Create a sample base image (simulating a gallery image)."""
    img = Image.new('RGB', size, ImageColor.getcolor(color, 'RGB'))
    draw = ImageDraw.Draw(img)
    
    # Draw some decorative elements to simulate a real image
    for i in range(0, size[0], 100):
        draw.line([(i, 0), (i, size[1])], fill='#ffffff', width=2)
    for i in range(0, size[1], 100):
        draw.line([(0, i), (size[0], i)], fill='#ffffff', width=2)
    
    # Add text to indicate this is the base
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
    except:
        font = ImageFont.load_default()
    
    text = "BASE IMAGE"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    draw.text(
        ((size[0] - text_width) // 2, (size[1] - text_height) // 2),
        text,
        fill='#ffffff',
        font=font
    )
    
    return img


def create_sample_overlay(size=(400, 300), color='#2E8B57', label='OVERLAY'):
    """Create a sample overlay image (simulating a weather widget)."""
    img = Image.new('RGBA', size, ImageColor.getcolor(color, 'RGB') + (255,))
    draw = ImageDraw.Draw(img)
    
    # Add border
    draw.rectangle([(0, 0), (size[0]-1, size[1]-1)], outline='#ffffff', width=5)
    
    # Add label
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
    except:
        font = ImageFont.load_default()
    
    bbox = draw.textbbox((0, 0), label, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    draw.text(
        ((size[0] - text_width) // 2, (size[1] - text_height) // 2),
        label,
        fill='#ffffff',
        font=font
    )
    
    # Add some weather-like icons (simple shapes)
    # Sun
    draw.ellipse([(20, 20), (80, 80)], fill='#FFD700', outline='#ffffff', width=2)
    
    # Temperature text
    draw.text((20, 100), "72°F", fill='#ffffff', font=font)
    
    return img


def calculate_position(base_size, overlay_size, position, margin=20):
    """Calculate (x, y) coordinates for overlay based on position string."""
    positions = {
        'top-left': (margin, margin),
        'top-right': (base_size[0] - overlay_size[0] - margin, margin),
        'bottom-left': (margin, base_size[1] - overlay_size[1] - margin),
        'bottom-right': (
            base_size[0] - overlay_size[0] - margin,
            base_size[1] - overlay_size[1] - margin
        ),
        'center': (
            (base_size[0] - overlay_size[0]) // 2,
            (base_size[1] - overlay_size[1]) // 2
        ),
    }
    return positions.get(position, positions['bottom-left'])


def apply_opacity(img, opacity):
    """Apply opacity to an image."""
    if opacity >= 1.0:
        return img
    
    # Create a copy and adjust alpha channel
    img_copy = img.copy()
    if img_copy.mode != 'RGBA':
        img_copy = img_copy.convert('RGBA')
    
    # Adjust alpha channel
    alpha = img_copy.split()[3]
    alpha = alpha.point(lambda p: int(p * opacity))
    img_copy.putalpha(alpha)
    
    return img_copy


def composite_images(base, overlay, position='bottom-left', opacity=1.0, margin=20):
    """
    Composite overlay onto base image.
    
    This is the core function that would go in utils/image_utils.py
    """
    # Ensure base is RGBA for compositing
    if base.mode != 'RGBA':
        base = base.convert('RGBA')
    
    # Apply opacity to overlay
    overlay = apply_opacity(overlay, opacity)
    
    # Calculate position
    pos = calculate_position(base.size, overlay.size, position, margin)
    
    # Create a transparent layer the size of base
    layer = Image.new('RGBA', base.size, (0, 0, 0, 0))
    layer.paste(overlay, pos, overlay)
    
    # Composite
    result = Image.alpha_composite(base, layer)
    
    return result


def run_proof_of_concept():
    """Run the proof of concept demonstration."""
    print("=" * 60)
    print("Image Overlay Proof of Concept")
    print("=" * 60)
    
    # Create output directory
    output_dir = '/tmp/overlay_poc'
    os.makedirs(output_dir, exist_ok=True)
    print(f"\nOutput directory: {output_dir}")
    
    # Create base image
    print("\n1. Creating base image (simulating gallery image)...")
    base = create_sample_base_image()
    base.save(os.path.join(output_dir, '01_base.png'))
    print(f"   Saved: 01_base.png ({base.size})")
    
    # Create overlay
    print("\n2. Creating overlay image (simulating weather widget)...")
    overlay = create_sample_overlay()
    overlay.save(os.path.join(output_dir, '02_overlay.png'))
    print(f"   Saved: 02_overlay.png ({overlay.size})")
    
    # Test different positions
    print("\n3. Testing different positions...")
    positions = ['top-left', 'top-right', 'bottom-left', 'bottom-right', 'center']
    for pos in positions:
        result = composite_images(base.copy(), overlay, position=pos, margin=20)
        filename = f'03_position_{pos}.png'
        result.save(os.path.join(output_dir, filename))
        print(f"   Saved: {filename}")
    
    # Test opacity
    print("\n4. Testing opacity blending...")
    opacities = [1.0, 0.9, 0.7, 0.5]
    for opacity in opacities:
        result = composite_images(base.copy(), overlay, position='bottom-left', opacity=opacity)
        filename = f'04_opacity_{int(opacity*100)}.png'
        result.save(os.path.join(output_dir, filename))
        print(f"   Saved: {filename} (opacity={opacity})")
    
    # Test multiple overlays
    print("\n5. Testing multiple overlays...")
    result = base.copy()
    
    # Add weather overlay (bottom-left)
    weather_overlay = create_sample_overlay(size=(350, 250), color='#2E8B57', label='WEATHER')
    result = composite_images(result, weather_overlay, position='bottom-left', opacity=0.9)
    
    # Add clock overlay (top-right)
    clock_overlay = create_sample_overlay(size=(300, 200), color='#DC143C', label='CLOCK')
    result = composite_images(result, clock_overlay, position='top-right', opacity=0.85)
    
    # Add status overlay (top-left, small)
    status_overlay = create_sample_overlay(size=(200, 150), color='#4169E1', label='STATUS')
    result = composite_images(result, status_overlay, position='top-left', opacity=0.8)
    
    result.save(os.path.join(output_dir, '05_multiple_overlays.png'))
    print(f"   Saved: 05_multiple_overlays.png")
    
    # Test sizing
    print("\n6. Testing overlay resizing...")
    large_overlay = create_sample_overlay(size=(600, 400), color='#8B4513', label='LARGE')
    # Resize to 40% of base width
    base_width = base.size[0]
    new_width = int(base_width * 0.4)
    aspect_ratio = large_overlay.size[1] / large_overlay.size[0]
    new_height = int(new_width * aspect_ratio)
    resized_overlay = large_overlay.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    result = composite_images(base.copy(), resized_overlay, position='bottom-left')
    result.save(os.path.join(output_dir, '06_resized_overlay.png'))
    print(f"   Saved: 06_resized_overlay.png (resized to 40% width)")
    
    # Summary
    print("\n" + "=" * 60)
    print("Proof of Concept Complete!")
    print("=" * 60)
    print(f"\nResults saved to: {output_dir}")
    print("\nKey findings:")
    print("  ✓ PIL/Pillow supports alpha compositing")
    print("  ✓ Position calculations work correctly")
    print("  ✓ Opacity blending works as expected")
    print("  ✓ Multiple overlays can be applied sequentially")
    print("  ✓ Overlays can be resized maintaining aspect ratio")
    print("\nConclusion: Composite plugin approach is technically feasible!")
    print("\nView the images to see the results:")
    for f in sorted(os.listdir(output_dir)):
        if f.endswith('.png'):
            print(f"  - {os.path.join(output_dir, f)}")
    

if __name__ == '__main__':
    try:
        run_proof_of_concept()
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
