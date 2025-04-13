import csv
from typing import List

def load_queries_from_csv(file_path: str, num_requests: int) -> List[str]:
    """Load queries from CSV file and repeat them to reach desired number of requests."""
    queries = []
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        queries = [row['query'] for row in reader]
    
    # Repeat queries to reach desired number of requests
    return [queries[i % len(queries)] for i in range(num_requests)] 