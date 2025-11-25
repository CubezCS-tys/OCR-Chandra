import sys
import re
import markdown
from pathlib import Path
from weasyprint import HTML
from latex2mathml.converter import convert as latex_to_mathml

def convert_latex_to_mathml(text):
    """Convert LaTeX math expressions to MathML for PDF rendering"""
    
    def replace_display_math(match):
        latex = match.group(1)
        try:
            mathml = latex_to_mathml(latex, display="block")
            return f'<div class="math-display">{mathml}</div>'
        except:
            # If conversion fails, return as code block
            return f'<pre class="math-error">$$${latex}$$$</pre>'
    
    def replace_inline_math(match):
        latex = match.group(1)
        try:
            mathml = latex_to_mathml(latex, display="inline")
            return f'<span class="math-inline">{mathml}</span>'
        except:
            # If conversion fails, return as code
            return f'<code class="math-error">${latex}$</code>'
    
    # Replace display math ($$...$$)
    text = re.sub(r'\$\$(.+?)\$\$', replace_display_math, text, flags=re.DOTALL)
    
    # Replace inline math ($...$)
    text = re.sub(r'\$([^\$]+?)\$', replace_inline_math, text)
    
    return text

def convert_md_to_pdf(md_path, pdf_path=None):
    """Convert markdown file to PDF with LaTeX math support"""
    
    md_path = Path(md_path)
    if pdf_path is None:
        pdf_path = md_path.with_suffix('.pdf')
    else:
        pdf_path = Path(pdf_path)
    
    print(f"Converting {md_path.name} to PDF with math support...")
    
    # Read markdown
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convert LaTeX to MathML first
    md_with_mathml = convert_latex_to_mathml(md_content)
    
    # Convert to HTML
    html_body = markdown.markdown(md_with_mathml, extensions=['extra', 'nl2br', 'tables'])
    
    # Create full HTML with styling optimized for PDF
    html_template = f'''<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <style>
        @page {{
            size: A4;
            margin: 2cm;
        }}
        
        body {{
            font-family: 'DejaVu Sans', 'Arial', sans-serif;
            line-height: 1.6;
            color: #333;
            font-size: 11pt;
        }}
        
        h1 {{
            color: #2c3e50;
            font-size: 24pt;
            margin-top: 0;
            margin-bottom: 12pt;
            border-bottom: 3pt solid #3498db;
            padding-bottom: 6pt;
            page-break-after: avoid;
        }}
        
        h2 {{
            color: #34495e;
            font-size: 18pt;
            margin-top: 18pt;
            margin-bottom: 9pt;
            border-bottom: 2pt solid #95a5a6;
            padding-bottom: 4pt;
            page-break-after: avoid;
        }}
        
        h3 {{
            color: #34495e;
            font-size: 14pt;
            margin-top: 14pt;
            margin-bottom: 7pt;
            page-break-after: avoid;
        }}
        
        h4, h5, h6 {{
            color: #555;
            margin-top: 12pt;
            margin-bottom: 6pt;
            page-break-after: avoid;
        }}
        
        p {{
            margin-bottom: 8pt;
            text-align: justify;
            orphans: 3;
            widows: 3;
        }}
        
        /* Math styling */
        .math-display {{
            direction: ltr;
            text-align: center;
            margin: 12pt 0;
            padding: 8pt;
            background-color: #f9f9f9;
            border-left: 3pt solid #3498db;
            page-break-inside: avoid;
        }}
        
        .math-inline {{
            direction: ltr;
            font-family: 'DejaVu Sans', serif;
        }}
        
        .math-error {{
            background-color: #fff3cd;
            padding: 4pt;
            border: 1pt solid #ffc107;
            direction: ltr;
        }}
        
        code {{
            background-color: #f5f5f5;
            padding: 2pt 4pt;
            border-radius: 2pt;
            font-family: 'DejaVu Sans Mono', 'Courier New', monospace;
            font-size: 9pt;
            direction: ltr;
        }}
        
        pre {{
            background-color: #f5f5f5;
            padding: 10pt;
            border-radius: 4pt;
            border-left: 3pt solid #3498db;
            direction: ltr;
            overflow-x: auto;
            page-break-inside: avoid;
        }}
        
        pre code {{
            background: none;
            padding: 0;
        }}
        
        blockquote {{
            border-right: 3pt solid #3498db;
            padding-right: 12pt;
            margin-right: 0;
            margin-left: 12pt;
            color: #555;
            font-style: italic;
            page-break-inside: avoid;
        }}
        
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 12pt 0;
            page-break-inside: avoid;
        }}
        
        th, td {{
            border: 1pt solid #ddd;
            padding: 8pt;
            text-align: right;
        }}
        
        th {{
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }}
        
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        
        hr {{
            border: none;
            border-top: 1pt solid #ccc;
            margin: 20pt 0;
        }}
    </style>
</head>
<body>
{html_body}
</body>
</html>'''
    
    # Convert HTML to PDF
    # Set base_url to the directory of the markdown file so relative image paths work
    HTML(string=html_template, base_url=str(md_path.parent)).write_pdf(pdf_path)
    
    print(f"✅ PDF created: {pdf_path}")
    print(f"   Size: {pdf_path.stat().st_size / 1024:.1f} KB")
    return pdf_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python md_to_pdf.py <markdown_file> [output_pdf_file]")
        print("\nExample:")
        print("  python md_to_pdf.py datalab_output/1749-000-022-008.md")
        print("  python md_to_pdf.py input.md output.pdf")
        sys.exit(1)
    
    md_file = sys.argv[1]
    pdf_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    convert_md_to_pdf(md_file, pdf_file)
