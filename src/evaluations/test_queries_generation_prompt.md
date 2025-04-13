This is the prompt I used to generate the test_queries. If you copy paste it into Cursor Chat, it'll generate a new similar set of similar queries for you. You can then go back to the past_queries dataset and fill in the ExpectedCacheHit yourself (not asking LLM to do that because it might make typos / minor hallucinations that will cause tests to fail).

Note: If you regenerated the past_queries, ensure that you also replace the sample queries provided with some queries from the new past_queries dataset.

TODO: sometimes the LLM mislabels the TestCategory - necessary for a human to look closely at each query and confirm.
=======

We are preparing a test dataset to evaluate the effectiveness of our caching system. 

## Task
Create a CSV file named `test_queries.csv` which has the following format:

Index, QueryText, SourceQueryIndex, TestCategory
1, [Test query 1], [The query which was used as a starting point to generate query 1], [Purpose of asking query 1]
2, [Test query 2], [The query which was used as a starting point to generate query 1], [Purpose of asking query 2]
and so on.

## Steps to creating the dataset
Here are 6 user queries. You will use them as starting points to generate your test queries.

QueryIndex, QueryText
3,"¿Cómo se dice 'hello' en español?"
5,"What are the top 3 most populous countries in the world?"
6,"🌟 What's the meaning of life? 🌟"
9,"Explain quantum computing to a 5-year-old"
24,"How do I make homemade pizza dough?"
47,"What's the latest Tesla model?"

For each user query Q above, you should generate queries in each of the following categories:
* ExactDuplicate: 1 query that is an exactly duplicate of Q.
* CleanedDuplicate: 1 query that is a duplicate of Q but in lowercase and without any special characters.
* SemanticallySimilar: 3 queries that are rewordings of Q, but that fully preserve the meaning, such that the response to Q would also be a valid response to your generated queries.
* SimilarlyWorded: 3 queries that are similarly worded to Q, but which change the meaning, such that a response to Q would not be a valid response to your generated queries.
* Unrelated: 2 queries that are completely unrelated to any of the initially provided queries.

Generate them by creating text yourself, not by writing a script!