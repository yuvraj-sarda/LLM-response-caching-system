import aiohttp
import time
from typing import Dict

async def send_query(session: aiohttp.ClientSession, query: str) -> Dict:
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