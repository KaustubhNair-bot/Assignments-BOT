from langchain_text_splitters import RecursiveCharacterTextSplitter
from config.settings import CHUNK_SIZE, CHUNK_OVERLAP

def split_documents(documents):
    """
    Splits a list of Document objects into smaller chunks.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    
    chunks = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")
    return chunks

if __name__ == "__main__":
    from rag.loader import load_documents
    docs = load_documents()
    chunks = split_documents(docs)
    if chunks:
        print(f"Sample chunk: {chunks[0].page_content[:100]}...")
