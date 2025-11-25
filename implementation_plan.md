# Improving OCR Output Quality

## Goal Description
The user reported issues with the quality of the OCR output. Specifically:
- **Searchable PDF**: Text selection is broken (likely due to text being covered by the image).
- **Word/HTML**: Layout and text direction could be improved.

I will update the processing script to fix the PDF layering issue and improve the RTL handling for Word and HTML.

## Proposed Changes

### OCR Pipeline
#### [MODIFY] [process_pdf.py](file:///home/yassine/antigrav-ocr/process_pdf.py)
- **Fix Searchable PDF**:
    - Draw image *before* text to prevent covering the text layer.
    - Calculate font size dynamically based on text box height.
- **Improve Word Output**:
    - Enable `bidi` property for paragraphs to ensure correct RTL behavior in Word.
- **Improve HTML Output**:
    - Add CSS for better Arabic font rendering.

## Verification Plan

### Automated Tests
- Run `process_pdf.py` on the sample PDF.
- Verify file existence.

### Manual Verification
- **Searchable PDF**: Open in a PDF viewer, try to select text. Ensure text highlights match the visual text.
- **Word**: Open in Word (or compatible viewer), check RTL direction and paragraph alignment.
- **HTML**: Open in browser, check readability.
