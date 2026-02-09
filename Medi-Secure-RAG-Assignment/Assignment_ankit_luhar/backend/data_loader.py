import pandas as pd
from langchain_community.document_loaders import DataFrameLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .rag_system import rag
import os

def load_data(file_path: str = "data/mtsamples.csv"):
    if not os.path.exists(file_path):
        print(f"File {file_path} not found. Please place the dataset in the data folder.")
        return

    print("Loading data...")
    df = pd.read_csv(file_path)
    
    
    if 'transcription' not in df.columns:
        print("Dataset missing 'transcription' column.")
        return
        
    df = df.dropna(subset=['transcription'])
    

    df = df.fillna("")
    

    df = df.head(100) 

    loader = DataFrameLoader(df, page_content_column="transcription")
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_documents(documents)

    print(f"Embedding and upserting {len(texts)} chunks to Pinecone...")
    rag.vectorstore.add_documents(texts)
    print("Data loading complete!")

if __name__ == "__main__":
    load_data()
