import pytest

from tokenrouter.classifier import classify, is_simple_math
from tokenrouter.types import Category


@pytest.mark.parametrize(
    ("prompt", "expected"),
    [
        ("What is the capital of Australia?", Category.FACTUAL),
        ("A shop has 240 items. How many remain after selling 60?", Category.MATH),
        ("Classify the sentiment of this review.", Category.SENTIMENT),
        ("Summarize this paragraph in one sentence.", Category.SUMMARIZATION),
        ("Extract all named entities and their types.", Category.NER),
        ("This function has a bug. Find and fix it.", Category.CODE_DEBUGGING),
        ("Each person owns a different pet. Who owns the cat?", Category.LOGIC),
        ("Write a Python function that returns the second largest number.", Category.CODE_GENERATION),
    ],
)
def test_all_categories(prompt: str, expected: Category) -> None:
    assert classify(prompt) is expected


def test_simple_math_gate() -> None:
    assert is_simple_math("How many remain if 240 items lose 60 items?")
    assert not is_simple_math("Project compound growth for 5 years, then compute interest.")

