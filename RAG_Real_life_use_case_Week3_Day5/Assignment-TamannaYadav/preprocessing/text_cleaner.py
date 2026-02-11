"""
Text Cleaner for Tesla RAG system.
Handles text normalization and noise removal while preserving semantic structure.
"""

import re
from typing import List
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.logger import get_logger
from ingestion.pdf_loader import Document

logger = get_logger(__name__)


class TextCleaner:
    """
    Cleans and normalizes extracted text from documents.
    
    Removes noise while preserving semantic structure for better chunking.
    """
    
    def __init__(self):
        """Initialize the text cleaner with default patterns."""
        self.header_patterns = [
            r'^Page \d+ of \d+$',
            r'^\d+$',
            r'^©.*Tesla.*$',
            r'^Tesla, Inc\.$',
            r'^Confidential$',
        ]
        
        self.footer_patterns = [
            r'^www\.tesla\.com$',
            r'^tesla\.com$',
        ]
        
        logger.info("Initialized TextCleaner")
    
    def clean(self, document: Document) -> Document:
        """
        Clean a single document.
        
        Args:
            document: Document object to clean
            
        Returns:
            Cleaned Document object
        """
        cleaned_text = self._clean_text(document.content)
        
        cleaned_doc = Document(
            content=cleaned_text,
            metadata={**document.metadata, 'cleaned': True}
        )
        
        logger.debug(f"Cleaned document: {document.metadata.get('filename', 'unknown')}")
        return cleaned_doc
    
    def clean_batch(self, documents: List[Document]) -> List[Document]:
        """
        Clean multiple documents.
        
        Args:
            documents: List of Document objects
            
        Returns:
            List of cleaned Document objects
        """
        cleaned_docs = []
        for doc in documents:
            cleaned_docs.append(self.clean(doc))
        
        logger.info(f"Cleaned {len(cleaned_docs)} documents")
        return cleaned_docs
    
    def _clean_text(self, text: str) -> str:
        """
        Apply cleaning operations to text.
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        text = self._remove_headers_footers(text)
        text = self._normalize_whitespace(text)
        text = self._remove_special_characters(text)
        text = self._fix_encoding_issues(text)
        text = self._preserve_structure(text)
        
        return text.strip()
    
    def _remove_headers_footers(self, text: str) -> str:
        """Remove common header and footer patterns."""
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line_stripped = line.strip()
            
            is_header_footer = False
            for pattern in self.header_patterns + self.footer_patterns:
                if re.match(pattern, line_stripped, re.IGNORECASE):
                    is_header_footer = True
                    break
            
            if not is_header_footer:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace while preserving paragraph breaks."""
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' +\n', '\n', text)
        text = re.sub(r'\n +', '\n', text)
        
        return text
    
    def _remove_special_characters(self, text: str) -> str:
        """Remove problematic special characters."""
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
        text = text.replace('\u2022', '•')
        text = text.replace('\u2013', '-')
        text = text.replace('\u2014', '-')
        text = text.replace('\u2018', "'")
        text = text.replace('\u2019', "'")
        text = text.replace('\u201c', '"')
        text = text.replace('\u201d', '"')
        
        return text
    
    def _fix_encoding_issues(self, text: str) -> str:
        """Fix common encoding issues."""
        replacements = {
            'â€™': "'",
            'â€œ': '"',
            'â€': '"',
            'â€"': '-',
            'â€"': '-',
            'Â': '',
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text
    
    def _preserve_structure(self, text: str) -> str:
        """Preserve semantic structure like lists and sections."""
        text = re.sub(r'^(\d+\.)\s*', r'\1 ', text, flags=re.MULTILINE)
        text = re.sub(r'^([•\-\*])\s*', r'\1 ', text, flags=re.MULTILINE)
        
        return text
