from typing import Dict, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class LegalLetterGenerator:
    def __init__(self, rag_system):
        self.rag_system = rag_system
    
    def generate_formal_letter(self, case_data: Dict) -> Dict[str, str]:
        """Generate formal legal letter"""
        
        # Search for relevant legal sections
        search_query = f"{case_data['case_title']} {case_data['incident_summary']} {' '.join(case_data.get('tags', []))}"
        relevant_docs = self.rag_system.similarity_search(search_query, k=7)
        
        # Generate letter content
        letter_prompt = f"""
        Generate a formal legal letter based on the following case details and legal context:
        
        Case Title: {case_data['case_title']}
        Client Name: {case_data['client_name']}
        Advocate Name: {case_data['advocate_name']}
        Law Firm: {case_data['law_firm_name']}
        Incident Summary: {case_data['incident_summary']}
        Tags: {', '.join(case_data.get('tags', []))}
        
        Legal Context:
        {self._format_context(relevant_docs)}
        
        Please generate a formal legal letter that includes:
        1. Clear statement of facts
        2. Legal grounds based on the provided context
        3. Demand/relief sought
        4. Professional closing
        
        The letter should be formal, legally sound, and favor the employee's position.
        Do not include letterhead formatting as that will be handled separately.
        """
        
        formal_letter_response = self.rag_system.generate_response(letter_prompt, relevant_docs)
        
        # Generate supporting arguments
        arguments_prompt = f"""
        Based on the case details and legal context provided, generate detailed legal arguments that support the employee's position:
        
        Case: {case_data['case_title']}
        Summary: {case_data['incident_summary']}
        
        Legal Context:
        {self._format_context(relevant_docs)}
        
        Provide:
        1. Key legal arguments
        2. Relevant legal provisions
        3. Precedent references
        4. Strategic recommendations
        5. Potential counterarguments and responses
        """
        
        legal_arguments_response = self.rag_system.generate_response(arguments_prompt, relevant_docs)
        
        # Extract string content from AIMessage objects
        formal_letter = self._extract_content(formal_letter_response)
        legal_arguments = self._extract_content(legal_arguments_response)
        
        # Extract supporting sections
        supporting_sections = [
            f"{doc['section_title']} (Page {doc['page_number']})"
            for doc in relevant_docs[:5]
        ]
        
        return {
            "formal_letter": formal_letter,
            "legal_arguments": legal_arguments,
            "supporting_sections": supporting_sections,
            "relevant_documents": relevant_docs
        }
    
    def _extract_content(self, response) -> str:
        """Extract string content from LangChain response objects"""
        if hasattr(response, 'content'):
            return response.content
        elif isinstance(response, str):
            return response
        else:
            return str(response)
    
    def _format_context(self, docs: List[Dict]) -> str:
        """Format documents for context"""
        formatted = []
        for doc in docs:
            formatted.append(f"Section: {doc['section_title']}\nContent: {doc['content'][:500]}...")
        return "\n\n".join(formatted)
    
    def format_letter_for_export(self, letter_data: Dict, case_data: Dict) -> str:
        """Format letter for PDF export with complete dynamic letterhead"""
        current_date = datetime.now().strftime("%B %d, %Y")
        
        # Extract content
        formal_letter = self._extract_content(letter_data.get('formal_letter', ''))
        formal_letter = self._process_text_formatting(formal_letter)
        
        formatted_letter = f"""
        <html>
        <head>
            <style>
                body {{ 
                    font-family: 'Times New Roman', serif; 
                    margin: 1.5in 1in 1in 1in; 
                    line-height: 1.6; 
                    color: #000000;
                    font-size: 12pt;
                    background: white;
                }}
                .letterhead {{ 
                    text-align: center; 
                    margin-bottom: 2em;
                    border-bottom: 2px solid #000000;
                    padding-bottom: 1em;
                }}
                .letterhead h1 {{
                    font-size: 18pt;
                    font-weight: bold;
                    margin: 0 0 0.5em 0;
                    letter-spacing: 2pt;
                    text-transform: uppercase;
                }}
                .firm-details {{
                    font-size: 11pt;
                    margin: 0.5em 0;
                    line-height: 1.4;
                }}
                .date-section {{ 
                    text-align: right; 
                    margin: 2em 0 1.5em 0;
                    font-weight: bold;
                }}
                .recipient {{
                    margin: 1.5em 0;
                    line-height: 1.4;
                }}
                .subject-line {{
                    margin: 1.5em 0;
                    font-weight: bold;
                    text-decoration: underline;
                }}
                .content {{ 
                    text-align: justify; 
                    margin: 1.5em 0;
                    font-size: 12pt;
                }}
                .content h2 {{
                    font-size: 14pt;
                    font-weight: bold;
                    margin: 1.5em 0 1em 0;
                    text-decoration: underline;
                }}
                .content p {{
                    margin: 1em 0;
                    text-indent: 0.5in;
                }}
                .section-header {{
                    font-weight: bold;
                    text-decoration: underline;
                    margin: 1.5em 0 0.5em 0;
                    text-indent: 0;
                }}
                .legal-provisions {{ 
                    margin: 2em 0;
                    padding: 1em;
                    border: 1px solid #000000;
                }}
                .legal-provisions h3 {{
                    font-size: 12pt;
                    font-weight: bold;
                    margin-bottom: 1em;
                    text-align: center;
                    text-decoration: underline;
                }}
                .legal-provisions ul {{ 
                    list-style-type: decimal;
                    margin: 0;
                    padding-left: 1.5em;
                }}
                .legal-provisions li {{ 
                    margin: 0.5em 0;
                    font-style: italic;
                }}
                .signature-block {{ 
                    margin-top: 3em;
                    text-align: left;
                }}
                .signature-line {{
                    margin-top: 2em;
                    margin-bottom: 0.5em;
                }}
                .typed-name {{
                    font-weight: bold;
                }}
                strong, b {{ font-weight: bold; }}
                em, i {{ font-style: italic; }}
                
                @media print {{
                    body {{ margin: 1in; font-size: 11pt; }}
                    .letterhead {{ break-after: avoid; }}
                    .legal-provisions {{ break-inside: avoid; }}
                    .signature-block {{ break-inside: avoid; }}
                }}
            </style>
        </head>
        <body>
            <div class="letterhead">
                <h1>{case_data.get('law_firm_name', 'Law Firm')}</h1>
                <div class="firm-details">
                    {case_data.get('law_firm_address', '')}<br>
                    {case_data.get('law_firm_city', '')}, {case_data.get('law_firm_state', '')} {case_data.get('law_firm_zip', '')}<br>
                    Phone: {case_data.get('law_firm_phone', '')}<br>
                    Email: {case_data.get('law_firm_email', '')}
                </div>
            </div>
            
            <div class="date-section">
                {current_date}
            </div>
            
            <div class="recipient">
                {case_data.get('recipient_name', '[Recipient Name]')}<br>
                {case_data.get('recipient_organization', '[Organization]')}<br>
                {case_data.get('recipient_address', '[Address]')}<br>
                {case_data.get('recipient_city', '[City]')}, {case_data.get('recipient_state', '[State]')} {case_data.get('recipient_zip', '[ZIP]')}
            </div>
            
            <div class="subject-line">
                <strong>Re:</strong> {case_data['case_title']}
            </div>
            
            <div class="content">
                <p><strong>Dear Sir/Madam,</strong></p>
                {formal_letter}
            </div>
            
            <div class="legal-provisions">
                <h3>Legal Provisions Referenced</h3>
                <ul>
                    {''.join([f"<li>{section}</li>" for section in letter_data.get('supporting_sections', [])])}
                </ul>
            </div>
            
            <div class="signature-block">
                <p>Respectfully submitted,</p>
                
                <div class="signature-line">
                    _________________________<br>
                    <span class="typed-name">{case_data['advocate_name']}</span><br>
                    Legal Counsel for {case_data['client_name']}<br>
                    {'Bar Registration: ' + case_data.get('bar_registration_number', '') + '<br>' if case_data.get('bar_registration_number') else ''}
                    {case_data.get('law_firm_phone', '')}<br>
                    {case_data.get('law_firm_email', '')}
                </div>
            </div>
        </body>
        </html>
        """
        
        return formatted_letter
    
    def _process_text_formatting(self, text: str) -> str:
        """Process markdown-style formatting for professional legal document"""
        import re
        
        # Handle **bold** text
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        
        # Handle *italic* text
        text = re.sub(r'(?<!\*)\*(?!\*)([^*]+)\*(?!\*)', r'<em>\1</em>', text)
        
        # Handle section headers
        text = re.sub(r'^([A-Z][A-Z\s]+:)', r'<div class="section-header">\1</div>', text, flags=re.MULTILINE)
        
        # Handle numbered points
        text = re.sub(r'^(\d+\.\s)', r'<strong>\1</strong>', text, flags=re.MULTILINE)
        
        # Convert paragraphs
        paragraphs = text.split('\n\n')
        formatted_paragraphs = []
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if paragraph:
                formatted_paragraphs.append(f'<p>{paragraph}</p>')
        
        return '\n'.join(formatted_paragraphs)



    def format_arguments_for_export(self, letter_data: Dict, case_data: Dict) -> str:
        """Format legal arguments for PDF export with professional styling"""
        current_date = datetime.now().strftime("%B %d, %Y")
        
        # Extract content
        legal_arguments = self._extract_content(letter_data.get('legal_arguments', ''))
        
        legal_arguments = self._process_text_formatting(legal_arguments)
        formatted_arguments = f"""
        <html>
        <head>
            <style>
                body {{ 
                    font-family: 'Times New Roman', serif; 
                    margin: 30px; 
                    line-height: 1.8; 
                    color: #2c3e50;
                    background-color: #ffffff;
                }}
                .header {{ 
                    text-align: center; 
                    margin-bottom: 40px; 
                    border-bottom: 3px solid #34495e;
                    padding-bottom: 20px;
                }}
                .law-firm {{ 
                    font-size: 1.2em; 
                    font-weight: bold; 
                    color: #2c3e50;
                    margin-bottom: 10px;
                }}
                .advocate-details {{ 
                    font-size: 1em; 
                    color: #7f8c8d;
                    font-style: italic;
                }}
                .document-title {{ 
                    font-size: 1.8em; 
                    font-weight: bold; 
                    color: #c0392b;
                    margin: 30px 0;
                    text-align: center;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }}
                .case-info {{ 
                    background: #ecf0f1; 
                    padding: 20px; 
                    border-left: 5px solid #3498db;
                    margin: 25px 0;
                    border-radius: 5px;
                }}
                .case-title {{ 
                    font-size: 1.3em; 
                    font-weight: bold; 
                    color: #2c3e50;
                    margin-bottom: 10px;
                }}
                .client-info {{ 
                    color: #7f8c8d; 
                    font-size: 0.95em;
                }}
                .date-section {{ 
                    text-align: right; 
                    margin: 20px 0;
                    font-weight: bold;
                    color: #34495e;
                }}
                .content {{ 
                    text-align: justify; 
                    margin: 30px 0;
                    font-size: 1.05em;
                }}
                .arguments-section {{ 
                    background: #f8f9fa;
                    padding: 25px;
                    border-radius: 8px;
                    margin: 25px 0;
                    border: 1px solid #dee2e6;
                }}
                .arguments-title {{ 
                    font-size: 1.4em; 
                    font-weight: bold; 
                    color: #c0392b;
                    margin-bottom: 20px;
                    text-align: center;
                    text-transform: uppercase;
                }}
                .legal-ref {{ 
                    background: #ffffff;
                    border: 2px solid #3498db;
                    padding: 20px;
                    margin: 25px 0;
                    border-radius: 8px;
                }}
                .legal-ref h3 {{ 
                    color: #2980b9; 
                    font-size: 1.2em;
                    margin-bottom: 15px;
                    text-align: center;
                }}
                .legal-ref ul {{ 
                    list-style-type: none;
                    padding-left: 0;
                }}
                .legal-ref li {{ 
                    background: #ecf0f1;
                    margin: 8px 0;
                    padding: 10px 15px;
                    border-left: 4px solid #3498db;
                    font-style: italic;
                    color: #2c3e50;
                }}
                .signature {{ 
                    margin-top: 50px; 
                    padding-top: 30px;
                    border-top: 2px solid #bdc3c7;
                }}
                .signature-block {{ 
                    text-align: left;
                    margin-top: 40px;
                }}
                .confidential {{ 
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    background: #e74c3c;
                    color: white;
                    padding: 10px 15px;
                    border-radius: 5px;
                    font-size: 0.9em;
                    font-weight: bold;
                    transform: rotate(-45deg);
                    opacity: 0.8;
                }}
                .page-header {{ 
                    font-size: 0.9em; 
                    color: #7f8c8d; 
                    text-align: center;
                    margin-bottom: 20px;
                    border-bottom: 1px solid #bdc3c7;
                    padding-bottom: 10px;
                }}
                .disclaimer {{ 
                    background: #fff3cd;
                    border: 1px solid #ffeaa7;
                    color: #856404;
                    padding: 15px;
                    margin: 25px 0;
                    border-radius: 5px;
                    font-size: 0.95em;
                    text-align: center;
                    font-style: italic;
                }}
                h1, h2, h3 {{ 
                    color: #2c3e50; 
                    font-weight: bold;
                }}
                h2 {{ 
                    border-bottom: 2px solid #3498db;
                    padding-bottom: 10px;
                    margin-top: 30px;
                }}
            </style>
        </head>
        <body>
            <div class="page-header">
                LEGAL STRATEGY & ARGUMENTS - CONFIDENTIAL ATTORNEY WORK PRODUCT
            </div>
            
            <div class="header">
                <div class="law-firm">LEGAL STRATEGY DOCUMENT</div>
                <div class="advocate-details">
                    <strong>{case_data['advocate_name']}</strong><br>
                    Legal Representative for {case_data['client_name']}
                </div>
            </div>
            
            <div class="document-title">
                Legal Arguments & Strategic Analysis
            </div>
            
            <div class="case-info">
                <div class="case-title">Re: {case_data['case_title']}</div>
                <div class="client-info">
                    <strong>Client:</strong> {case_data['client_name']}<br>
                    <strong>Legal Counsel:</strong> {case_data['advocate_name']}<br>
                    <strong>Case Tags:</strong> {', '.join(case_data.get('tags', ['N/A']))}
                </div>
            </div>
            
            <div class="date-section">
                <strong>Date of Analysis:</strong> {current_date}
            </div>
            
            <div class="disclaimer">
                <strong>CONFIDENTIALITY NOTICE:</strong> This document contains attorney work product and privileged information. 
                It is intended solely for internal case preparation and strategic planning.
            </div>
            
            <div class="arguments-section">
                <div class="arguments-title">Detailed Legal Analysis</div>
                <div class="content">
                    {legal_arguments}
                </div>
            </div>
            
            <div class="legal-ref">
                <h3>Referenced Legal Provisions from Indian Penal Code</h3>
                <ul>
                    {''.join([f"<li>{section}</li>" for section in letter_data.get('supporting_sections', [])])}
                </ul>
            </div>
            
            <div class="signature">
                <div class="signature-block">
                    <p><strong>Prepared by:</strong><br><br>
                    <strong>{case_data['advocate_name']}</strong><br>
                    Legal Counsel<br>
                    Date: {current_date}</p>
                    
                    <p style="margin-top: 30px; font-style: italic; color: #7f8c8d;">
                        <strong>Note:</strong> This document is prepared for internal case strategy and should not be disclosed 
                        to opposing parties or used in formal legal proceedings without proper review and modification.
                    </p>
                </div>
            </div>
            
            <div class="confidential">
                CONFIDENTIAL
            </div>
        </body>
        </html>
        """
        
        return formatted_arguments
