import streamlit as st
import os
import tempfile
from pathlib import Path
import base64
from process_with_datalab import process_pdf_with_datalab
from md_to_pdf import convert_md_to_pdf
from md_to_html import convert_md_to_html
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

st.set_page_config(page_title="OCR Prototype Tool", page_icon="📄", layout="wide")

st.title("📄 OCR Prototype Tool")
st.markdown("Upload a PDF to process it using the Datalab API.")

# Check for API Key
api_key = os.getenv("DATALAB_API_KEY")
# If you want to hardcode the API key, uncomment the line below and replace with your key:
# api_key = "your_api_key_here"

if not api_key:
    st.error("❌ DATALAB_API_KEY environment variable not found. Please set it in your .env file or environment.")
    st.stop()

# Initialize session state
if 'processed' not in st.session_state:
    st.session_state.processed = False
if 'original_pdf_data' not in st.session_state:
    st.session_state.original_pdf_data = None
if 'generated_pdf_data' not in st.session_state:
    st.session_state.generated_pdf_data = None
if 'md_content' not in st.session_state:
    st.session_state.md_content = None
if 'html_content' not in st.session_state:
    st.session_state.html_content = None
if 'base_name' not in st.session_state:
    st.session_state.base_name = "output"

def display_pdf(pdf_data):
    """Display PDF in an iframe"""
    base64_pdf = base64.b64encode(pdf_data).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    # Check if this is a new file
    file_contents = uploaded_file.getvalue()
    if st.session_state.original_pdf_data != file_contents:
        # Reset state for new file
        st.session_state.processed = False
        st.session_state.original_pdf_data = file_contents
        st.session_state.generated_pdf_data = None
        st.session_state.md_content = None
        st.session_state.html_content = None
        st.session_state.base_name = Path(uploaded_file.name).stem

    if st.button("Process PDF", type="primary"):
        with st.spinner("Processing PDF with Datalab API... This may take a few minutes."):
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Save uploaded file
                pdf_path = temp_path / uploaded_file.name
                with open(pdf_path, "wb") as f:
                    f.write(st.session_state.original_pdf_data)
                
                # Create output directory
                output_dir = temp_path / "output"
                output_dir.mkdir()
                
                try:
                    # Process PDF
                    process_pdf_with_datalab(str(pdf_path), str(output_dir), api_key=api_key)
                    
                    md_file = output_dir / f"{st.session_state.base_name}.md"
                    
                    if md_file.exists():
                        # Generate HTML and PDF
                        html_file = output_dir / f"{st.session_state.base_name}.html"
                        pdf_file = output_dir / f"{st.session_state.base_name}.pdf"
                        
                        convert_md_to_html(md_file, html_file)
                        convert_md_to_pdf(md_file, pdf_file)
                        
                        # Read content
                        with open(md_file, "r", encoding="utf-8") as f:
                            md_content = f.read()
                        with open(html_file, "r", encoding="utf-8") as f:
                            html_content = f.read()
                        with open(pdf_file, "rb") as f:
                            st.session_state.generated_pdf_data = f.read()

                        # Embed images in Markdown for Preview and HTML for Download
                        # This ensures they show up in Streamlit and in the downloaded HTML
                        import re
                        import base64
                        
                        def image_to_base64(match):
                            img_path = match.group(2)
                            # Resolve path relative to output_dir
                            full_img_path = output_dir / img_path
                            if full_img_path.exists():
                                with open(full_img_path, "rb") as img_f:
                                    encoded = base64.b64encode(img_f.read()).decode()
                                    ext = full_img_path.suffix.lower().replace('.', '')
                                    if ext == 'jpg': ext = 'jpeg'
                                    return f"![{match.group(1)}](data:image/{ext};base64,{encoded})"
                            return match.group(0)

                        def html_image_to_base64(match):
                            img_path = match.group(1)
                            full_img_path = output_dir / img_path
                            if full_img_path.exists():
                                with open(full_img_path, "rb") as img_f:
                                    encoded = base64.b64encode(img_f.read()).decode()
                                    ext = full_img_path.suffix.lower().replace('.', '')
                                    if ext == 'jpg': ext = 'jpeg'
                                    return f'src="data:image/{ext};base64,{encoded}"'
                            return match.group(0)

                        # Fix Markdown for Preview
                        # Pattern: ![alt](path)
                        st.session_state.md_content = re.sub(r'!\[([^\]]*)\]\(([^\)]+)\)', image_to_base64, md_content)
                        
                        # Fix HTML for Download
                        # Pattern: src="path"
                        st.session_state.html_content = re.sub(r'src="([^"]+)"', html_image_to_base64, html_content)
                            
                        st.session_state.processed = True
                        st.rerun() # Rerun to show results
                    else:
                        st.error("Processing failed or no output generated.")
                        
                except Exception as e:
                    st.error(f"An error occurred: {e}")

if st.session_state.processed:
    st.success("✅ Processing complete!")
    
    # Downloads
    col1, col2, col3 = st.columns(3)
    
    col1.download_button(
        label="Download Markdown",
        data=st.session_state.md_content,
        file_name=f"{st.session_state.base_name}.md",
        mime="text/markdown"
    )
    
    col2.download_button(
        label="Download HTML",
        data=st.session_state.html_content,
        file_name=f"{st.session_state.base_name}.html",
        mime="text/html"
    )
    
    col3.download_button(
        label="Download PDF",
        data=st.session_state.generated_pdf_data,
        file_name=f"{st.session_state.base_name}.pdf",
        mime="application/pdf"
    )
    
    st.divider()
    
    # Side-by-side view
    st.subheader("Comparison")
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("### Original PDF")
        if st.session_state.original_pdf_data:
            display_pdf(st.session_state.original_pdf_data)
            
    with col_right:
        st.markdown("### Generated PDF")
        if st.session_state.generated_pdf_data:
            display_pdf(st.session_state.generated_pdf_data)
