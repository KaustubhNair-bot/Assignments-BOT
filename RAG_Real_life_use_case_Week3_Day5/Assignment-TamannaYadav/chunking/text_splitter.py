"""
Recursive Text Splitter for Tesla RAG system.
Implements recursive character-based text splitting with overlap.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path
import uuid

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.logger import get_logger
from config.settings import CHUNK_SIZE, CHUNK_OVERLAP, SEPARATORS
from ingestion.pdf_loader import Document

logger = get_logger(__name__)


@dataclass
class Chunk:
    """Represents a text chunk with metadata."""
    chunk_id: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.chunk_id:
            self.chunk_id = str(uuid.uuid4())


class RecursiveTextSplitter:
    """
    Recursively splits text into chunks using a hierarchy of separators.
    
    Attempts to split on larger semantic boundaries first (paragraphs),
    then falls back to smaller boundaries (sentences, words) as needed.
    """
    
    def __init__(
        self,
        chunk_size: int = CHUNK_SIZE,
        chunk_overlap: int = CHUNK_OVERLAP,
        separators: Optional[List[str]] = None
    ):
        """
        Initialize the text splitter.
        
        Args:
            chunk_size: Target size for each chunk (in characters, ~4 chars per token)
            chunk_overlap: Number of characters to overlap between chunks
            separators: List of separators to use, in order of preference
        """
        self.chunk_size = chunk_size * 4
        self.chunk_overlap = chunk_overlap * 4
        self.separators = separators or SEPARATORS
        
        logger.info(
            f"Initialized RecursiveTextSplitter with chunk_size={chunk_size} tokens, "
            f"overlap={chunk_overlap} tokens"
        )
    
    def split_document(self, document: Document) -> List[Chunk]:
        """
        Split a document into chunks.
        
        Args:
            document: Document object to split
            
        Returns:
            List of Chunk objects with metadata
        """
        text = document.content
        chunks = self._split_text(text, self.separators)
        
        chunk_objects = []
        for idx, chunk_text in enumerate(chunks):
            chunk = Chunk(
                chunk_id=f"{document.metadata.get('filename', 'doc')}_{idx}",
                content=chunk_text,
                metadata={
                    **document.metadata,
                    'chunk_index': idx,
                    'chunk_count': len(chunks),
                    'char_count': len(chunk_text)
                }
            )
            chunk_objects.append(chunk)
        
        logger.info(
            f"Split document '{document.metadata.get('filename', 'unknown')}' "
            f"into {len(chunk_objects)} chunks"
        )
        
        return chunk_objects
    
    def split_documents(self, documents: List[Document]) -> List[Chunk]:
        """
        Split multiple documents into chunks.
        
        Args:
            documents: List of Document objects
            
        Returns:
            List of all Chunk objects
        """
        all_chunks = []
        for doc in documents:
            chunks = self.split_document(doc)
            all_chunks.extend(chunks)
        
        logger.info(f"Total chunks created: {len(all_chunks)}")
        return all_chunks
    
    def _split_text(self, text: str, separators: List[str]) -> List[str]:
        """
        Recursively split text using the separator hierarchy.
        
        Args:
            text: Text to split
            separators: List of separators to try
            
        Returns:
            List of text chunks
        """
        final_chunks = []
        
        separator = separators[-1] if separators else ""
        new_separators = []
        
        for i, sep in enumerate(separators):
            if sep == "":
                separator = sep
                break
            if sep in text:
                separator = sep
                new_separators = separators[i + 1:]
                break
        
        splits = self._split_by_separator(text, separator)
        
        good_splits = []
        for split in splits:
            if len(split) < self.chunk_size:
                good_splits.append(split)
            else:
                if good_splits:
                    merged = self._merge_splits(good_splits, separator)
                    final_chunks.extend(merged)
                    good_splits = []
                
                if new_separators:
                    other_chunks = self._split_text(split, new_separators)
                    final_chunks.extend(other_chunks)
                else:
                    final_chunks.append(split)
        
        if good_splits:
            merged = self._merge_splits(good_splits, separator)
            final_chunks.extend(merged)
        
        return final_chunks
    
    def _split_by_separator(self, text: str, separator: str) -> List[str]:
        """Split text by a separator, keeping non-empty parts."""
        if separator:
            splits = text.split(separator)
            splits = [s + separator if i < len(splits) - 1 else s 
                     for i, s in enumerate(splits)]
        else:
            splits = list(text)
        
        return [s for s in splits if s.strip()]
    
    def _merge_splits(self, splits: List[str], separator: str) -> List[str]:
        """
        Merge splits into chunks of appropriate size with overlap.
        
        Args:
            splits: List of text splits
            separator: Separator used between splits
            
        Returns:
            List of merged chunks
        """
        chunks = []
        current_chunk = []
        current_length = 0
        
        for split in splits:
            split_length = len(split)
            
            if current_length + split_length > self.chunk_size and current_chunk:
                chunk_text = "".join(current_chunk).strip()
                if chunk_text:
                    chunks.append(chunk_text)
                
                while current_length > self.chunk_overlap and current_chunk:
                    removed = current_chunk.pop(0)
                    current_length -= len(removed)
            
            current_chunk.append(split)
            current_length += split_length
        
        if current_chunk:
            chunk_text = "".join(current_chunk).strip()
            if chunk_text:
                chunks.append(chunk_text)
        
        return chunks
