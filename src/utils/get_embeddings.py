# TODO: I was trying to implement a vector embedding cache, but it's not working as expected. Some issue with syncing with redis.
# So, this is not in use at the moment.

# from sentence_transformers import SentenceTransformer
# import numpy as np

# # Initialize the model
# embedder = SentenceTransformer("msmarco-distilbert-base-v4")

# def get_embedding(text: str) -> list[float]:
#     """Get embedding for a text using Hugging Face's sentence-transformers."""
#     return embedder.encode(text).astype(np.float32).tolist()