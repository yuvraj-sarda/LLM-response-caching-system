# An LLM Response Caching System
A high-performance semantic caching system designed to reduce LLM API costs while maintaining response quality. The system aims to intelligently identify and cache semantically similar queries.

## Setup and Running Instructions
Git clone
Start Docker desktop
Docker compose build
Docker compose up

Then, two api endpoints are exposed:
GET: \ --> servers as a health check
\api\query -> you can post here and receive the response, either cached or main.

## Architecture Overview and Design Decisions
For the main language, I decided to use Python – it's simple, well-established and has a lot of related ML packages.

For the server architecture, there are many popular technologies that could be used: Flask, FastAPI, and Django. I went with FastAPI because it seems like it is [better](https://www.netguru.com/blog/python-flask-versus-fastapi) for speed and performance (which is of high priority here). I've also worked with it before so it was quicker to setup for this project.

OpenAI recently updated to a new Responses API and they recommend using it for new projects. So, I'm using it instead of the traditional Chat Completions API.

For caching, I chose Redis as the primary caching solution because it provides incredibly fast access times, has built-in data structures for similarity search, and can handle our target throughput of 100 requests/second. It's also widely used, well documented, is docker friendly and has persistence options.

For the tests, I'm using pytest – based on quick research, it seems to be the industry standard.

## Evaluations

Load Testing Explanation
* Using proper async handling to ensure requests are processed properly via control loop
* considered using redis asynchronously too, but that could cause race conditions and atomicity issues. And it is only a few milliseconds of retrieval time, so not worth it. LLM calls are much more slow and responsible for the bulk of the the latency.

## Explanation of your semantic similarity approach 
At the moment, only exact match queries are being cached. I attempted to create and store vector embeddings too using HuggingFace's sentence transformers, but I was running into issues with Redis and Docker and I haven't had time yet to debug that.

## Tradeoffs and Optimizations
- Discussion of tradeoffs and potential optimizations

## Future Work
If I had more time to work on this, what would I have done?

My evaluation datasets are small; if I had more time, I'd prepare a more robust one.
Couldn't finish implementing the similarity based caching section; running into issues with docker and redis.

## Known issues with caching approach
While the caching system will likely save costs, it is necessarily going to reduce the quality of responses in some cases and cause unexpected behaviour.
* while we the query itself might be time insensitive, the LLM response might be time-sensitive (include numbers or dates that might get outdated). Time sensitivity of something also doesn't just depend on query but also when the query is asked (eg: who's the president of the USA is mostly time insensitive, but is so near the elections).
* While we might cache a query and get a valid answer back, the retrieved answer might not be perfectly suited (it would be slightly suboptimal; for examples of this, see the semantically similar test queries).
