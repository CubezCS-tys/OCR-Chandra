import os
import sys
import numpy as np
from pdf2image import convert_from_path
# Try importing FormulaRecognition logic
# It seems it might be part of PPStructure or separate.
# Let's try to instantiate it directly if possible, or use PPStructure.
from paddleocr import PPStructureV3

# Initialize PPStructure which usually handles layout analysis including formulas
# layout=True enables layout analysis
# table=False, ocr=True
# We want to see if it detects equations.
engine = PPStructureV3()

def test_formula(pdf_path):
    print(f"Testing formula recognition on {pdf_path}...")
    images = convert_from_path(pdf_path)
    
    if images:
        # Test on page 10 (where equations were visible in screenshots)
        # Page 10 in 0-index is 9.
        if len(images) > 9:
            image = np.array(images[9])
            print("Processing page 10...")
        else:
            image = np.array(images[0])
            print("Processing page 1...")
            
        result = engine(image)
        
        for line in result:
            # line is a dict with keys like 'type', 'bbox', 'img', 'res'
            print(f"Type: {line.get('type')}")
            print(f"Text: {line.get('res')}")
            
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_formula.py <pdf_path>")
    else:
        test_formula(sys.argv[1])
