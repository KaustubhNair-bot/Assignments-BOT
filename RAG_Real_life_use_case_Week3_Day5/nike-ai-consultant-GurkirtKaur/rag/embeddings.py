from langchain_community.embeddings import SentenceTransformerEmbeddings
from config.settings import EMBEDDING_MODEL_NAME

def get_embedding_model():
    """
    Returns the configured HuggingFace embedding model.
    """
    print(f"Loading embedding model: {EMBEDDING_MODEL_NAME}...")
    embeddings = SentenceTransformerEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    return embeddings

if __name__ == "__main__":
    model = get_embedding_model()
    vec = model.embed_query("Just do it.")
    print(f"Embedding generated. Dimension: {len(vec)}")
