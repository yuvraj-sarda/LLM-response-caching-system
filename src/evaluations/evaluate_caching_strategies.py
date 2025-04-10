"""
To run this script:
docker compose up -d
REDIS_HOST=localhost python -m src.evaluations.evaluate_caching_strategies
"""

import pandas as pd
import time
import os
import asyncio
from src.server import handle_query, QueryRequest
from src.redis_client import redis_client


def calculate_cost(queryText: str, responseText: str, source: str) -> float:
    """Calculate the cost of a request based on its source and query length."""
    match source:
      case "cache":
        return 0.0 # Cache hits are free
      case "llm":
        # TODO: there's definitely a better way of getting costs directly from openai.
        # GPT-4 pricing: $0.03 per 1K tokens for input, $0.06 per 1K tokens for output
        # Rough estimate: 1 token ~= 4 characters
        input_tokens = len(queryText) / 4
        # Assume output is roughly same length as input
        output_tokens = len(queryText) / 4
        return (input_tokens * 0.03 + output_tokens * 0.06) / 1000
      case _:
        print("ERR: unsupported cache source")
        return 0.0

async def evaluate_strategy(strategy: str, test_queries: pd.DataFrame) -> pd.DataFrame:
    print(f"\nTesting strategy: {strategy}")
    os.environ["CACHING_STRATEGY"] = strategy
    test_queries[strategy + '_response_time'] = 0.0
    test_queries[strategy + '_cost'] = 0.0
    test_queries[strategy + '_cache_hit_correctly'] = False

    for index, row in test_queries.iterrows():
        queryText = row["QueryText"]
        expected_cache_hit = bool(row["ExpectedCacheHit"])
        
        # Time the query
        start_time = time.time()
        response = await handle_query(QueryRequest(query=queryText))
        end_time = time.time()
        
        # Calculate & store metrics
        test_queries.at[index, strategy + '_response_time'] = end_time - start_time
        test_queries.at[index, strategy + '_cost'] = calculate_cost(queryText, response.response, response.metadata.source)
        
        if expected_cache_hit == "": # if we don't expect cache hit
          cache_hit_correctly: bool = response.metadata.source == "llm"
        else: # we expect cache hit
          cache_hit_correctly: bool = response.response == expected_cache_hit
          
        test_queries.at[index, strategy + '_cache_hit_correctly'] = cache_hit_correctly
        
        # Cleanup step: If the query got added to the cache (eg: by an llm call), remove it. 
        # This ensures each test is independent.
        redis_client.delete(queryText)
    
    return test_queries

async def main():
    print("Flushing db")
    redis_client.flushdb()
    print("DB has been cleared")

    past_queries = pd.read_csv("src/evaluations/past_queries.csv")

    print("Caching past queries...")
    for index, row in past_queries.iterrows():
        redis_client.set(row['QueryText'], row['ResponseText'])
        print(f"Cached query {index + 1}: {row['QueryText'][:50]}...")

    print("Finished caching all queries!")

    test_queries = pd.read_csv("src/evaluations/test_queries.csv")

    # Test different caching strategies
    for strategy in ["no_cache", "exact_match_only"]:
        test_queries = await evaluate_strategy(strategy, test_queries)
        
        # Calculate and print summary statistics for this strategy
        avg_response_time = test_queries[strategy + '_response_time'].mean()
        avg_cost = test_queries[strategy + '_cost'].mean()
        avg_accuracy = test_queries[strategy + '_cache_hit_correctly'].mean()
        
        print(f"\nStrategy: {strategy}")
        print(f"Average response time: {avg_response_time:.4f} seconds")
        print(f"Average cost per query: ${avg_cost:.6f}")
        print(f"Average cache hit accuracy: {avg_accuracy:.2%}")
        
        # Save results for this strategy
        test_queries.to_csv(f"src/evaluations/test_results.csv", index=False)

if __name__ == "__main__":
    asyncio.run(main())

