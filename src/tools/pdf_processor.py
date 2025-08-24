"""
PDF Processing tool for Data & Analytics category
"""
import fitz  # fitz
import requests
from typing import Dict, List, Any, Optional
from loguru import logger
import re
from urllib.parse import urlparse
import tempfile
import os

class PDFProcessor:
    """Process PDF documents from URLs or local files"""
    
    def __init__(self):
        self.max_pages = 5  # Limit pages to avoid token limits
        self.max_chars_per_page = 2000
    
    def extract_text_from_url(self, pdf_url: str) -> Dict[str, Any]:
        """Extract text from PDF URL"""
        logger.info(f"📄 Processing PDF from URL: {pdf_url[:60]}...")
        
        try:
            # Download PDF to temp file
            response = requests.get(pdf_url, timeout=30)
            response.raise_for_status()
            
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                tmp_file.write(response.content)
                tmp_file_path = tmp_file.name
            
            try:
                result = self._extract_text_from_file(tmp_file_path)
                result['source_url'] = pdf_url
                return result
            finally:
                # Clean up temp file
                if os.path.exists(tmp_file_path):
                    os.unlink(tmp_file_path)
                    
        except Exception as e:
            logger.error(f"❌ Failed to process PDF from URL: {e}")
            return {
                'success': False,
                'error': str(e),
                'text': '',
                'metadata': {},
                'source_url': pdf_url
            }
    
    def _extract_text_from_file(self, file_path: str) -> Dict[str, Any]:
        """Extract text from local PDF file"""
        try:
            doc = fitz.open(file_path)
            
            metadata = {
                'page_count': len(doc),
                'title': doc.metadata.get('title', ''),
                'author': doc.metadata.get('author', ''),
                'subject': doc.metadata.get('subject', ''),
                'creator': doc.metadata.get('creator', '')
            }
            
            # Extract text from limited pages
            pages_to_process = min(self.max_pages, len(doc))
            extracted_text = []
            
            for page_num in range(pages_to_process):
                page = doc[page_num]
                text = page.get_text()
                
                # Clean and limit text
                cleaned_text = self._clean_text(text)
                if len(cleaned_text) > self.max_chars_per_page:
                    cleaned_text = cleaned_text[:self.max_chars_per_page] + "..."
                
                if cleaned_text.strip():
                    extracted_text.append({
                        'page': page_num + 1,
                        'text': cleaned_text
                    })
            
            doc.close()
            
            # Combine all text
            full_text = "\n\n".join([page['text'] for page in extracted_text])
            
            logger.info(f"✅ Extracted {len(full_text)} characters from {pages_to_process} pages")
            
            return {
                'success': True,
                'text': full_text,
                'pages': extracted_text,
                'metadata': metadata,
                'pages_processed': pages_to_process
            }
            
        except Exception as e:
            logger.error(f"❌ PDF extraction failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'text': '',
                'metadata': {},
                'pages_processed': 0
            }
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page numbers and headers/footers patterns
        text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
        text = re.sub(r'\n\s*Page \d+.*?\n', '\n', text)
        
        # Remove email addresses and URLs for privacy
        text = re.sub(r'\S+@\S+\.\S+', '[EMAIL]', text)
        text = re.sub(r'http[s]?://\S+', '[URL]', text)
        
        return text.strip()
    
    def extract_paper_sections(self, text: str) -> Dict[str, str]:
        """Extract common academic paper sections"""
        sections = {}
        
        # Common section patterns
        patterns = {
            'abstract': r'(?i)(abstract|summary)\s*[:.]?\s*(.*?)(?=\n\s*(?:introduction|keywords|1\.|i\.|background))',
            'introduction': r'(?i)(introduction|background)\s*[:.]?\s*(.*?)(?=\n\s*(?:method|approach|related work|2\.|ii\.))',
            'methodology': r'(?i)(method|approach|methodology)\s*[:.]?\s*(.*?)(?=\n\s*(?:result|experiment|3\.|iii\.))',
            'results': r'(?i)(result|finding|experiment)\s*[:.]?\s*(.*?)(?=\n\s*(?:discussion|conclusion|4\.|iv\.))',
            'conclusion': r'(?i)(conclusion|discussion|summary)\s*[:.]?\s*(.*?)(?=\n\s*(?:reference|acknowledgment|bibliography))'
        }
        
        for section, pattern in patterns.items():
            match = re.search(pattern, text, re.DOTALL | re.MULTILINE)
            if match:
                content = match.group(2).strip()[:1000]  # Limit length
                if len(content) > 50:  # Only include substantial content
                    sections[section] = content
        
        return sections

# Global instance
pdf_processor = PDFProcessor()
