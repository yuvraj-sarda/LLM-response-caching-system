"""
I planned to write some unit tests for the code using pytest; however, I found that just simple end-to-end testing + evaluations and external test scripts were enough to test the functionalities for now. 

If this project is to be made production ready though, I would implement some tests (in this folder).
"""

def func(x):
    return x + 1


def test_answer():
    assert func(3) == 5