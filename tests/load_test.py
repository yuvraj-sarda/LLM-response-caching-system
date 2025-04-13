"""
This file is used to test the performance of the API under load.

To run it:
DISABLE_AUTO_CACHE=TRUE python3 tests/load_test.py

Note: The DISABLE_AUTO_CACHE environment variable must be set to "TRUE" before running the script.

If redis has some results already cached and you want to empty the cache, run:
docker ps | grep redis
and then
docker exec <container_name> redis-cli FLUSHALL

Example:
docker exec llm-response-caching-system-redis-1 redis-cli FLUSHALL
"""

import asyncio
import aiohttp
import time
import json
from typing import List, Dict
import statistics
from dataclasses import dataclass
import os
from datetime import datetime
import csv

@dataclass
class LoadTestResults:
    total_requests: int
    total_time: float
    response_times: List[float]
    cache_hits: int
    query_details: List[Dict]
    test_start_time: float
    timing_details: List[Dict]

    @property
    def requests_per_second(self) -> float:
        return self.total_requests / self.total_time

    @property
    def average_response_time(self) -> float:
        return statistics.mean(self.response_times)

    @property
    def median_response_time(self) -> float:
        return statistics.median(self.response_times)

    @property
    def percentile_95_response_time(self) -> float:
        return statistics.quantiles(self.response_times, n=20)[18]

    @property
    def cache_hit_rate(self) -> float:
        return (self.cache_hits / self.total_requests) * 100

    @property
    def max_llm_query_time(self) -> float:
        llm_times = [t['llm_query'] for t in self.timing_details if 'llm_query' in t]
        return max(llm_times) if llm_times else 0.0

    def print_results(self) -> None:
        print(f"\nLoad Test Results:")
        print(f"Total requests: {self.total_requests}")
        print(f"Total time: {self.total_time:.2f} seconds")
        print(f"Requests per second: {self.requests_per_second:.2f}")
        print(f"Average response time: {self.average_response_time:.2f} seconds")
        print(f"Median response time: {self.median_response_time:.2f} seconds")
        print(f"95th percentile response time: {self.percentile_95_response_time:.2f} seconds")
        print(f"Cache hit rate: {self.cache_hit_rate:.1f}%")
        
        # Print timing analysis
        if self.timing_details:
            print("\nTiming Analysis:")
            cache_times = [t['cache_lookup'] for t in self.timing_details if 'cache_lookup' in t]
            llm_times = [t['llm_query'] for t in self.timing_details if 'llm_query' in t]
            
            if cache_times:
                print(f"Average cache lookup time: {statistics.mean(cache_times):.2f} seconds")
                print(f"Median cache lookup time: {statistics.median(cache_times):.2f} seconds")
            
            if llm_times:
                print(f"Average LLM query time: {statistics.mean(llm_times):.2f} seconds")
                print(f"Median LLM query time: {statistics.median(llm_times):.2f} seconds")
                print(f"Maximum LLM query time: {self.max_llm_query_time:.2f} seconds")

    def save_to_csv(self) -> None:
        csv_file = os.path.join("logs", f"load_test.csv")
        
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            # Write header
            writer.writerow(['queryText', 'startTime', 'endTime', 'responseTime', 'source', 'timing'])
            
            # Write each query's details
            for query_detail in self.query_details:
                writer.writerow([
                    query_detail['query'],
                    query_detail['start_time'] - self.test_start_time,
                    query_detail['end_time'] - self.test_start_time,
                    query_detail['response_time'],
                    query_detail['source'],
                    json.dumps(query_detail.get('timing', {}))
                ])
        
        print(f"\nDetailed query-wise results saved to: {csv_file}")

async def send_query(session: aiohttp.ClientSession, query: str, test_start_time: float) -> Dict:
    """Send a single query to the API and return the response time and metadata."""
    start_time = time.time()
    try:
        async with session.post(
            "http://localhost:3000/api/query",
            json={"query": query, "forceRefresh": False}
        ) as response:
            response_data = await response.json()
            end_time = time.time()
            response_time = end_time - start_time
            
            # Safely extract timing information
            timing = response_data.get("metadata", {}).get("timing", {})
            
            return {
                "query": query,
                "start_time": start_time,
                "end_time": end_time,
                "response_time": response_time,
                "source": response_data.get("metadata", {}).get("source", "unknown"),
                "timing": timing
            }
    except Exception as e:
        print(f"Error processing query '{query[:10]}...': {str(e)}")
        return {
            "query": query,
            "start_time": start_time,
            "end_time": time.time(),
            "response_time": time.time() - start_time,
            "source": "error",
            "timing": {}
        }

async def run_load_test(num_requests: int = 100) -> LoadTestResults:
    """Run a load test with the specified number of concurrent requests."""
    # Read queries from CSV file
    queries = []
    with open('tests/load_test_queries.csv', 'r') as f:
        reader = csv.DictReader(f)
        queries = [row['query'] for row in reader]
    
    # Repeat queries to reach desired number of requests
    queries = [queries[i % len(queries)] for i in range(num_requests)]
    
    test_start_time = time.time()
    async with aiohttp.ClientSession() as session:
        tasks = [send_query(session, query, test_start_time) for query in queries]
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