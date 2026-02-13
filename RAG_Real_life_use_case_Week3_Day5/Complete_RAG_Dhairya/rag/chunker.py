from pathlib import Path
from typing import List, Dict
from .config import CHUNK_SIZE, CHUNK_OVERLAP
from .metadata import MANUAL_METADATA

def split_text(text: str) -> List[str]:
    if len(text) <= CHUNK_SIZE:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + CHUNK_SIZE

        if end >= len(text):
            chunks.append(text[start:].strip())
            break

        chunk = text[start:end]
        sentence_end = chunk.rfind('.')

        if sentence_end > CHUNK_SIZE * 0.7:
            chunks.append(chunk[:sentence_end+1])
            start = start + sentence_end + 1 - CHUNK_OVERLAP
        else:
            chunks.append(chunk)
            start = end - CHUNK_OVERLAP

    return chunks

def create_chunks(text: str, filename: str) -> List[Dict]:
    metadata = MANUAL_METADATA.get(filename, {})
    chunk_texts = split_text(text)

    chunks = []
    for i, chunk_text in enumerate(chunk_texts):
        chunks.append({
            "chunk_id": f"{Path(filename).stem}_chunk_{i+1}",
            "text": chunk_text,
            "metadata": metadata
        })
    return chunks
