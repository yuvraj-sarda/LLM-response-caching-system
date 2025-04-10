from openai import OpenAI
client = OpenAI()
from .cache_response import cache_response
  
async def query_llm(query: str) -> str:
  try:
    response = client.responses.create(
      model="gpt-4o",
      instructions="You are a helpful assistant.",
      input=query,
    )

    print(response)
    cache_response(query, response.output_text)
    return response.output_text
  except Exception as e:
    print(f"Error in query_llm: {e}")
    return "Unfortunately, LLM querying is not available right now due to an internal error. Please try again later." # handle error gracefully