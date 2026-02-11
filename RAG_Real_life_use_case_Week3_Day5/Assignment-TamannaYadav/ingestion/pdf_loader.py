"""
PDF Document Loader for Tesla RAG system.
Handles loading and text extraction from Tesla PDF documents.
"""

import os
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass, field

import pdfplumber

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class Document:
    """Represents a loaded document with metadata."""
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if 'source' not in self.metadata:
            self.metadata['source'] = 'unknown'


class PDFLoader:
    """
    Loads and extracts text from PDF documents.
    
    Supports loading single files or entire directories of PDFs.
    """
    
    def __init__(self, source_path: str):
        """
        Initialize the PDF loader.
        
        Args:
            source_path: Path to a PDF file or directory containing PDFs
        """
        self.source_path = Path(source_path)
        logger.info(f"Initialized PDFLoader with source: {self.source_path}")
    
    def load(self) -> List[Document]:
        """
        Load documents from the source path.
        
        Returns:
            List of Document objects with extracted text and metadata
        """
        if self.source_path.is_file():
            return [self._load_single_pdf(self.source_path)]
        elif self.source_path.is_dir():
            return self._load_directory()
        else:
            raise ValueError(f"Invalid source path: {self.source_path}")
    
    def _load_single_pdf(self, pdf_path: Path) -> Document:
        """
        Extract text from a single PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Document object with extracted text and metadata
        """
        logger.info(f"Loading PDF: {pdf_path.name}")
        
        pages_text = []
        page_count = 0
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                page_count = len(pdf.pages)
                
                for page_num, page in enumerate(pdf.pages, start=1):
                    text = page.extract_text()
                    if text:
                        pages_text.append({
                            'page_number': page_num,
                            'text': text
                        })
                        
            full_text = "\n\n".join([p['text'] for p in pages_text])
            
            metadata = {
                'source': str(pdf_path),
                'filename': pdf_path.name,
                'page_count': page_count,
                'pages': pages_text
            }
            
            logger.info(f"Successfully extracted {len(full_text)} characters from {pdf_path.name}")
            
            return Document(content=full_text, metadata=metadata)
            
        except Exception as e:
            logger.error(f"Error loading PDF {pdf_path}: {e}")
            raise
    
    def _load_directory(self) -> List[Document]:
        """
        Load all PDF files from a directory.
        
        Returns:
            List of Document objects
        """
        documents = []
        pdf_files = list(self.source_path.glob("*.pdf"))
        
        logger.info(f"Found {len(pdf_files)} PDF files in {self.source_path}")
        
        for pdf_path in pdf_files:
            try:
                doc = self._load_single_pdf(pdf_path)
                documents.append(doc)
            except Exception as e:
                logger.warning(f"Skipping {pdf_path.name} due to error: {e}")
                continue
        
        logger.info(f"Successfully loaded {len(documents)} documents")
        return documents
