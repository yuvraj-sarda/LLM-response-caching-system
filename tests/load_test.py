"""
This file is used to test the performance of the API under load.

To run it:
python3 tests/load_test.py


Note: if redis has some cached results that you want to remove, you can do so by running:
docker ps | grep redis
and then
docker exec <container_name> redis-cli FLUSHALL

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

    def print_results(self) -> None:
        print(f"\nLoad Test Results:")
        print(f"Total requests: {self.total_requests}")
        print(f"Total time: {self.total_time:.2f} seconds")
        print(f"Requests per second: {self.requests_per_second:.2f}")
        print(f"Average response time: {self.average_response_time:.2f} seconds")
        print(f"Median response time: {self.median_response_time:.2f} seconds")
        print(f"95th percentile response time: {self.percentile_95_response_time:.2f} seconds")
        print(f"Cache hit rate: {self.cache_hit_rate:.1f}%")

    def save_to_csv(self) -> None:
        csv_file = os.path.join("logs", f"load_test.csv")
        
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            # Write header
            writer.writerow(['queryText', 'startTime', 'endTime', 'responseTime', 'source'])
            
            # Write each query's details
            for query_detail in self.query_details:
                writer.writerow([
                    query_detail['query'],
                    query_detail['start_time'] - self.test_start_time,
                    query_detail['end_time'] - self.test_start_time,
                    query_detail['response_time'],
                    query_detail['source']
                ])
        
        print(f"\nDetailed query-wise results saved to: {csv_file}")

async def send_query(session: aiohttp.ClientSession, query: str, test_start_time: float) -> Dict:
    """Send a single query to the API and return the response time and metadata."""
    print(f"Sending query: {query[:10]}...")
    start_time = time.time()
    async with session.post(
        "http://localhost:3000/api/query",
        json={"query": query, "forceRefresh": False}
    ) as response:
        response_data = await response.json()
        end_time = time.time()
        response_time = end_time - start_time
        return {
            "query": query,
            "start_time": start_time,
            "end_time": end_time,
            "response_time": response_time,
            "source": response_data["metadata"]["source"]
        }

async def run_load_test(num_requests: int = 100) -> LoadTestResults:
    """Run a load test with the specified number of concurrent requests."""
    # Sample queries to use for testing
    test_queries = [
        "What is the capital of France?",
        "Explain quantum computing in simple terms",
        "What are the benefits of exercise?",
        "How does photosynthesis work?",
        "What is the meaning of life?",
        "Tell me about the history of the internet",
        "What are the main causes of climate change?",
        "How do I make a good cup of coffee?",
        "What is machine learning?",
        "Explain the theory of relativity"
    ]
    
    # Repeat queries to reach desired number of requests
    queries = [test_queries[i % len(test_queries)] for i in range(num_requests)]
    
    test_start_time = time.time()
    async with aiohttp.ClientSession() as session:
        tasks = [send_query(session, query, test_start_time) for query in queries]
        results = await asyncio.gather(*tasks)
    
    total_time = time.time() - test_start_time
    response_times = [r["response_time"] for r in results]
    cache_hits = sum(1 for r in results if r["source"] == "cache")
    
    return LoadTestResults(
        total_requests=num_requests,
        total_time=total_time,
        response_times=response_times,
        cache_hits=cache_hits,
        query_details=results,
        test_start_time=test_start_time
    )

if __name__ == "__main__":
    os.environ["DISABLE_AUTO_CACHE"] = "TRUE"
    results = asyncio.run(run_load_test())
    results.print_results()
    results.save_to_csv() 