from openai import OpenAI
client = OpenAI()
from redis_client import redis_client
  
async def query_llm(query: str) -> str:
  try:
    response = client.responses.create(
      model="gpt-4o",
      instructions="You are a helpful assistant.",
      input=query,
    )

    print(response)
    
    redis_client.set(query, response.output_text)
    return response.output_text
  except Exception as e:
    print(e)
    return "Unfortunately, LLM querying is not available right now due to an internal error. Please try again later." # handle error gracefully