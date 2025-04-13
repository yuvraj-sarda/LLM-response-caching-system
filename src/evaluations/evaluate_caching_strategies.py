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
import tracemalloc

tracemalloc.start()

async def main():
    await initialise_cache()

    # Read test queries with proper handling of empty strings
    test_df = pd.read_csv(
        "src/evaluations/test_queries.csv",
        keep_default_na=True,
        na_values=['']
    )

    # Test different caching strategies
    strategies = ["exact_match_only", "no_cache"]
    for strategy in strategies:
        await evaluate_strategy(strategy, test_df)
              
    # Save results with proper handling of empty values
    test_df.to_csv(
        "src/evaluations/test_results.csv",
        index=False,
        na_rep=''
    )
        
    await save_aggregated_results(test_df, strategies)

async def initialise_cache():
    redis_client.flushdb()
    print("Flushed the db")
    
    past_queries = pd.read_csv("src/evaluations/past_queries.csv")
    for index, row in past_queries.iterrows():
        redis_client.set(row['QueryText'], row['ResponseText'])

    print("Cached all queries.")

async def evaluate_strategy(strategy: str, test_queries: pd.DataFrame) -> pd.DataFrame:
    print(f"\n## Testing strategy: {strategy}")
    os.environ["CACHING_STRATEGY"] = strategy
    test_queries[strategy + '_response_time'] = 0.0
    test_queries[strategy + '_cost'] = 0.0
    test_queries[strategy + '_cache_hit_correctly'] = False

    # TODO: right now, everything is being done synchronously, which makes running this very slow (50 tests with ~3 seconds per test = 150 seconds)
    # We should do this parallely, but there is an issue with cache setting in one test possibly interfering with other tests.
    for index, row in test_queries.iterrows():
        print(f"Handling test query {index}")
        queryText = row["QueryText"]
        expected_cache_hit = row["ExpectedCacheHit"]
        
        # Time the query
        start_time = time.time()
        response = await handle_query(QueryRequest(query=queryText))
        end_time = time.time()
        
        # Cleanup step: If the query got added to the cache (eg: by an llm call), remove it. 
        # This ensures each test is independent.
        redis_client.delete(queryText)
        
        # Calculate & store metrics
        test_queries.at[index, strategy + '_response_time'] = end_time - start_time
        test_queries.at[index, strategy + '_cost'] = calculate_cost(queryText, response.response, response.metadata.source)
        
        # TODO: i'm not sure if this code is working as expected; might be buggy.
        if expected_cache_hit == "": # if we don't expect cache hit
          cache_hit_correctly: bool = (response.metadata.source == 'llm')
        else: # we expect cache hit
          cache_hit_correctly: bool = (response.response == expected_cache_hit)
          
        test_queries.at[index, strategy + '_cache_hit_correctly'] = cache_hit_correctly
    
    return test_queries

async def save_aggregated_results(test_results: pd.DataFrame, strategies: list[str]) -> bool:
    markdown_content = ""
    for strategy in strategies:
        # Calculate summary statistics for this strategy
        avg_response_time = test_results[strategy + '_response_time'].mean()
        avg_cost = test_results[strategy + '_cost'].mean()
        avg_accuracy = test_results[strategy + '_cache_hit_correctly'].mean()
        
        # Create markdown content
        markdown_content += f"""
## Strategy: {strategy}
- Average response time: {avg_response_time:.4f} seconds
- Average cost per query: ${avg_cost:.6f}
- Average cache hit accuracy: {avg_accuracy:.2%}

""" 
    # Write to file
    with open("src/evaluations/test_results_aggregated.md", "w") as f:
        f.write(markdown_content)

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
        output_tokens = len(responseText) / 4
        return (input_tokens * 0.03 + output_tokens * 0.06) / 1000
      case _:
        print(f"Warning: unsupported response source: {source}")
        return 0.0

if __name__ == "__main__":
    asyncio.run(main())