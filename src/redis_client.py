"""
This file abstracts away the redis client to ensure that the same redis instance is being used everywhere.
"""
import os
import redis

redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'redis'), # This approach allows the redis host to be set to localhost too, which enables objects outside the docker container to interact with it too (useful for quickly running tests).
    port=6379,
    decode_responses=True
) 