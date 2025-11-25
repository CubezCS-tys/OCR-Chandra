#!/usr/bin/env python3
"""
Fix image paths in markdown to point to extracted images
"""
import sys
import re
from pathlib import Path

def fix_image_paths(md_path, images_dir=None):
    """
    Fix image paths in markdown to point to actual extracted images
    
    Args:
        md_path: Path to markdown file
        images_dir: Directory containing extracted images (default: {md_name}_images)
    """
    md_path = Path(md_path)
    if images_dir is None:
        images_dir = md_path.parent / f"{md_path.stem}_images"
    else:
        images_dir = Path(images_dir)
    
    if not images_dir.exists():
        print(f"Warning: Images directory not found: {images_dir}")
        return
    
    # Get list of extracted images
    image_files = sorted(images_dir.glob("*"))
    if not image_files:
        print(f"No images found in {images_dir}")
        return
    
    print(f"Found {len(image_files)} images:")
    for img in image_files:
        print(f"  - {img.name}")
    
    # Read markdown
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix image paths
    # Pattern: ![](_page_XX_Figure_Y.jpeg) or ![description]()
    # Replace with actual image paths
    
    # Create mapping of page numbers to images
    page_to_image = {}
    for img_file in image_files:
        # Extract page number from filename (e.g., page16_img1.jpeg -> 16)
        match = re.search(r'page(\d+)_', img_file.name)
        if match:
            page_num = int(match.group(1))
            if page_num not in page_to_image:
                page_to_image[page_num] = []
            page_to_image[page_num].append(img_file)
    
    print(f"\nPage to image mapping:")
    for page, images in sorted(page_to_image.items()):
        print(f"  Page {page}: {[img.name for img in images]}")
    
    # Replace image references
    def replace_image(match):
        full_match = match.group(0)
        description = match.group(1) if match.group(1) else "Image"
        
        # Try to extract page number from surrounding context
        # Look for {XX}---- pattern before the image
        start_pos = max(0, match.start() - 200)
        context_before = content[start_pos:match.start()]
        page_match = re.search(r'\{(\d+)\}---', context_before)
        
        if page_match:
            page_num = int(page_match.group(1))
            if page_num in page_to_image:
                # Use relative path from markdown file
                img_file = page_to_image[page_num][0]
                rel_path = f"{images_dir.name}/{img_file.name}"
                return f"![{description}]({rel_path})"
        
        # If no page match, return original
        return full_match
    
    # Pattern to match: ![description](_page_XX_Figure_Y.jpeg) or ![description]()
    original_content = content
    content = re.sub(r'!\[([^\]]*)\]\([^\)]*_page_\d+[^\)]*\)', replace_image, content)
    content = re.sub(r'!\[([^\]]*)\]\(\)', replace_image, content)
    
    if content != original_content:
        # Write back
        output_path = md_path.parent / f"{md_path.stem}_with_images.md"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\n✅ Fixed image paths: {output_path}")
        return output_path
    else:
        print("\n⚠️  No image references found to fix")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fix_images.py <markdown_file> [images_dir]")
        print("\nExample:")
        print("  python fix_images.py datalab_output/1749-000-022-008.md")
        sys.exit(1)
    
    md_file = sys.argv[1]
    images_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    fix_image_paths(md_file, images_dir)
