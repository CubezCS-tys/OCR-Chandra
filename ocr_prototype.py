from paddleocr import PaddleOCR
from pdf2image import convert_from_path
from PIL import Image, ImageDraw
import sys
import numpy as np

# Initialize PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang='ar')

def process_pdf(pdf_path):
    print(f"Processing {pdf_path}...")
    
    try:
        images = convert_from_path(pdf_path)
    except Exception as e:
        print(f"Error converting PDF: {e}")
        return

    print(f"PDF has {len(images)} pages.")
    
    if images:
        image = images[0]
        print("Running OCR on page 1...")
        
        result = ocr.ocr(np.array(image))
        
        # New PaddleOCR format seems to be a list containing a dict
        res = result[0]
        if not res or 'rec_texts' not in res:
            print("No text detected or unknown format.")
            print(res.keys() if res else "Empty result")
            return

        print("\n--- Detected Text ---")
        texts = res['rec_texts']
        scores = res['rec_scores']
        boxes = res['rec_boxes'] # Assuming [xmin, ymin, xmax, ymax] or similar
        
        for idx, (text, score) in enumerate(zip(texts, scores)):
            print(f"Line {idx+1}: {text} (Conf: {score:.2f})")
            
        # Save visualization
        print("\nSaving visualization to 'page1_ocr.jpg'...")
        draw = ImageDraw.Draw(image)
        for box in boxes:
            # box might be [xmin, ymin, xmax, ymax]
            # Draw rectangle
            draw.rectangle(list(box), outline='red')
        image.save('page1_ocr.jpg')
        
        # Save simple HTML
        print("Saving text to 'page1.html'...")
        with open('page1.html', 'w', encoding='utf-8') as f:
            f.write('<html dir="rtl"><head><meta charset="utf-8"></head><body>')
            for text in texts:
                f.write(f'<p>{text}</p>\n')
            f.write('</body></html>')
            
        print("Done.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ocr_prototype.py <pdf_path>")
    else:
        import numpy as np # Need numpy for image conversion
        process_pdf(sys.argv[1])
