#!/usr/bin/env python3
"""
Convert HTML to PDF using Chromium headless mode.
This preserves MathJax rendering perfectly.
"""
import sys
import subprocess
from pathlib import Path

def html_to_pdf_chromium(html_path, pdf_path=None):
    """Convert HTML to PDF using Chromium's headless mode"""
    
    html_path = Path(html_path).absolute()
    if pdf_path is None:
        pdf_path = html_path.with_suffix('.pdf')
    else:
        pdf_path = Path(pdf_path).absolute()
    
    if not html_path.exists():
        print(f"Error: HTML file not found: {html_path}")
        return False
    
    print(f"Converting {html_path.name} to PDF using Chromium...")
    print("Waiting for MathJax to render...")
    
    # Chromium command for PDF generation
    # --headless: run without GUI
    # --disable-gpu: disable GPU (not needed for PDF)
    # --print-to-pdf: output to PDF
    # --no-pdf-header-footer: remove header/footer
    # --run-all-compositor-stages-before-draw: wait for rendering
    # file://: use file protocol
    
    cmd = [
        'chromium-browser',
        '--headless',
        '--disable-gpu',
        '--no-pdf-header-footer',
        '--print-to-pdf=' + str(pdf_path),
        '--run-all-compositor-stages-before-draw',
        '--virtual-time-budget=10000',  # Wait 10 seconds for MathJax
        f'file://{html_path}'
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0 and pdf_path.exists():
            print(f"✅ PDF created: {pdf_path}")
            print(f"   Size: {pdf_path.stat().st_size / 1024:.1f} KB")
            return True
        else:
            print(f"❌ Error: Chromium failed")
            if result.stderr:
                print(f"   {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Error: Conversion timed out")
        return False
    except FileNotFoundError:
        print("❌ Error: chromium-browser not found")
        print("   Install with: sudo apt install chromium-browser")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python html_to_pdf.py <html_file> [output_pdf]")
        print("\nExample:")
        print("  python html_to_pdf.py datalab_output/1749-000-022-008.html")
        print("  python html_to_pdf.py input.html output.pdf")
        sys.exit(1)
    
    html_file = sys.argv[1]
    pdf_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = html_to_pdf_chromium(html_file, pdf_file)
    sys.exit(0 if success else 1)
