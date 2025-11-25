# OCR Solution Walkthrough

I have implemented a solution to convert your Arabic PDFs into Word, Searchable PDF, and HTML formats using PaddleOCR.

## What has been done
1. **Environment Setup**: Created a virtual environment and installed `paddleocr`, `pdf2image`, `python-docx`, `reportlab`, `arabic-reshaper`, `python-bidi` and other dependencies.
2. **Prototype**: Verified OCR accuracy on the first page of your sample PDF.
3. **Full Implementation**: Created `process_pdf.py` to process the entire document.
4. **Quality Improvements**:
    - **Searchable PDF**: Fixed text selection by drawing the image *behind* the text layer and adjusting font size.
    - **Word**: Improved RTL/LTR direction handling for better support of mixed content (Arabic + Math/English).
    - **HTML**: Added Google Fonts (Cairo, Roboto) and CSS styling for a cleaner, more readable layout.

## How to use
To process a PDF, run the following command from the `antigrav-ocr` directory:

```bash
source .venv/bin/activate
python process_pdf.py <path_to_pdf> <output_directory>
```

Example:
```bash
python process_pdf.py pdfs/1749-000-022-008.pdf output
```

## Outputs
The script generates:
- **[filename].docx**: A Word document with the extracted text, respecting RTL/LTR direction.
- **[filename]_searchable.pdf**: A PDF with the original images and a hidden text layer for searching and selecting.
- **[filename].html**: A styled HTML version of the text using Google Fonts.

## Notes
- **Accuracy**: The OCR uses PaddleOCR's Arabic model.
- **Layout**: The Searchable PDF preserves the visual layout exactly. The Word output preserves text content and paragraph structure.
