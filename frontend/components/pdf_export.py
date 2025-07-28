# Streamlit component for PDF export
import streamlit as st
import base64

def export_to_pdf(html_content, filename):
    """Export HTML content to PDF"""
    
    try:
        # For this implementation, we'll provide HTML download
        # Full PDF generation would require additional libraries like weasyprint
        
        b64 = base64.b64encode(html_content.encode()).decode()
        href = f'<a href="data:text/html;base64,{b64}" download="{filename}.html">Download HTML File</a>'
        
        st.markdown(href, unsafe_allow_html=True)
        st.info("HTML file ready for download. Convert to PDF using your preferred tool.")
        
    except Exception as e:
        st.error(f"Export error: {str(e)}")

def create_pdf_preview(letter_content, case_data):
    """Create PDF preview HTML"""
    
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Times New Roman', serif; margin: 40px; }}
            .header {{ text-align: center; margin-bottom: 30px; }}
            .content {{ line-height: 1.6; text-align: justify; }}
            .signature {{ margin-top: 40px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>LEGAL NOTICE</h1>
            <p><strong>{case_data.get('advocate_name', '')}</strong></p>
        </div>
        
        <div class="content">
            <h2>{case_data.get('case_title', '')}</h2>
            {letter_content.get('formal_letter', '')}
            
            <h3>Legal Arguments:</h3>
            {letter_content.get('legal_arguments', '')}
        </div>
        
        <div class="signature">
            <p>Sincerely,<br><br>
            <strong>{case_data.get('advocate_name', '')}</strong></p>
        </div>
    </body>
    </html>
    """
    
    return html_template
