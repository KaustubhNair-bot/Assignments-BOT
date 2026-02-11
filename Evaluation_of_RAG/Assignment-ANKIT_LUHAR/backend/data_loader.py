"""Load the mtsamples.csv dataset into the Pinecone vector store.

Usage (from project root):
    python -m backend.data_loader
"""

from __future__ import annotations

import os
import sys

import pandas as pd
from langchain_community.document_loaders import DataFrameLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .rag_system import rag


def load_data(file_path: str = "data/mtsamples.csv", max_rows: int = 100):
    """Read CSV, chunk the transcriptions, and upsert into the vector store."""

    if not os.path.exists(file_path):
        print(f"[DataLoader] File '{file_path}' not found.")
        print("             Place mtsamples.csv inside the data/ folder.")
        return

    print(f"[DataLoader] Reading {file_path} …")
    df = pd.read_csv(file_path)

    if "transcription" not in df.columns:
        print("[DataLoader] ERROR — dataset is missing a 'transcription' column.")
        return

    df = df.dropna(subset=["transcription"])
    df = df.fillna("")  # avoid Pinecone metadata errors
    df = df.head(max_rows)

    print(f"[DataLoader] {len(df)} rows selected for embedding.")

    loader = DataFrameLoader(df, page_content_column="transcription")
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = splitter.split_documents(documents)

    print(f"[DataLoader] Upserting {len(chunks)} chunks into vector store …")
    try:
        rag.vectorstore.add_documents(chunks)
    except Exception as exc:
        print(f"[DataLoader] Upsert error: {exc}")
        raise
    print("[DataLoader] Done ✓")


if __name__ == "__main__":
    load_data()
