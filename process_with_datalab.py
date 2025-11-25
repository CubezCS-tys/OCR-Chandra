import os
import sys
import time
import re
import requests
from pathlib import Path
import fitz  # PyMuPDF for image extraction
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

API_URL = "https://www.datalab.to/api/v1/marker"

def fix_image_paths_in_markdown(markdown_content, images_dir, base_name):
    """
    Fix image paths in markdown to point to extracted images.
    Replaces patterns like ![](_page_XX_Figure_Y.jpeg) with actual image paths.
    """
    images_dir = Path(images_dir)
    if not images_dir.exists():
        return markdown_content
    
    # Get list of extracted images
    image_files = sorted(images_dir.glob("*"))
    if not image_files:
        return markdown_content
    
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
    
    # Function to replace image references
    def replace_image(match):
        description = match.group(1) if match.group(1) else "Image"
        old_path = match.group(2)
        
        # Try to extract page number from old path
        page_match = re.search(r'_page_(\d+)_', old_path)
        if page_match:
            # Page numbers in filename are 0-indexed, but we want 1-indexed
            page_num = int(page_match.group(1)) + 1
            
            if page_num in page_to_image:
                img_file = page_to_image[page_num][0]
                rel_path = f"{images_dir.name}/{img_file.name}"
                return f"![{description}]({rel_path})"
        
        # If no match, try to find by context (look for {XX}---- pattern)
        return match.group(0)
    
    # Replace image references
    # Pattern: ![description](_page_XX_Figure_Y.jpeg) or ![description]()
    markdown_content = re.sub(
        r'!\[([^\]]*)\]\(([^\)]*_page_\d+[^\)]*)\)',
        replace_image,
        markdown_content
    )
    
    # Also handle empty image references ![]()
    # Find them by looking at surrounding context for page markers
    lines = markdown_content.split('\n')
    current_page = None
    fixed_lines = []
    
    for line in lines:
        # Check for page marker {XX}----
        page_marker = re.search(r'\{(\d+)\}---', line)
        if page_marker:
            current_page = int(page_marker.group(1)) + 1  # Convert to 1-indexed
        
        # Replace empty image references with actual images
        if '![]()' in line and current_page and current_page in page_to_image:
            img_file = page_to_image[current_page][0]
            rel_path = f"{images_dir.name}/{img_file.name}"
            line = line.replace('![]()', f'![Image from page {current_page}]({rel_path})')
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def extract_images_from_pdf(pdf_path, output_dir):
    """Extract all images from PDF using PyMuPDF"""
    os.makedirs(output_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    image_count = 0
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        image_list = page.get_images()
        
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            
            image_filename = f"page{page_num+1}_img{img_index+1}.{image_ext}"
            image_path = os.path.join(output_dir, image_filename)
            
            with open(image_path, "wb") as img_file:
                img_file.write(image_bytes)
            
            image_count += 1
            print(f"  Extracted: {image_filename}")
    
    print(f"Total images extracted: {image_count}")
    return image_count

def process_pdf_with_datalab(pdf_path, output_dir, api_key=None, use_llm=False):
    """
    Process PDF using Datalab's Chandra API
    
    Args:
        pdf_path: Path to PDF file
        output_dir: Directory to save outputs
        api_key: Datalab API key (or set DATALAB_API_KEY env variable)
        use_llm: Use LLM for better accuracy (slower, costs more)
    """
    # Get API key
    if api_key is None:
        api_key = os.getenv("DATALAB_API_KEY")
    
    if not api_key:
        print("ERROR: No API key provided!")
        print("Please set DATALAB_API_KEY environment variable or pass api_key parameter")
        print("Get your API key from: https://www.datalab.to/")
        return
    
    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    base_name = pdf_path.stem
    
    # Extract images first
    print(f"\n=== Extracting images from PDF ===")
    images_dir = output_dir / f"{base_name}_images"
    # extract_images_from_pdf(str(pdf_path), str(images_dir))
    
    print(f"\n=== Submitting PDF to Datalab API ===")
    print(f"File: {pdf_path.name}")
    print(f"Using LLM: {use_llm}")
    
    # Submit PDF
    with open(pdf_path, 'rb') as f:
        form_data = {
            'file': (pdf_path.name, f, 'application/pdf'),
            "force_ocr": (None, True),  # Force OCR since original text is bad
            "paginate": (None, True),
            'output_format': (None, 'markdown'),
            "use_llm": (None, use_llm),
            "strip_existing_ocr": (None, True),  # Remove bad existing OCR
            "disable_image_extraction": (None, False)
        }
        headers = {"X-Api-Key": api_key}
        
        try:
            response = requests.post(API_URL, files=form_data, headers=headers)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            print(f"ERROR submitting PDF: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return
    
    if not data.get('success'):
        print(f"ERROR: {data.get('error', 'Unknown error')}")
        return
    
    request_id = data['request_id']
    check_url = data['request_check_url']
    print(f"Request ID: {request_id}")
    print(f"Polling for completion...")
    
    # Poll for completion
    max_polls = 300  # 10 minutes max
    for i in range(max_polls):
        time.sleep(2)
        
        try:
            response = requests.get(check_url, headers=headers)
            response.raise_for_status()
            check_result = response.json()
        except requests.exceptions.RequestException as e:
            print(f"ERROR checking status: {e}")
            continue
        
        status = check_result.get('status')
        
        if status == 'complete':
            print(f"\n✅ Conversion complete!")
            
            # Save markdown
            markdown_content = check_result.get('markdown', '')
            markdown_path = output_dir / f"{base_name}.md"
            with open(markdown_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            print(f"Saved Markdown: {markdown_path}")
            
            # Save images from API
            images = check_result.get('images', {})
            if images:
                images_dir = output_dir / f"{base_name}_images"
                images_dir.mkdir(exist_ok=True)
                
                import base64
                count = 0
                for filename, b64_data in images.items():
                    image_path = images_dir / filename
                    try:
                        # Handle data URI scheme if present (e.g. data:image/png;base64,...)
                        if ',' in b64_data:
                            b64_data = b64_data.split(',')[1]
                        
                        with open(image_path, 'wb') as f:
                            f.write(base64.b64decode(b64_data))
                        count += 1
                        print(f"  Saved API image: {filename}")
                    except Exception as e:
                        print(f"  Error saving image {filename}: {e}")
                
                print(f"Saved {count} images from API to {images_dir}")
                
                # Update markdown to point to these images
                # The API usually returns paths like "image.png", we need "images_dir/image.png"
                # But wait, if we put markdown in output_dir and images in output_dir/images_dir
                # We need to update references
                
                # Simple replace for now: look for the filenames and prepend the dir
                for filename in images.keys():
                    markdown_content = markdown_content.replace(f"({filename})", f"({images_dir.name}/{filename})")
                
                with open(markdown_path, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                print("Updated markdown image paths")

            # Skip local path fixing since we're using API images now
            # markdown_content = fix_image_paths_in_markdown(...)
            
            # Save HTML (if available)
            html_content = check_result.get('html')
            if html_content:
                html_path = output_dir / f"{base_name}.html"
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                print(f"Saved HTML: {html_path}")
            
            # Save JSON metadata
            import json
            json_path = output_dir / f"{base_name}_metadata.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(check_result, f, indent=2, ensure_ascii=False)
            print(f"Saved Metadata: {json_path}")
            
            return
            
        elif status == 'failed':
            print(f"❌ Conversion failed: {check_result.get('error', 'Unknown error')}")
            return
        else:
            print(f"  Status: {status} (poll {i+1}/{max_polls})")
    
    print("⏱️ Timeout waiting for conversion")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python process_with_datalab.py <pdf_path> <output_dir> [--use-llm]")
        print("\nEnvironment variables:")
        print("  DATALAB_API_KEY: Your Datalab API key (required)")
        print("\nOptions:")
        print("  --use-llm: Use LLM for better accuracy (slower, costs more)")
        print("\nGet your API key from: https://www.datalab.to/")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_dir = sys.argv[2]
    use_llm = '--use-llm' in sys.argv
    
    process_pdf_with_datalab(pdf_path, output_dir, use_llm=use_llm)
