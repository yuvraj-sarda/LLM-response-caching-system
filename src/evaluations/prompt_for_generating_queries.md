We are preparing a dataset that simulates cached user queries to a general LLM. 

Generate a CSV file of the following format:

Index, QueryText, ResponseText
1, [Sample query 1], [Sample response to query 1 from an LLM]
2, [Sample query 2], [Sample response to query 2 from an LLM]
and so on

Each QueryText is independent and comes from a separate source. There should be 100 queries in your output. 

Your collection should satisfy the following diversity criteria:
- Most QueryTexts should be around 100 tokens in length. 20 QueryTexts should be significantly shorter (around 30 tokens) and around 20 QueryTexts should be significantly longer (around 300 tokens).
- Most QueryTexts should be in English, but include some in other languages, and some that have special characters (like emojis).
- The QueryTexts should span across many different topic areas and domains.
- The QueryTexts should vary in time sensitivity. You should have QueryTexts whose responses will be accurate for years (key scientific facts), and QueryTexts whose responses would become wrong in just a few minutes or hours (eg: weather) or days or weeks or months. 
- 70 QueryTexts should be such that they warrant simple ResponseTexts; 30 QueryTexts should be more complex.
- ResponseTexts should all be short and concise; around 100 tokens long.


