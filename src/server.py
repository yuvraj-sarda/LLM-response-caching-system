import os
from dotenv import load_dotenv

# Load environment variables once at application startup
load_dotenv()

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from query_llm import query_llm
from query_cache import query_cache

app = FastAPI()

class QueryRequest(BaseModel):
    query: str
    forceRefresh: Optional[bool] = False

class QueryMetadata(BaseModel):
    source: str # "cache" or "llm"

class QueryResponse(BaseModel):
    response: str
    metadata: QueryMetadata

@app.get("/health")
def health_check():
    return {"status": "The server is working."}

@app.post("/api/query", response_model=QueryResponse)
async def handle_query(request: QueryRequest):
    if (not request.forceRefresh):    
      cache_response: str = await query_cache(request.query)
      if (cache_response):
        return QueryResponse(
            response=cache_response,
            metadata=QueryMetadata(source="cache")
        )
    
    llm_response = await query_llm(request.query)
    return QueryResponse(
        response=llm_response,
        metadata=QueryMetadata(source="llm")
    )
    
