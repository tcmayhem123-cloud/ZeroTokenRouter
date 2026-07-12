from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


SPEC = spec_from_file_location("local_evaluate", Path("scripts/evaluate.py"))
assert SPEC and SPEC.loader
MODULE = module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_keyword_and_numeric_scoring() -> None:
    ok, failures = MODULE.score_answer(
        "The result is 144 items.", {"all": ["result"], "number": 144}
    )
    assert ok
    assert failures == []


def test_missing_requirement_fails() -> None:
    ok, failures = MODULE.score_answer("Tokyo", {"all": ["Canberra"]})
    assert not ok
    assert failures

