import chromadb
from chromadb.utils import embedding_functions
import os
from dotenv import load_dotenv

# Load our .env
load_dotenv()
DB_PATH = os.getenv("CHROMA_DB_PATH")


def get_vector_db_collection(df=None):
    """
    Initializes or loads the Vector Database.
    """
    # 1. Setup Persistence (Saving to disk)
    # We use a persistent client so we don't re-index every time we start the app
    client = chromadb.PersistentClient(path=DB_PATH)

    # 2. Choose the 'Translator' (Embedding Function)
    # We use 'all-MiniLM-L6-v2'. It's fast, small, and runs locally.
    emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    # 3. Create/Get the Collection
    collection = client.get_or_create_collection(
        name="medical_transcriptions", embedding_function=emb_fn
    )

    # 4. Populate if Empty
    if df is not None and collection.count() == 0:
        # We prepare lists for the DB
        documents = df["clean_transcription"].tolist()

        # Metadata allows us to filter! We store Specialty and Description
        metadatas = [
            {"specialty": row["medical_specialty"], "description": row["description"]}
            for _, row in df.iterrows()
        ]

        # IDs must be unique strings
        ids = [str(i) for i in range(len(documents))]

        # Add to database in batches
        # We do this so the memory doesn't overflow if the CSV is huge
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            collection.add(
                documents=documents[i : i + batch_size],
                metadatas=metadatas[i : i + batch_size],
                ids=ids[i : i + batch_size],
            )

    return collection


def query_similar_cases(collection, query_text, n_results=3):
    """
    Search function that finds the most relevant past cases.
    """
    results = collection.query(query_texts=[query_text.lower()], n_results=n_results)
    return results
