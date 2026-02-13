from pathlib import Path
from rag.pdf_loader import extract_text_from_pdf
from rag.chunker import create_chunks
from rag.vector_store import add_chunks, collection_has_data

def ingest_all():
    if collection_has_data():
        print("✅ Vector store already populated. Skipping ingestion.")
        return

    print("🚀 No data found in vector store. Starting ingestion...")

    pdf_dir = Path("data/raw")
    all_chunks = []

    for pdf in pdf_dir.glob("*.pdf"):
        print(f"Processing: {pdf.name}")
        text = extract_text_from_pdf(str(pdf))
        chunks = create_chunks(text, pdf.name)
        all_chunks.extend(chunks)

    add_chunks(all_chunks)
    print("🎉 Ingestion complete!")


if __name__ == "__main__":
    ingest_all()
