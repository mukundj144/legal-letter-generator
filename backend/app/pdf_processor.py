# PDF processing utilities
import fitz  # PyMuPDF
import os
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class PDFProcessor:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.document = None
        
    def load_pdf(self):
        """Load PDF document"""
        try:
            self.document = fitz.open(self.pdf_path)
            logger.info(f"Successfully loaded PDF: {self.pdf_path}")
            return True
        except Exception as e:
            logger.error(f"Error loading PDF: {str(e)}")
            return False
    
    def extract_text_by_pages(self) -> List[Dict[str, str]]:
        """Extract text from all pages"""
        if not self.document:
            self.load_pdf()
            
        pages_data = []
        for page_num in range(len(self.document)):
            page = self.document[page_num]
            text = page.get_text()
            
            pages_data.append({
                "page_number": page_num + 1,
                "content": text,
                "metadata": {
                    "page_count": len(self.document),
                    "source": self.pdf_path
                }
            })
        
        return pages_data
    
    def extract_sections(self) -> List[Dict[str, str]]:
        """Extract and structure legal sections"""
        pages_data = self.extract_text_by_pages()
        sections = []
        
        current_section = ""
        current_content = ""
        
        for page_data in pages_data:
            content = page_data["content"]
            lines = content.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Detect section headers (common patterns in legal documents)
                if (line.startswith("Section") or 
                    line.startswith("Article") or 
                    line.startswith("Chapter") or
                    line.isupper() and len(line) < 100):
                    
                    # Save previous section
                    if current_section and current_content:
                        sections.append({
                            "section_title": current_section,
                            "content": current_content.strip(),
                            "page_number": page_data["page_number"]
                        })
                    
                    current_section = line
                    current_content = ""
                else:
                    current_content += line + " "
        
        # Add the last section
        if current_section and current_content:
            sections.append({
                "section_title": current_section,
                "content": current_content.strip(),
                "page_number": pages_data[-1]["page_number"] if pages_data else 1
            })
        
        return sections
    
    def close(self):
        """Close PDF document"""
        if self.document:
            self.document.close()
