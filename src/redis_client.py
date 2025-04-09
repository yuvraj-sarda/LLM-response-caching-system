"""
This file abstracts away the redis client to ensure that the same redis instance is being used everywhere.
"""
import redis

redis_client = redis.Redis(
    host='redis',
    port=6379,
    decode_responses=True
) 