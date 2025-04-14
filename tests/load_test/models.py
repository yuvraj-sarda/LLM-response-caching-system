from dataclasses import dataclass
from typing import List, Dict
import statistics
import os
import json
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
        os.makedirs("logs", exist_ok=True)
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