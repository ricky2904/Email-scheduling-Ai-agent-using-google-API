import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# Setup Chroma client
client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory=".chroma"  # Local directory to store memory
))

# Create or load collection
collection = client.get_or_create_collection(name="email_events")

# Sentence transformer for generating embeddings
embedder = SentenceTransformer("all-MiniLM-L6-v2")  # You can switch to a larger model if needed

def check_duplicate(subject: str, snippet: str, threshold: float = 0.85) -> bool:
    """
    Check if a similar email (subject + snippet) was already processed.
    Returns True if a near-duplicate is found.
    """
    text = f"{subject} {snippet}"
    embedding = embedder.encode([text]).tolist()

    try:
        results = collection.query(query_embeddings=embedding, n_results=1)
        if results['documents']:
            score = results['distances'][0][0]
            print(f"🔎 Similarity score: {1 - score:.4f}")
            if score <= 1 - threshold:  # cosine distance: lower is more similar
                return True
    except Exception as e:
        print(f"⚠️ ChromaDB query failed: {e}")
    return False

def store_event(subject: str, snippet: str, metadata: dict):
    """
    Store a new email + extracted metadata into Chroma memory.
    """
    text = f"{subject} {snippet}"
    embedding = embedder.encode([text]).tolist()
    try:
        collection.add(
            documents=[text],
            embeddings=embedding,
            ids=[metadata["id"]],
            metadatas=[metadata]
        )
        print(f"✅ Stored event to memory: {metadata['id']}")
    except Exception as e:
        print(f"❌ Failed to store event in memory: {e}")
