import os
from dotenv import load_dotenv
import time

# Load environment variables once at application startup
load_dotenv()

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, Dict
from query_llm import query_llm
from query_cache import query_cache

app = FastAPI()

class QueryRequest(BaseModel):
    query: str
    forceRefresh: Optional[bool] = False

class QueryMetadata(BaseModel):
    source: str # "cache" or "llm"
    timing: Dict[str, float] # Added timing information

class QueryResponse(BaseModel):
    response: str
    metadata: QueryMetadata

@app.get("/health")
def health_check():
    return {"status": "The server is working."}

@app.post("/api/query", response_model=QueryResponse)
async def handle_query(request: QueryRequest) -> QueryResponse:
    timing = {}
    timing['start_time'] = time.time()
    
    if (not request.forceRefresh):    
        cache_start = time.time()
        cache_response: str | None = await query_cache(request.query)
        timing['cache_lookup'] = time.time() - cache_start
        
        if (cache_response != None):
            timing['total'] = time.time() - timing['start_time']
            return QueryResponse(
                response=cache_response,
                metadata=QueryMetadata(source="cache", timing=timing)
            )
    
    llm_start = time.time()
    llm_response = await query_llm(request.query)
    timing['llm_query'] = time.time() - llm_start
    
    timing['total'] = time.time() - timing['start_time']
    return QueryResponse(
        response=llm_response,
        metadata=QueryMetadata(source="llm", timing=timing)
    )
    
