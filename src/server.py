import os
from dotenv import load_dotenv
import time

# Load environment variables once at application startup; need to do this before importing any other modules
load_dotenv()

from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict
from src.utils.query_llm import query_llm
from src.utils.query_cache import query_cache

# Configure FastAPI app
app = FastAPI(
    title="LLM Response Caching System",
    description="API for caching LLM responses",
    version="1.0.0"
)

class QueryRequest(BaseModel):
    query: str
    forceRefresh: Optional[bool] = False

class QueryMetadata(BaseModel):
    source: str # "cache" or "llm"
    timing: Dict[str, float] # Added timing information

class QueryResponse(BaseModel):
    response: str
    metadata: QueryMetadata

@app.get("/")
def health_check():
    return {"status": "The server is working."}

@app.post("/api/query", response_model=QueryResponse)
async def handle_query(request: QueryRequest) -> QueryResponse:
    timing = {}
    timing['start_time'] = time.time()
    
    try:
        # Try cache first
        if not request.forceRefresh:
            cache_start = time.time()
            cache_response: str | None = await query_cache(request.query)
            timing['cache_lookup'] = time.time() - cache_start
            
            if cache_response is not None:
                timing['total'] = time.time() - timing['start_time']
                return QueryResponse(
                    response=cache_response,
                    metadata=QueryMetadata(source="cache", timing=timing)
                )
        
        # Query LLM otherwise
        llm_start = time.time()
        llm_response = await query_llm(request.query)
        timing['llm_query'] = time.time() - llm_start
        
        timing['total'] = time.time() - timing['start_time']
        return QueryResponse(
            response=llm_response,
            metadata=QueryMetadata(source="llm", timing=timing)
        )
        
    except Exception as e:
        # Log the error for debugging
        print(f"Error in handle_query: {e}")
        timing['total'] = time.time() - timing['start_time']
        return QueryResponse(
            response="An error occurred while processing your request. Please try again later.",
            metadata=QueryMetadata(source="error", timing=timing)
        )
    
