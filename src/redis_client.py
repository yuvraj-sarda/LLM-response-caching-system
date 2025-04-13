"""
This file abstracts away the redis client to ensure that the same redis instance is being used everywhere.
"""
import os
import redis
from redis.commands.search.field import VectorField, TextField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query

# Initialize Redis client
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'redis'), # This approach allows the redis host to be set to localhost too, which enables objects outside the docker container to interact with it too (useful for quickly running tests).
    port=6379,
    decode_responses=True
)


# TODO: I was trying to implement a vector embedding cache, but it's not working as expected. Some issue with syncing with redis.
# def create_vector_index() -> str:
#     """
#     Creates the vector index if it doesn't already exist.
    
#     Args:
#         index_name: The name of the index to create (default: "idx:vector_cache")
#     """
#     index_name = "idx:vector_cache"
    
#     # Check if index already exists
#     try:
#         redis_client.ft(index_name).info()
#         return index_name  # Index exists, no need to create it
#     except redis.ResponseError as e:
#         expected_error: bool = "Unknown index name" in str(e)
#         if not expected_error:
#             raise e
    
#     # Define the schema for our vector index
#     schema = (
#         TextField("$.id", as_name="id"),
#         TextField("$.query", as_name="query"),
#         TextField("$.response", as_name="response"),
#         VectorField(
#             "$.query_embedding",
#             "FLAT",
#             {
#                 "TYPE": "FLOAT32",
#                 "DIM": 384,  # all-MiniLM-L6-v2 dimension
#                 "DISTANCE_METRIC": "COSINE",
#             },
#             as_name="query_embedding",
#         ),
#     )
    
#     definition = IndexDefinition(prefix=["vector_cache:"], index_type=IndexType.JSON)
    
#     # Create the index
#     redis_client.ft(index_name).create_index(
#         fields=schema,
#         definition=definition
#     )
#     return index_name

# create_vector_index() 