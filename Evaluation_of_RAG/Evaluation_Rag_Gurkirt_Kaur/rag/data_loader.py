"""
Data Loader Module for Medical Transcriptions
Handles loading, preprocessing, and chunking of medical text data
"""

import pandas as pd
import os
from typing import List, Dict
import re
import spacy
from app.config import Config

# Load Spacy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Spacy model not found. Downloading...")
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

class DataLoader:
    """Handles loading and preprocessing of medical transcription data"""
    
    def __init__(self):
        self.data_path = Config.DATA_PATH
        # For semantic chunking, we might not strictly use CHUNK_SIZE as a hard character limit in the same way,
        # but we can use it to guide the window size or aggregation
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
            # FOR EVALUATION SPEED: Limit to 50 samples (Commented out for production)
            # df = df.head(50)
            # print(f"Reduced to {len(df)} sample transcriptions for evaluation")
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
        # Keeping fewer restrictions might be better for BioBERT but let's stick to safe clean
        text = re.sub(r'[^\w\s\.,;:!?()-]', '', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into semantic chunks using Spacy (sentence-based sliding window)
        
        Args:
            text: Text to chunk
            
        Returns:
            List of text chunks
        """
        if not text:
            return []
        
        # Clean the text first
        text = self.clean_text(text)
        
        doc = nlp(text)
        sentences = [sent.text for sent in doc.sents]
        
        if not sentences:
            return []

        chunks = []
        current_chunk = []
        current_length = 0
        
        # Simple sliding window of sentences approach
        # We aggregate sentences until we hit the chunk size, then overlap.
        # However, the user request specifically asked for:
        # "Implement a sliding window strategy to break text into meaningful chunks."
        # The prompt proposed code was:
        # window_size=500 (tokens?) -> doc[i:i+window_size]
        # Let's align with the prompt's idea of a window over tokens/text but respects sentence boundaries if possible,
        # OR just use the prompt's spacy token window approach if it's cleaner.
        # The prompt's code:
        # doc = nlp(text)
        # for i in range(0, len(doc), window_size):
        #    chunk = doc[i:i+window_size]
        
        # Let's use a robust approach: Group sentences.
        
        # Use a window of generic size (e.g. 512 tokens approx or characters)
        # BioBERT limit is 512 tokens. 
        # Config.CHUNK_SIZE is 500 chars (from config). 500 chars is small.
        # Let's assume Config.CHUNK_SIZE is intended to be *token* count for BioBERT or char count.
        # Given BioBERT, 512 tokens is valid. 500 chars is ~100 tokens. 
        # Let's aim for chunks of ~200-300 tokens to allow context and fit in 512.
        
        # Implementing the sliding window as requested in the Prompt Code Reference, but adjusted for the Config.
        # The prompt's reference code:
        #   def chunk_text(text, window_size=500):
        #       doc = nlp(text)
        #       ... for i in range(0, len(doc), window_size) ...
        
        # We will use that logic but ensure we convert span back to text.
        
        # Adjust window_size to be reasonable for BioBERT. 100-200 tokens is good for retrieval.
        # The prompt suggested window_size=500. 500 tokens is close to max 512.
        # Let's use a stride/overlap.
        
        window_size = 300 # tokens, safe for BioBERT (512 limit) and context
        stride = 200 # Overlap of 100 tokens
        
        # If the text is short
        if len(doc) <= window_size:
            return [text]
            
        for i in range(0, len(doc), stride):
            # Create span
            span = doc[i : i + window_size]
            
            # If span is too short (tail end) and we already have chunks, maybe merge or drop?
            # But let's just keep it.
            if len(span) > 0:
                chunks.append(span.text)
            
            if i + window_size >= len(doc):
                break
                
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
