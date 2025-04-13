"""
This script tests the performance of the API under load conditions. 

Run the script with:
    DISABLE_AUTO_CACHE=TRUE python3 -m tests.load_test.run_test

# Notes:
DISABLE_AUTO_CACHE must be set to "TRUE" to prevent affecting the actual cache

If redis has some results already cached and you want to empty the cache, run:
    docker ps | grep redis
and then
    docker exec <container_name> redis-cli FLUSHALL
For example:
    docker exec llm-response-caching-system-redis-1 redis-cli FLUSHALL
"""

import asyncio
import aiohttp
import time
import os
from typing import Dict

from .models import LoadTestResults
from .api_client import send_query
from .utils import load_queries_from_csv

async def run_load_test(num_requests: int = 100) -> LoadTestResults:
    """Run a load test with the specified number of concurrent requests."""
    # Read queries from CSV file
    queries = load_queries_from_csv('tests/load_test/queries.csv', num_requests)
    
    test_start_time = time.time()
    async with aiohttp.ClientSession() as session:
        tasks = [send_query(session, query) for query in queries]
        results = await asyncio.gather(*tasks)
    
    total_time = time.time() - test_start_time
    response_times = [r["response_time"] for r in results]
    cache_hits = sum(1 for r in results if r["source"] == "cache")
    timing_details = [r["timing"] for r in results]
    
    return LoadTestResults(
        total_requests=num_requests,
        total_time=total_time,
        response_times=response_times,
        cache_hits=cache_hits,
        query_details=results,
        test_start_time=test_start_time,
        timing_details=timing_details
    )

if __name__ == "__main__":
    if os.environ.get("DISABLE_AUTO_CACHE") != "TRUE":
        print("Warning: DISABLE_AUTO_CACHE is not set to TRUE. Please run the script with:")
        print("DISABLE_AUTO_CACHE=TRUE python3 tests/load_test.py")
        exit(1)
    
    results = asyncio.run(run_load_test())
    results.print_results()
    results.save_to_csv()