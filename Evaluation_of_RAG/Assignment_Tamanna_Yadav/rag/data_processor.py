"""Data processing for medical transcriptions."""
import pandas as pd
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
from tqdm import tqdm
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import settings
from .chunker import TextChunker


class DataProcessor:
    """
    Processes medical transcription data for indexing.
    Implements privacy-preserving transformations.
    """
    
    def __init__(self, data_path: Path = None):
        """
        Initialize the data processor.
        
        Args:
            data_path: Path to the CSV file
        """
        self.data_path = data_path or settings.RAW_DATA_PATH
        self.df: Optional[pd.DataFrame] = None
    
    def load_data(self) -> pd.DataFrame:
        """Load the medical transcriptions dataset."""
        self.df = pd.read_csv(self.data_path)
        print(f"Loaded {len(self.df)} records from {self.data_path}")
        return self.df
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize transcription text.
        
        Args:
            text: Raw transcription text
            
        Returns:
            Cleaned text
        """
        if pd.isna(text):
            return ""
        
        text = str(text)
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
    
    def anonymize_text(self, text: str) -> str:
        """
        Remove or mask potential patient identifiers.
        This is a basic implementation - production systems would use
        more sophisticated NER-based de-identification.
        
        Args:
            text: Input text
            
        Returns:
            Anonymized text
        """
        text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', text)
        
        text = re.sub(r'\b\d{3}[-]?\d{2}[-]?\d{4}\b', '[SSN]', text)
        
        text = re.sub(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            '[EMAIL]',
            text
        )
        
        text = re.sub(
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            '[DATE]',
            text
        )
        
        return text
    
    def process_transcriptions(
        self, 
        anonymize: bool = True, 
        deduplicate: bool = True,
        apply_chunking: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Process all transcriptions for indexing.
        
        Args:
            anonymize: Whether to apply anonymization
            deduplicate: Whether to remove duplicate transcriptions
            apply_chunking: Whether to chunk long transcriptions
            
        Returns:
            List of processed document dictionaries
            
        Chunking Strategy:
        - Long transcriptions are split into smaller chunks
        - Uses recursive splitting with semantic boundaries
        - Overlap between chunks preserves context
        - Why: Improves retrieval precision for long documents
        """
        if self.df is None:
            self.load_data()
        
        documents = []
        seen_transcriptions = set()
        
        for idx, row in tqdm(self.df.iterrows(), total=len(self.df), desc="Processing transcriptions"):
            transcription = self.clean_text(row.get('transcription', ''))
            
            if not transcription or len(transcription) < 50:
                continue
            
            if deduplicate:
                trans_hash = hash(transcription[:500])
                if trans_hash in seen_transcriptions:
                    continue
                seen_transcriptions.add(trans_hash)
            
            if anonymize:
                transcription = self.anonymize_text(transcription)
            
            doc = {
                "id": int(idx),
                "transcription": transcription,
                "description": self.clean_text(row.get('description', '')),
                "medical_specialty": str(row.get('medical_specialty', 'Unknown')).strip(),
                "sample_name": self.clean_text(row.get('sample_name', '')),
                "keywords": self.clean_text(row.get('keywords', ''))
            }
            
            documents.append(doc)
        
        print(f"Processed {len(documents)} unique transcriptions (removed {len(self.df) - len(documents)} duplicates)")
        
        if apply_chunking:
            chunker = TextChunker(
                chunk_size=getattr(settings, 'CHUNK_SIZE', 512),
                chunk_overlap=getattr(settings, 'CHUNK_OVERLAP', 50),
                min_chunk_size=getattr(settings, 'MIN_CHUNK_SIZE', 100)
            )
            documents = chunker.chunk_documents(documents)
        
        return documents
    
    def get_text_for_embedding(self, doc: Dict[str, Any]) -> str:
        """
        Create the text representation for embedding.
        Combines relevant fields for better semantic search.
        
        Args:
            doc: Document dictionary
            
        Returns:
            Combined text for embedding
        """
        parts = []
        
        if doc.get('medical_specialty'):
            parts.append(f"Specialty: {doc['medical_specialty']}")
        
        if doc.get('description'):
            parts.append(f"Summary: {doc['description']}")
        
        if doc.get('transcription'):
            parts.append(doc['transcription'])
        
        return " ".join(parts)
