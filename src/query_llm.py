import os
import logging
from datetime import datetime
from openai import AsyncOpenAI
from src.cache_response import cache_response

client = AsyncOpenAI()

os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    filename='logs/llm_queries.txt',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# TODO: probably need to add an intermediate data structure here to handle rate limits
async def query_llm(query: str) -> str:
  try:
    response = await client.responses.create(
        model="gpt-4o",
        instructions="You are a helpful assistant.",
        input=query,
    )    

    logging.info(f"Query: {query}")
    logging.info(f"Response: {response}")
    logging.info("="*50)  # Separator between entries
    
    cache_response(query, response.output_text)
    
    return response.output_text
  except Exception as e:
    print(f"Error in query_llm: {e}")
    return "Unfortunately, LLM querying is not available right now due to an internal error. Please try again later." # handle error gracefully