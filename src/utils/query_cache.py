import os
import re
import numpy as np
from src.utils.redis_client import redis_client
# from src.utils.get_embeddings import get_embedding
from redis.commands.search.query import Query

async def query_cache(query: str) -> str | None:
  """
  Depending on the CACHING_STRATEGY set in the .env file, checks if there is a reusable query in the cache.
  """
  strategy = os.environ.get("CACHING_STRATEGY")
  
  match strategy:
    case "no_cache":
      return None
    
    case "exact_match_only":
      cached_item = redis_client.get(query)
      return cached_item
    
    # Add more cases
    # * Small local LLM cache
    # * Vector embedding cache
    # * Hybrid cache
    
    case _:
      print(f"The caching strategy was not set, or is unknown: {strategy}. Using default")
      return redis_client.get(query)


# I was trying to implement vector embedding cache, but it's not working as expected. Some issue with syncing with redis.
# async def query_cache_advanced(query: str) -> str | None:
#   """
#   Depending on the CACHING_STRATEGY set in the .env file, checks if there is a reusable query in the cache.
#   """
#   strategy = os.environ.get("CACHING_STRATEGY")
  
#   match strategy:
#     case "no_cache":
#       return None
    
#     case "exact_match_only":
#       cached_item = redis_client.json().get(query, "$.response")
#       return cached_item
    
#     case "cleaned_match":
#       cleaned_query = clean_query(query)
#       # TODO: simple retrieval wont work, need to use fuzzy search and redis
#       cached_item = redis_client.json().get(cleaned_query, "$.response")
#       return cached_item
    
#     case "vector_embedding":
#         # Get embedding for the query and perform vector search
#         query_embedding = get_embedding(query)
#         return perform_vector_search(query_embedding)
    
#     # Add more cases
#     # * Small local LLM cache
#     # * Vector embedding cache
#     # * Hybrid cache
    
#     case _:
#       print(f"The caching strategy was not set, or is unknown: {strategy}. Using default")
#       return redis_client.json().get(query, "$.response")

# def clean_query(query: str) -> str:
#     # Convert to lowercase
#     cleaned_query = query.lower()
    
#     # Remove special characters, keeping only alphanumeric and spaces
#     cleaned_query = re.sub(r'[^a-z0-9\s]', '', cleaned_query)
    
#     # Remove extra whitespace
#     cleaned_query = ' '.join(cleaned_query.split())
    
#     return cleaned_query

# def perform_vector_search(query_embedding: list[float], similarity_threshold: float = 0.85) -> str | None:
#     """
#     Performs vector similarity search in Redis and returns the best matching response if found.
    
#     Args:
#         query_embedding: The embedding vector of the query
#         similarity_threshold: Minimum cosine similarity required for a match (default: 0.85)
    
#     Returns:
#         The cached response if a sufficiently similar query is found, None otherwise
#     """
#     # Convert embedding to bytes for Redis
#     query_embedding_bytes = np.array(query_embedding, dtype=np.float32).tobytes()
    
#     # Create vector search query
#     query = (
#         Query(f"(*)=>[KNN 3 @query_embedding $vector AS vector_score]")
#         .sort_by("vector_score")
#         .return_fields("response", "vector_score")
#         .dialect(2)
#     )
    
#     # Execute vector search
#     results = redis_client.ft("idx:vector_cache").search(
#         query,
#         query_params={"vector": query_embedding_bytes}
#     )
    
#     # If we have results and the best match is close enough
#     if results.docs and (1 - float(results.docs[0].vector_score)) >= similarity_threshold:
#         return results.docs[0].response
    
#     return None
