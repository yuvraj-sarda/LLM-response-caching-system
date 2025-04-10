import os
from .redis_client import redis_client

async def query_cache(query: str) -> str | None:
  """
  Depending on the CACHING_STRATEGY set in the .env file, checks if there is a reusable query in the cache.
  """
  strategy = os.environ.get("CACHING_STRATEGY")
  
  match strategy:
    case "no_cache":
      return None
    
    case "exact_match_only":
      return await redis_client.get(query)
    
    # Add more cases
    # * Small local LLM cache
    # * Vector embedding cache
    # * Hybrid cache
    
    case _:
      print(f"The caching strategy was not set, or is unknown: {strategy}. Using default")
      result = await redis_client.get(query)
