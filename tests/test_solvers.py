import pytest

from tokenrouter.solvers import solve_simple_math


@pytest.mark.parametrize(
    ("prompt", "expected"),
    [
        ("Calculate 18 percent of 250.", "45"),
        ("What is 12 × 7?", "84"),
        ("Compute 15 / 4.", "3.75"),
        (
            "A store has 240 items. It sells 15% on Monday and 60 more on Tuesday. "
            "How many items remain?",
            "144 remain",
        ),
    ],
)
def test_high_confidence_math(prompt: str, expected: str) -> None:
    answer = solve_simple_math(prompt)
    assert answer is not None
    assert expected in answer


def test_ambiguous_word_problem_is_not_forced() -> None:
    assert solve_simple_math("A complicated rate problem has several unknowns.") is None
