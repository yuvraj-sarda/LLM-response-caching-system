from src.redis_client import redis_client
import os
import uuid
from src.utils.get_embeddings import get_embedding

def cache_response(query: str, response_text: str) -> bool:
    if os.getenv("DISABLE_AUTO_CACHE") == "TRUE":
        return False
    
    redis_client.set(query, response_text, ex=calculate_TTL(query))
    return True

def calculate_TTL(query: str) -> int:
    """
    Calculates how long a query should be cached for.
    Returns number of seconds.
    """
    MAX_TTL = 60*60*24*30 # 1 month
    # TODO: implement this. This is tricky. One approach is to look for specific sets of keywords (eg: "today", "this week", "current" etc) and use that to calculate a more specific TTL.
    return MAX_TTL

## I was trying to implement a vector embedding cache, but it's not working as expected. Some issue with syncing with redis.
# def cache_response_with_vector_embedding(query: str, response_text: str) -> bool:
#     if os.getenv("DISABLE_AUTO_CACHE") == "TRUE":
#         return False
#     # Get embedding for the query
#     query_embedding = get_embedding(query)
    
#     # Create a unique ID for this cache entry
#     cache_id = str(uuid.uuid4())
    
#     # Create a JSON object with query, response, and embedding
#     cache_data = {
#         "id": cache_id,
#         "query": query,
#         "response": response_text,
#         "query_embedding": query_embedding
#     }
    
#     # Store in Redis with vector_cache prefix and unique ID
#     key = f"vector_cache:{cache_id}"
#     redis_client.json().set(key, "$", cache_data)
#     redis_client.expire(key, calculate_TTL(query))
    
#     return True