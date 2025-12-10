r"""
Icon & Logo Updater Script
---------------------------
This script updates ALL icon and logo files across the project with a new source image.
It generates multiple formats (PNG, ICO, SVG) and sizes for:
- Favicons
- Logos
- Apple Touch Icons
- Web App Manifest Icons
- Splash Screens

Usage:
    python update_favicon.py <source_image_path>
    
Example:
    python update_favicon.py C:\Users\aiwebadmin\Desktop\new_logo.png
"""

import os
import sys
from pathlib import Path
from PIL import Image
import shutil

# Define all icon locations in the project organized by type
ICON_LOCATIONS = {
    # Favicons (32x32, 96x96, ICO, SVG)
    'favicon': [
        "static/static/favicon.png",
        "static/favicon.png",
        "backend/open_webui/static/favicon.png",
        "backend/open_webui/static/swagger-ui/favicon.png",
    ],
    'favicon-96x96': [
        "static/static/favicon-96x96.png",
        "backend/open_webui/static/favicon-96x96.png",
    ],
    'favicon-dark': [
        "static/static/favicon-dark.png",
        "backend/open_webui/static/favicon-dark.png",
    ],
    'favicon-ico': [
        "static/static/favicon.ico",
        "backend/open_webui/static/favicon.ico",
    ],
    'favicon-svg': [
        "static/static/favicon.svg",
        "backend/open_webui/static/favicon.svg",
    ],
    
    # Logos (typically larger, used in UI)
    'logo': [
        "static/static/logo.png",
        "backend/open_webui/static/logo.png",
    ],
    
    # Apple Touch Icons (180x180 recommended)
    'apple-touch-icon': [
        "static/static/apple-touch-icon.png",
        "backend/open_webui/static/apple-touch-icon.png",
    ],
    
    # Web App Manifest Icons
    'web-app-192': [
        "static/static/web-app-manifest-192x192.png",
        "backend/open_webui/static/web-app-manifest-192x192.png",
    ],
    'web-app-512': [
        "static/static/web-app-manifest-512x512.png",
        "backend/open_webui/static/web-app-manifest-512x512.png",
    ],
    
    # Splash Screens
    'splash': [
        "static/static/splash.png",
        "backend/open_webui/static/splash.png",
    ],
    'splash-dark': [
        "static/static/splash-dark.png",
        "backend/open_webui/static/splash-dark.png",
    ],
}

def get_project_root():
    """Get the project root directory."""
    script_dir = Path(__file__).parent.absolute()
    return script_dir

def create_png_icon(source_img, output_path, size=(32, 32), maintain_aspect=True):
    """Create a PNG icon of specified size."""
    img = source_img.copy()
    
    if maintain_aspect:
        img.thumbnail(size, Image.Resampling.LANCZOS)
        # Create a new image with RGBA mode
        final_img = Image.new('RGBA', size, (255, 255, 255, 0))
        # Paste the resized image centered
        offset = ((size[0] - img.size[0]) // 2, (size[1] - img.size[1]) // 2)
        final_img.paste(img, offset)
    else:
        # Resize to exact dimensions (for splash screens)
        final_img = img.resize(size, Image.Resampling.LANCZOS)
    
    final_img.save(output_path, 'PNG', optimize=True)
    print(f"✓ Created {size[0]}x{size[1]} PNG: {output_path.name}")

def create_ico_favicon(source_img, output_path):
    """Create a 32x32 ICO favicon."""
    size = (32, 32)
    img = source_img.copy()
    
    # Resize to exact 32x32
    final_img = img.resize(size, Image.Resampling.LANCZOS)
    
    # Save with explicit sizes parameter to ensure 32x32
    final_img.save(output_path, format='ICO', sizes=[(32, 32)])
    print(f"✓ Created 32x32 ICO: {output_path.name}")

def create_svg_from_png(source_img, output_path):
    """Convert PNG to SVG by embedding as base64 data URI."""
    import base64
    from io import BytesIO
    
    # Use a larger size for better quality (512x512)
    img = source_img.copy()
    img.thumbnail((512, 512), Image.Resampling.LANCZOS)
    
    # Convert to PNG bytes
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    png_data = buffer.getvalue()
    
    # Encode as base64
    base64_data = base64.b64encode(png_data).decode('utf-8')
    
    # Create SVG with embedded PNG using proper viewBox for scaling
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="512" height="512" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
    <image width="512" height="512" xlink:href="data:image/png;base64,{base64_data}"/>
</svg>'''
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    print(f"✓ Created SVG from PNG (512x512): {output_path.name}")

def update_all_favicons(source_path):
    """Update all icon and logo files in the project."""
    source_path = Path(source_path)
    project_root = get_project_root()
    
    if not source_path.exists():
        print(f"❌ Error: Source file not found: {source_path}")
        return False
    
    print(f"\n📁 Project root: {project_root}")
    print(f"🖼️  Source image: {source_path}\n")
    
    # Load source image
    try:
        if source_path.suffix.lower() == '.svg':
            print("⚠️  SVG source detected. SVG files will be copied directly.")
            source_img = None
        else:
            source_img = Image.open(source_path)
            if source_img.mode != 'RGBA':
                source_img = source_img.convert('RGBA')
            print(f"✓ Loaded source image: {source_img.size[0]}x{source_img.size[1]} pixels\n")
    except Exception as e:
        print(f"❌ Error loading source image: {e}")
        return False
    
    # Create temporary directory for generated files
    temp_dir = project_root / "temp_icons"
    temp_dir.mkdir(exist_ok=True)
    
    # Generate all required formats
    print("🔨 Generating icon files...\n")
    
    generated_files = {}
    
    if source_img:
        # Favicons
        print("📱 Favicons:")
        generated_files['favicon'] = temp_dir / "favicon.png"
        create_png_icon(source_img, generated_files['favicon'], (500, 500))
        
        generated_files['favicon-96x96'] = temp_dir / "favicon-96x96.png"
        create_png_icon(source_img, generated_files['favicon-96x96'], (96, 96))
        
        generated_files['favicon-dark'] = temp_dir / "favicon-dark.png"
        create_png_icon(source_img, generated_files['favicon-dark'], (500, 500))
        
        generated_files['favicon-ico'] = temp_dir / "favicon.ico"
        create_ico_favicon(source_img, generated_files['favicon-ico'])
        
        # Logo (256x256 or larger)
        print("\n🎨 Logo:")
        generated_files['logo'] = temp_dir / "logo.png"
        create_png_icon(source_img, generated_files['logo'], (500, 500))
        
        # Apple Touch Icon (180x180)
        print("\n🍎 Apple Touch Icon:")
        generated_files['apple-touch-icon'] = temp_dir / "apple-touch-icon.png"
        create_png_icon(source_img, generated_files['apple-touch-icon'], (180, 180))
        
        # Web App Manifest Icons
        print("\n📲 Web App Manifest Icons:")
        generated_files['web-app-192'] = temp_dir / "web-app-manifest-192x192.png"
        create_png_icon(source_img, generated_files['web-app-192'], (192, 192))
        
        generated_files['web-app-512'] = temp_dir / "web-app-manifest-512x512.png"
        create_png_icon(source_img, generated_files['web-app-512'], (512, 512))
        
        # Splash Screens (typically larger, e.g., 1024x1024 or 2048x2048)
        print("\n💦 Splash Screens:")
        generated_files['splash'] = temp_dir / "splash.png"
        create_png_icon(source_img, generated_files['splash'], (500, 500), maintain_aspect=False)
        
        generated_files['splash-dark'] = temp_dir / "splash-dark.png"
        create_png_icon(source_img, generated_files['splash-dark'], (500, 500), maintain_aspect=False)
    
    # SVG version
    print("\n🎯 SVG:")
    generated_files['favicon-svg'] = temp_dir / "favicon.svg"
    if source_path.suffix.lower() == '.svg':
        shutil.copy2(source_path, generated_files['favicon-svg'])
        print(f"✓ Copied SVG: {generated_files['favicon-svg'].name}")
    else:
        create_svg_from_png(source_img, generated_files['favicon-svg'])
    
    # Copy files to all locations
    print("\n📋 Updating icon files across the project...\n")
    
    updated_count = 0
    for icon_type, locations in ICON_LOCATIONS.items():
        if icon_type in generated_files:
            source_file = generated_files[icon_type]
            for location in locations:
                target_path = project_root / location
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                try:
                    shutil.copy2(source_file, target_path)
                    print(f"✓ Updated: {location}")
                    updated_count += 1
                except Exception as e:
                    print(f"❌ Failed to update {location}: {e}")
    
    # Clean up temporary directory
    print(f"\n🧹 Cleaning up temporary files...")
    shutil.rmtree(temp_dir)
    
    print(f"\n✅ Icon update complete! Updated {updated_count} files.")
    print("\n📝 Next steps:")
    print("   1. If you have a custom SVG design, manually update the SVG files")
    print("   2. Test the application to ensure all icons are displaying correctly")
    print("   3. Check favicon, logo, splash screens on different devices")
    print("   4. Commit the changes to version control")
    
    return True

def main():
    """Main function."""
    print("=" * 70)
    print("     Icon & Logo Updater for OMD AI Project")
    print("=" * 70)
    
    if len(sys.argv) < 2:
        print("\n❌ Error: No source image provided")
        print("\nUsage:")
        print(f"    python {sys.argv[0]} <source_image_path>")
        print("\nExample:")
        print(f"    python {sys.argv[0]} C:\\Users\\aiwebadmin\\Desktop\\new_logo.png")
        print("\nSupported formats: PNG, JPG, JPEG, SVG")
        print("\nThis script will update:")
        print("  ✓ Favicons (32x32, 96x96, ICO, SVG)")
        print("  ✓ Logos (256x256)")
        print("  ✓ Apple Touch Icons (180x180)")
        print("  ✓ Web App Manifest Icons (192x192, 512x512)")
        print("  ✓ Splash Screens (2048x2048)")
        sys.exit(1)
    
    source_path = sys.argv[1]
    
    # Check if PIL is available
    try:
        from PIL import Image
    except ImportError:
        print("\n❌ Error: Pillow library not found")
        print("\nPlease install it using:")
        print("    pip install Pillow")
        sys.exit(1)
    
    success = update_all_favicons(source_path)
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
