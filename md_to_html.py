import sys
import markdown
from pathlib import Path

import re

def clean_latex(text):
    """Clean LaTeX to fix common errors and improve Arabic rendering"""
    
    # 0. Remove image descriptions (alt text with empty URL)
    # Pattern: ![Description]()
    text = re.sub(r'!\[[^\]]*\]\(\)', '', text)
    
    # 1. Fix \left without \right
    # Use regex to avoid matching \rightarrow as \right
    def fix_delimiters(match):
        content = match.group(1)
        
        # Count \left and \right only when they are distinct commands
        # Look for \left followed by non-letter, or end of string
        left_count = len(re.findall(r'\\left(?![a-zA-Z])', content))
        right_count = len(re.findall(r'\\right(?![a-zA-Z])', content))
        
        if left_count != right_count:
            # Replace only exact \left and \right commands
            content = re.sub(r'\\left(?![a-zA-Z])', '', content)
            content = re.sub(r'\\right(?![a-zA-Z])', '', content)
            
        return f'$${content}$$'
    
    text = re.sub(r'\$\$(.+?)\$\$', fix_delimiters, text, flags=re.DOTALL)
    
    # 2. Extract Arabic text from \text{} inside math blocks
    # MathJax sometimes messes up RTL text inside LTR math blocks
    # We'll try to move it outside the math block if it's at the end
    
    def extract_arabic(match):
        math_content = match.group(1)
        # Look for \text{...} containing Arabic
        arabic_text_match = re.search(r'\\text\{([^\}]*[\u0600-\u06FF]+[^\}]*)\}', math_content)
        
        if arabic_text_match:
            arabic_text = arabic_text_match.group(1)
            # Remove the \text{...} from math
            cleaned_math = math_content.replace(arabic_text_match.group(0), '')
            return f'$${cleaned_math}$$ <span dir="rtl">{arabic_text}</span>'
        
        return match.group(0)
    
    text = re.sub(r'\$\$(.+?)\$\$', extract_arabic, text, flags=re.DOTALL)
    
    return text

def convert_md_to_html(md_path, html_path=None):
    """Convert markdown file to styled HTML with RTL support for Arabic"""
    
    md_path = Path(md_path)
    if html_path is None:
        html_path = md_path.with_suffix('.html')
    else:
        html_path = Path(html_path)
    
    # Read markdown
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Clean LaTeX
    md_content = clean_latex(md_content)
    
    # Convert to HTML (with math support)
    # Use python-markdown-math extension if available, otherwise keep $ delimiters
    try:
        html_body = markdown.markdown(md_content, extensions=['extra', 'nl2br'])
    except:
        html_body = markdown.markdown(md_content, extensions=['extra', 'nl2br'])
    
    # Create full HTML with styling and MathJax
    html_template = f'''<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{md_path.stem}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Amiri:ital,wght@0,400;0,700;1,400;1,700&family=IBM+Plex+Sans+Arabic:wght@400;700&family=Roboto+Mono:wght@400;700&display=swap" rel="stylesheet">
    
    <!-- MathJax for LaTeX rendering -->
    <script>
        MathJax = {{
            tex: {{
                inlineMath: [['$', '$']],
                displayMath: [['$$', '$$']],
                processEscapes: true,
                tags: 'ams'
            }},
            svg: {{
                fontCache: 'global'
            }},
            output: {{
                font: 'mathjax-modern'
            }}
        }};
    </script>
    <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js" id="MathJax-script" async></script>
    <style>
        body {{
            font-family: 'Amiri', 'Times New Roman', serif;
            line-height: 2.0;
            max-width: 900px;
            margin: 0 auto;
            padding: 40px;
            background-color: #ffffff;
            color: #333;
            font-size: 18px;
        }}
        
        /* Ensure math is LTR but text inside can be RTL */
        .mjx-chtml {{
            direction: ltr;
        }}
        
        h1, h2, h3, h4, h5, h6 {{
            font-family: 'IBM Plex Sans Arabic', sans-serif;
            color: #2c3e50;
            margin-top: 1.5em;
            margin-bottom: 0.5em;
        }}
        
        h1 {{
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        
        h2 {{
            border-bottom: 2px solid #95a5a6;
            padding-bottom: 8px;
        }}
        
        p {{
            margin-bottom: 1em;
            text-align: justify;
        }}
        
        code {{
            background-color: #f5f5f5;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Roboto Mono', monospace;
            font-size: 0.9em;
            direction: ltr;
            display: inline-block;
        }}
        
        pre {{
            background-color: #f5f5f5;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            border-left: 4px solid #3498db;
            direction: ltr;
        }}
        
        pre code {{
            background: none;
            padding: 0;
        }}
        
        blockquote {{
            border-right: 4px solid #3498db;
            padding-right: 15px;
            margin-right: 0;
            color: #555;
            font-style: italic;
        }}
        
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: right;
        }}
        
        th {{
            background-color: #3498db;
            color: white;
        }}
        
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        
        hr {{
            border: none;
            border-top: 2px solid #eee;
            margin: 40px 0;
        }}
        
        /* Page breaks from markdown */
        .page-break {{
            page-break-after: always;
            margin: 40px 0;
            border-top: 3px dashed #ccc;
        }}
    </style>
</head>
<body>
{html_body}
</body>
</html>'''
    
    # Write HTML
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    print(f"✅ Converted: {md_path.name} → {html_path.name}")
    return html_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python md_to_html.py <markdown_file> [output_html_file]")
        sys.exit(1)
    
    md_file = sys.argv[1]
    html_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    convert_md_to_html(md_file, html_file)
