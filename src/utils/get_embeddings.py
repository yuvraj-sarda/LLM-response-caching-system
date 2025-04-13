from sentence_transformers import SentenceTransformer
import numpy as np

# Initialize the model
embedder = SentenceTransformer("msmarco-distilbert-base-v4")

def get_embedding(text: str) -> list[float]:
    """Get embedding for a text using Hugging Face's sentence-transformers."""
    return embedder.encode(text).astype(np.float32).tolist()