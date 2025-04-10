from .redis_client import redis_client

def cache_response(query: str, responseText: str) -> bool:
  return redis_client.set(query, responseText, ex=calculate_TTL(query))

def calculate_TTL(query: str) -> int:
  """
  Calculates how long a query should be cached for.
  Returns number of seconds.
  """
  MAX_TTL = 60*60*24*30 # 1 month
  return MAX_TTL