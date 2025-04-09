from redis_client import redis_client

async def query_cache(query: str) -> str | None:
    return redis_client.get(query)