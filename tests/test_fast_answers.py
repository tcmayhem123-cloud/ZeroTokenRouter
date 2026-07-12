from tokenrouter.fast_answers import answer
from tokenrouter.types import Category


def test_fast_local_paths_cover_practice_shapes() -> None:
    assert answer(Category.MATH, "Calculate 18 percent of 250.") == "45"
    summary = answer(
        Category.SUMMARIZATION,
        "Summarize in exactly one sentence: Encryption converts readable data into a protected form. A key is required to recover the original information.",
    )
    assert summary and "Encryption" in summary and "key" in summary
    entities = answer(
        Category.NER,
        "Extract named entities and label their types: Microsoft opened an office in Nairobi in January 2024.",
    )
    assert entities and "Microsoft" in entities and "Nairobi" in entities
    logic = answer(
        Category.LOGIC,
        "Three friends, Sam, Jo, and Lee, each own a different pet: cat, dog, bird. Sam does not own the bird. Jo owns the dog. Who owns the cat?",
    )
    assert logic and "Sam owns cat" in logic
