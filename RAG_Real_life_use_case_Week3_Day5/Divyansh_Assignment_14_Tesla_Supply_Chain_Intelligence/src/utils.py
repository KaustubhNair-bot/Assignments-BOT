import pymupdf4llm
import os


def process_pdfs(data_path):
    all_text = ""
    for file in os.listdir(data_path):
        if file.endswith(".pdf"):
            md_text = pymupdf4llm.to_markdown(os.path.join(data_path, file))
            all_text += md_text

    # Native Chunking (3x Logic: Split by double newline, join until 1000 chars)
    # This is better because it respects paragraph breaks
    raw_chunks = all_text.split("\n\n")
    final_chunks = []
    current_chunk = ""

    for p in raw_chunks:
        if len(current_chunk) + len(p) < 1000:
            current_chunk += p + "\n\n"
        else:
            final_chunks.append(current_chunk.strip())
            current_chunk = p + "\n\n"
    if current_chunk:
        final_chunks.append(current_chunk.strip())

    return final_chunks
