import os
import sys
import numpy as np
from paddleocr import PaddleOCR
from pdf2image import convert_from_path
from PIL import Image, ImageDraw
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import arabic_reshaper
from bidi.algorithm import get_display
import fitz  # PyMuPDF

# Initialize PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang='ar')

def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

def extract_images_from_pdf(pdf_path, output_dir):
    """Extract all images from PDF using PyMuPDF"""
    create_directory(output_dir)
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

def process_pdf_to_formats(pdf_path, output_dir):
    create_directory(output_dir)
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    
    # Extract images first
    print(f"\n=== Extracting images from PDF ===")
    images_dir = os.path.join(output_dir, f"{base_name}_images")
    extract_images_from_pdf(pdf_path, images_dir)
    
    print(f"\n=== Converting PDF to images for OCR ===")
    try:
        images = convert_from_path(pdf_path)
    except Exception as e:
        print(f"Error converting PDF: {e}")
        return

    # Initialize Word Document
    doc = Document()
    
    # Initialize HTML content
    html_content = []
    
    # Initialize Searchable PDF
    pdf_output_path = os.path.join(output_dir, f"{base_name}_searchable.pdf")
    c = canvas.Canvas(pdf_output_path, pagesize=A4)
    
    # Register Arabic font for PDF
    font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))
    else:
        print("Warning: DejaVuSans font not found. PDF text might not render correctly.")

    for page_num, image in enumerate(images):
        print(f"Processing page {page_num + 1}/{len(images)}...")
        
        # 1. Draw Image FIRST (so text is on top)
        temp_img_path = f"temp_page_{page_num}.jpg"
        image.save(temp_img_path)
        c.setPageSize((image.width, image.height))
        c.drawImage(temp_img_path, 0, 0, width=image.width, height=image.height)
        os.remove(temp_img_path)
        
        # OCR
        result = ocr.ocr(np.array(image))
        res = result[0]
        
        if res and 'rec_texts' in res:
            texts = res['rec_texts']
            scores = res['rec_scores']
            boxes = res['rec_boxes'] # [xmin, ymin, xmax, ymax]
            
            # Add to HTML
            html_content.append(f'<div class="page" id="page-{page_num+1}">')
            
            # Filter and collect text with HIGHER confidence threshold
            for text, score, box in zip(texts, scores, boxes):
                # Increased threshold from 0.6 to 0.75 to filter out noise
                if score > 0.75:
                    # --- Searchable PDF (Invisible Text) ---
                    img_width, img_height = image.size
                    
                    x = box[0]
                    y = img_height - box[3] 
                    
                    # Calculate font size
                    box_height = box[3] - box[1]
                    font_size = box_height * 0.75
                    
                    t = c.beginText()
                    t.setTextRenderMode(3) # Invisible
                    t.setFont('DejaVuSans', font_size)
                    t.setTextOrigin(x, y)
                    
                    # Handle Arabic reshaping
                    reshaped_text = arabic_reshaper.reshape(text)
                    bidi_text = get_display(reshaped_text)
                    
                    t.textOut(bidi_text)
                    c.drawText(t)
                    
                    # --- Determine Direction (RTL/LTR) ---
                    is_arabic = any('\u0600' <= char <= '\u06FF' for char in text)
                    direction = 'rtl' if is_arabic else 'ltr'
                    align = WD_ALIGN_PARAGRAPH.RIGHT if is_arabic else WD_ALIGN_PARAGRAPH.LEFT
                    
                    # --- Word ---
                    p = doc.add_paragraph(text)
                    p.alignment = align
                    
                    # --- HTML ---
                    html_content.append(f'<p class="{direction}">{text}</p>')
            
            html_content.append('</div><hr>')
            c.showPage()
            
            # Add page break in Word
            if page_num < len(images) - 1:
                doc.add_page_break()
            
        else:
            print(f"No text found on page {page_num + 1}")
            c.showPage()

    # Save Word
    word_path = os.path.join(output_dir, f"{base_name}.docx")
    doc.save(word_path)
    print(f"\nSaved Word doc: {word_path}")
    
    # Save HTML with improved CSS
    html_header = '''<html dir="rtl">
<head>
    <meta charset="utf-8">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&family=Roboto+Mono:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body { 
            font-family: 'Cairo', 'Roboto Mono', monospace; 
            line-height: 1.8; 
            background-color: #f9f9f9;
            color: #333;
            max-width: 900px;
            margin: 0 auto;
            padding: 40px;
        }
        .page {
            background: white;
            padding: 40px;
            margin-bottom: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            border-radius: 8px;
        }
        p { margin-bottom: 12px; }
        .rtl { direction: rtl; text-align: right; }
        .ltr { 
            direction: ltr; 
            text-align: left; 
            font-family: 'Roboto Mono', monospace;
            background-color: #f5f5f5;
            padding: 8px;
            border-radius: 4px;
            border-left: 3px solid #4CAF50;
        }
        hr { border: 0; border-top: 1px solid #eee; margin: 40px 0; }
    </style>
</head>
<body>'''
    
    final_html = html_header + "".join(html_content) + '</body></html>'
    
    html_path = os.path.join(output_dir, f"{base_name}.html")
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(final_html)
        
    print(f"Saved HTML: {html_path}")
    
    # Save PDF
    c.save()
    print(f"Saved Searchable PDF: {pdf_output_path}")
    print(f"\nImages extracted to: {images_dir}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python process_pdf.py <pdf_path> <output_dir>")
    else:
        process_pdf_to_formats(sys.argv[1], sys.argv[2])
