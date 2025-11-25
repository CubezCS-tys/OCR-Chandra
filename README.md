# OCR Solution - Complete Workflow

This project provides tools to convert Arabic PDFs into various formats using the Datalab Chandra API.

## Complete Workflow

```
Original PDF → Datalab API → Markdown → HTML/PDF
```

## Quick Start

1. **Get API Key**: Sign up at [Datalab](https://www.datalab.to/)
2. **Set API Key**: Create `.env` file with `DATALAB_API_KEY=your_key`
3. **Process PDF**:
   ```bash
   source .venv/bin/activate
   python process_with_datalab.py pdfs/your_file.pdf output
   ```
4. **Convert to PDF** (optional):
   ```bash
   python md_to_pdf.py output/your_file.md
   ```

## Available Scripts

### 1. `process_with_datalab.py` - Main OCR Processing
Converts PDF to markdown using Datalab Chandra API.

**Usage:**
```bash
python process_with_datalab.py <pdf_path> <output_dir> [--use-llm]
```

**Outputs:**
- `[filename].md` - Clean markdown with full text
- `[filename]_metadata.json` - Processing metadata
- `[filename]_images/` - Extracted images

**Example:**
```bash
python process_with_datalab.py pdfs/1749-000-022-008.pdf datalab_output
```

---

### 2. `md_to_html.py` - Markdown to HTML
Converts markdown to styled HTML with RTL support.

**Usage:**
```bash
python md_to_html.py <markdown_file> [output_html]
```

**Example:**
```bash
python md_to_html.py datalab_output/1749-000-022-008.md
```

---

### 3. `md_to_pdf.py` - Markdown to PDF
Converts markdown to PDF with proper Arabic RTL support.

**Usage:**
```bash
python md_to_pdf.py <markdown_file> [output_pdf]
```

**Example:**
```bash
python md_to_pdf.py datalab_output/1749-000-022-008.md
```

---

## Complete Example

Process a PDF and create all formats:

```bash
# 1. Process PDF with Datalab API
python process_with_datalab.py pdfs/document.pdf output

# 2. Convert to HTML
python md_to_html.py output/document.md

# 3. Convert to PDF
python md_to_pdf.py output/document.md

# Now you have:
# - output/document.md (markdown)
# - output/document.html (styled HTML)
# - output/document.pdf (formatted PDF)
# - output/document_images/ (extracted images)
```

## Batch Processing

Process all PDFs in a folder:

```bash
for pdf in pdfs/*.pdf; do
    python process_with_datalab.py "$pdf" output
    basename=$(basename "$pdf" .pdf)
    python md_to_pdf.py "output/${basename}.md"
done
```

## Features

✅ **High-Quality OCR** - Uses Datalab Chandra API  
✅ **Arabic RTL Support** - Proper right-to-left text rendering  
✅ **Image Extraction** - Automatically extracts embedded images  
✅ **Multiple Formats** - Markdown, HTML, and PDF outputs  
✅ **Clean Styling** - Professional formatting with Google Fonts  
✅ **No GPU Required** - Cloud-based processing  

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Requirements

- Python 3.8+
- Datalab API key
- Internet connection (for API calls)

## Cost

Datalab API is a paid service. Check pricing at https://www.datalab.to/

## Legacy Scripts

- `process_pdf.py` - Local PaddleOCR processing (lower quality, offline)
