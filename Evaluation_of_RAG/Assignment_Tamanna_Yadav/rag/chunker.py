"""Text chunking strategies for medical transcriptions."""
from typing import List, Dict, Any
import re


class TextChunker:
    """
    Implements chunking strategies for medical transcriptions.
    
    Why Chunking Matters:
    - Long transcriptions may exceed embedding model's context window
    - Smaller chunks improve retrieval precision
    - Overlapping chunks preserve context at boundaries
    """
    
    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        min_chunk_size: int = 100
    ):
        """
        Initialize the chunker.
        
        Args:
            chunk_size: Target size for each chunk (in characters)
            chunk_overlap: Overlap between consecutive chunks
            min_chunk_size: Minimum chunk size to keep
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
    
    def recursive_split(self, text: str) -> List[str]:
        """
        Recursively split text using semantic boundaries.
        
        Strategy:
        1. Try to split on paragraph breaks (double newline)
        2. Then on sentence boundaries (. ! ?)
        3. Then on clause boundaries (, ; :)
        4. Finally on word boundaries (space)
        
        This preserves semantic meaning better than fixed-size splitting.
        
        Args:
            text: Input text to split
            
        Returns:
            List of text chunks
        """
        if len(text) <= self.chunk_size:
            return [text] if len(text) >= self.min_chunk_size else []
        
        separators = [
            "\n\n",      # Paragraph breaks
            "\n",        # Line breaks
            ". ",        # Sentence endings
            "? ",        # Questions
            "! ",        # Exclamations
            "; ",        # Semicolons
            ", ",        # Commas
            " ",         # Words
        ]
        
        chunks = []
        current_chunk = ""
        
        for separator in separators:
            if separator in text:
                parts = text.split(separator)
                
                for part in parts:
                    part_with_sep = part + separator if separator != " " else part + " "
                    
                    if len(current_chunk) + len(part_with_sep) <= self.chunk_size:
                        current_chunk += part_with_sep
                    else:
                        if current_chunk and len(current_chunk.strip()) >= self.min_chunk_size:
                            chunks.append(current_chunk.strip())
                        
                        if len(part_with_sep) > self.chunk_size:
                            sub_chunks = self.recursive_split(part)
                            chunks.extend(sub_chunks)
                            current_chunk = ""
                        else:
                            overlap_text = self._get_overlap(current_chunk)
                            current_chunk = overlap_text + part_with_sep
                
                if current_chunk and len(current_chunk.strip()) >= self.min_chunk_size:
                    chunks.append(current_chunk.strip())
                
                return chunks
        
        return self._fixed_size_split(text)
    
    def _get_overlap(self, text: str) -> str:
        """Get the overlap portion from the end of text."""
        if len(text) <= self.chunk_overlap:
            return text
        return text[-self.chunk_overlap:]
    
    def _fixed_size_split(self, text: str) -> List[str]:
        """Fallback to fixed-size splitting with overlap."""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]
            
            if len(chunk.strip()) >= self.min_chunk_size:
                chunks.append(chunk.strip())
            
            start = end - self.chunk_overlap
        
        return chunks
    
    def chunk_document(self, doc: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Chunk a document and create new document entries for each chunk.
        
        Args:
            doc: Original document dictionary
            
        Returns:
            List of chunked document dictionaries
        """
        transcription = doc.get("transcription", "")
        
        if len(transcription) <= self.chunk_size:
            return [doc]
        
        chunks = self.recursive_split(transcription)
        
        chunked_docs = []
        for i, chunk in enumerate(chunks):
            chunked_doc = {
                "id": f"{doc.get('id', 0)}_{i}",
                "original_id": doc.get("id", 0),
                "chunk_index": i,
                "total_chunks": len(chunks),
                "transcription": chunk,
                "description": doc.get("description", ""),
                "medical_specialty": doc.get("medical_specialty", "Unknown"),
                "sample_name": doc.get("sample_name", ""),
                "keywords": doc.get("keywords", "")
            }
            chunked_docs.append(chunked_doc)
        
        return chunked_docs
    
    def chunk_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Chunk multiple documents.
        
        Args:
            documents: List of document dictionaries
            
        Returns:
            List of chunked document dictionaries
        """
        all_chunks = []
        
        for doc in documents:
            chunks = self.chunk_document(doc)
            all_chunks.extend(chunks)
        
        print(f"Chunked {len(documents)} documents into {len(all_chunks)} chunks")
        return all_chunks


class SentenceChunker(TextChunker):
    """
    Sentence-based chunking that groups sentences together.
    Better for medical text where sentence boundaries are meaningful.
    """
    
    def __init__(
        self,
        sentences_per_chunk: int = 5,
        overlap_sentences: int = 1,
        min_chunk_size: int = 100
    ):
        """
        Initialize sentence-based chunker.
        
        Args:
            sentences_per_chunk: Number of sentences per chunk
            overlap_sentences: Number of overlapping sentences
            min_chunk_size: Minimum chunk size to keep
        """
        super().__init__(min_chunk_size=min_chunk_size)
        self.sentences_per_chunk = sentences_per_chunk
        self.overlap_sentences = overlap_sentences
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        sentence_pattern = r'(?<=[.!?])\s+'
        sentences = re.split(sentence_pattern, text)
        return [s.strip() for s in sentences if s.strip()]
    
    def recursive_split(self, text: str) -> List[str]:
        """Split text by sentences with overlap."""
        sentences = self._split_into_sentences(text)
        
        if len(sentences) <= self.sentences_per_chunk:
            return [text] if len(text) >= self.min_chunk_size else []
        
        chunks = []
        start = 0
        
        while start < len(sentences):
            end = min(start + self.sentences_per_chunk, len(sentences))
            chunk_sentences = sentences[start:end]
            chunk = " ".join(chunk_sentences)
            
            if len(chunk) >= self.min_chunk_size:
                chunks.append(chunk)
            
            start = end - self.overlap_sentences
            if start >= len(sentences) - 1:
                break
        
        return chunks
