# An LLM Response Caching System
This is a high-performance semantic caching system designed to reduce LLM API costs while maintaining response quality. It aims to intelligently identify and cache semantically similar queries.

## Setup and Running Instructions
1. Clone the repository:
```bash
git clone git@github.com:yuvraj-sarda/LLM-response-caching-system.git
cd LLM-response-caching-system
```

2. Create a `.env` file in the root folder using the template from `.env.example`

3. Launch the Docker Desktop app

4. Start the system:
```bash
docker compose build
docker compose up
```

The server will be now available at http://localhost:3000/

## API Endpoints

- **GET /** 
  - Returns: `{"status": "The server is working."}`
  - Purpose: Verify server is running

- **POST /api/query**
  - Request Body:
    ```json
    {
      "query": "string",
      "forceRefresh": false // boolean (optional)
    }
    ```
  - Response:
    ```json
    {
      "response": "string",
      "metadata": {
        "source": "cache" | "llm" | "error",
        "timing": {} // a dictionary containing info about how much time different stages of the request took
      }
    }
    ```
  - The `forceRefresh` parameter can be used to bypass the cache and get a fresh response from the LLM

## Tech Stack

- **Python**: I chose to implement this in python because of its simplicity and its extensive ML ecoystem. 
- **FastAPI**: A web framework for building APIs. I chose it over alternatives like Flask and Django because it is known for its speed and performance (which are key considerations here).
- **Redis**: Caching solution providing:
  - Sub-millisecond response times
  - Built-in data structures for similarity search
  - Persistence options
  - Docker-friendly deployment
- **OpenAI API**: OpenAI has an industry standard package that one can easily adjust to use other providers too. I'm using the latest Responses API (instead of the Chat Completions API) as recommended by OpenAI.
- **HuggingFace Sentence Transformers**: For computing semantic similarity between queries.

## Architecture Overview

The system follows a simple but effective control flow. When a query arrives at the FastAPI server, 
1. It checks if caching is enabled and if the user hasn't requested a force refresh. 
2. If so, the query is then passed to `query_cache()` which implements the appropriate caching strategy depending on the configs in the .env file. 
3. If a cache hit occurs, the response is returned immediately. 
4. Otherwise, the query is forwarded to the LLM service. The LLM response is cached for future use and returned to the user.

## Associated Scripts
Alongside the main caching system, I've also written two key scripts to properly evaluate and validate the caching system. These scripts are essential in order to:
1. Quantify whether the caching system actually reduces costs and improves performance
2. Compare different caching strategies to find the optimal approach
3. Ensure the system can handle real-world usage patterns

`src/evaluations/evaluate_caching_strategies.py`:
This script evaluates the effectiveness of different caching strategies by measuring their impact on response time, cost, and accuracy. I wrote an LLM prompt to generate a diverse database of past queries and another one for test queries. The script first caches the past queries and concurrently feeds each test query into the system to see how it performs. The detailed results are then stored in files.

`tests/load_test/run_test.py`:
This script tests the system's performance under load conditions by sending concurrent requests to the API. The API was easily able to process 100 concurrent requests (I haven't tried with a higher concurrency rate), with the main time consuming activity being awaiting the responses from OpenAI.

While the API route currently handles the request to OpenAI asynchronously correctly, it blocks when reading/writing to the Redis cache. I considered whether this should also be done asynchronously in order to maximise speed. However, this would break atomicity of operations and thus create potential race conditions. Moreover, given that Redis calls are really fast (sub-milliseconds), this didn't really contribute much to the response times. So, I didn't make the optimisation. 

## Future Work
- At the moment, the system only correctly retrieves items from the cache when there is an exact query match. This isn't ideal. I implemented a vector embedding based approach using HuggingFace's sentence transformers and Redis vector search. However, I was running into some integration issues with Redis and Docker and I didn't have time to debug that. So for now, I've just commented these sections of the code out. When I have some more time, I'll go through the documentation more thoroughly and debug this.

- Implement a few other caching approaches. I'm particularly interested in seeing if a combination of vector embeddings (to get top 5 most similar cached queries) and a small local LLM (to accurately distinguish if the cache should be hit or not) will be a performant and accurate solution. This hybrid approach could potentially provide better accuracy than pure vector similarity while maintaining good performance.

- Once all the desired caching approaches have been defined, the evaluation scripts should be tweaked and run. This will help clearly identify the tradeoffs between the different approaches (especially the speed, cost and accuracy) and test various similarity thresholds.

- Create a more diverse and robust evaluation dataset. The current test queries are generated using an LLM prompt (`src/evaluations/test_queries_generation_prompt.md`) and can thus be easily scaled. However, due to limited time, I was only able to prepare a small dataset. A larger dataset with more diverse query types and edge cases would provide better insights into the system's performance.

- Implement `calculate_TTL` function inside the `cache_response.py` file. This would ensure that time-sensitive functions are cached only for the duration for which they are likely to be valid. It's best to first create a test dataset and script for this; then try various approaches in a similar switch case fashion as I did for the caching system, ultimately going with the approach that performs the best on the test dataset.

## Additional Considerations
I observed an issue while preparing the evaluation datasets: no matter how perfect the caching system is, it will still be erraneous sometimes. There are a few reasons for this:

1. While two queries may be semantically similar and the same response would technically work for both queries, it would lead to suboptimal responses. For example, "What are the 3 most populous countries?" and "List the top 3 countries by population size" are semantically similar; but an LLM response like "India, China, USA" would be perfect for the former, but suboptimal for the second query, where a user likely expects some actual numbers too.

2. Some queries can be time insensitive in general, but may be time sensitive during specific periods. For example, it's pretty time-insensitive to consider "Who's the president of the USA" in general, but not so closer to an election, or during an impeachment process. 

3. Some times, the query may be time insensitive, but the response may nevertheless include some time sensitive facts/figures and thus get invalidated. Eg: the most populous country question is fairly time insensitive, but if the LLM response contains population figures, it might become outdated.

I don't know how these concerns should be dealt with yet, but they're worth thinking about.