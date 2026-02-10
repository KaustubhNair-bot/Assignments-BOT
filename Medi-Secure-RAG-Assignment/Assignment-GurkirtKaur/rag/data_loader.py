"""
Data Loader Module for Medical Transcriptions
Handles loading, preprocessing, and chunking of medical text data
"""

import pandas as pd
import os
from typing import List, Dict
import re
from app.config import Config

class DataLoader:
    """Handles loading and preprocessing of medical transcription data"""
    
    def __init__(self):
        self.data_path = Config.DATA_PATH
        self.chunk_size = Config.CHUNK_SIZE
        self.chunk_overlap = Config.CHUNK_OVERLAP
    
    def load_data(self) -> pd.DataFrame:
        """
        Load medical transcriptions from CSV file
        
        Returns:
            DataFrame containing medical transcriptions
        """
        try:
            df = pd.read_csv(self.data_path)
            # Check if required columns exist
            if 'transcription' not in df.columns:
                raise ValueError("CSV file must contain 'transcription' column")
            
            # Remove rows with empty transcriptions
            df = df.dropna(subset=['transcription'])
            df = df[df['transcription'].str.strip() != '']
            
            print(f"Loaded {len(df)} medical transcriptions")
            return df
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Data file not found at {self.data_path}")
        except Exception as e:
            raise Exception(f"Error loading data: {str(e)}")
    
    def clean_text(self, text: str) -> str:
        """
        Clean and preprocess text data
        
        Args:
            text: Raw text string
            
        Returns:
            Cleaned text string
        """
        if not isinstance(text, str):
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep medical punctuation
        text = re.sub(r'[^\w\s\.,;:!?()-]', '', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks for better embedding
        
        Args:
            text: Text to chunk
            
        Returns:
            List of text chunks
        """
        if not text:
            return []
        
        # Clean the text first
        text = self.clean_text(text)
        
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # If we're not at the end, try to break at word boundary
            if end < len(text):
                # Find the last space before the chunk size limit
                last_space = text.rfind(' ', start, end)
                if last_space != -1:
                    end = last_space
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            start = max(start + 1, end - self.chunk_overlap)
        
        return chunks
    
    def prepare_documents(self) -> List[Dict]:
        """
        Load data and prepare documents with chunks
        
        Returns:
            List of dictionaries containing chunked documents with metadata
        """
        df = self.load_data()
        
        documents = []
        doc_id = 0
        
        for idx, row in df.iterrows():
            transcription = str(row['transcription'])
            
            # Create chunks
            chunks = self.chunk_text(transcription)
            
            for chunk_idx, chunk in enumerate(chunks):
                doc = {
                    'doc_id': doc_id,
                    'original_id': idx,
                    'chunk_id': chunk_idx,
                    'text': chunk,
                    'full_transcription': transcription,  # Add full transcription
                    'metadata': {
                        'medical_specialty': row.get('medical_specialty', 'Unknown'),
                        'sample_name': row.get('sample_name', f'Sample_{idx}'),
                        'keywords': row.get('keywords', ''),
                        'total_chunks': len(chunks)
                    }
                }
                documents.append(doc)
                doc_id += 1
        
        print(f"Created {len(documents)} document chunks from {len(df)} transcriptions")
        return documents
    
    def get_sample_data_info(self) -> Dict:
        """
        Get information about the loaded dataset
        
        Returns:
            Dictionary with dataset statistics
        """
        try:
            df = self.load_data()
            
            info = {
                'total_transcriptions': len(df),
                'total_characters': df['transcription'].str.len().sum(),
                'avg_transcription_length': df['transcription'].str.len().mean(),
                'medical_specialties': df.get('medical_specialty', pd.Series(['Unknown'])).value_counts().to_dict(),
                'has_keywords': 'keywords' in df.columns,
                'sample_names': df.get('sample_name', pd.Series([f'Sample_{i}' for i in range(len(df))])).tolist()[:5]
            }
            
            return info
            
        except Exception as e:
            return {'error': str(e)}
