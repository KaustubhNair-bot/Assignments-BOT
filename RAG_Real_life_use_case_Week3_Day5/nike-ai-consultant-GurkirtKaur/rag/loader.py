"""
Document Loader Module - PDF-based
Loads HR policy documents from PDF files and extracts text for RAG pipeline.
"""
import os
import glob
import pdfplumber
from langchain_community.docstore.document import Document
from config.settings import DATA_DIR


def load_documents():
    """
    Loads all PDF files from the configured DATA_DIR and extracts text.
    
    This function:
    1. Finds all .pdf files in the data directory
    2. Extracts text from each page using pdfplumber
    3. Combines pages into a single document per PDF
    4. Returns LangChain Document objects with metadata
    
    Returns:
        list: List of LangChain Document objects with extracted text and metadata
    """
    docs = []
    pdf_files = glob.glob(os.path.join(DATA_DIR, "*.pdf"))
    
    print(f"Loading PDF files from {DATA_DIR}...")
    
    for pdf_path in pdf_files:
        try:
            # Extract text from PDF using pdfplumber
            full_text = extract_text_from_pdf(pdf_path)
            
            # Create LangChain Document object
            doc = Document(
                page_content=full_text,
                metadata={
                    "source": pdf_path,
                    "filename": os.path.basename(pdf_path)
                }
            )
            
            docs.append(doc)
            print(f"✓ Loaded: {os.path.basename(pdf_path)} ({len(full_text)} characters)")
            
        except Exception as e:
            print(f"✗ Error loading {pdf_path}: {e}")
    
    print(f"\nTotal documents loaded: {len(docs)}")
    return docs


def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF file using pdfplumber.
    
    Handles multi-page PDFs by:
    - Looping through all pages
    - Extracting text from each page
    - Combining with page separators for clean formatting
    
    Args:
        pdf_path: Absolute path to PDF file
        
    Returns:
        str: Extracted text from all pages combined
    """
    text_content = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            # Extract text from current page
            page_text = page.extract_text()
            
            if page_text:
                # Clean up text: remove excessive whitespace
                page_text = page_text.strip()
                text_content.append(page_text)
                print(f"  Page {page_num}: {len(page_text)} characters")
    
    # Combine all pages with double newline separator
    full_text = "\n\n".join(text_content)
    
    return full_text


if __name__ == "__main__":
    # Test the loader
    documents = load_documents()
    
    if documents:
        print("\n" + "="*50)
        print("SAMPLE OUTPUT (First 500 characters):")
        print("="*50)
        print(documents[0].page_content[:500])
        print("...")
    else:
        print("\nNo documents loaded. Please add PDF files to the data directory.")
