from pathlib import Path

import pytest

from tokenrouter.config import ModelCatalog
from tokenrouter.routing import decide
from tokenrouter.types import Backend, Category, RoutingProfile, Task


CATALOG = ModelCatalog(("minimax-m3", "kimi-k2p7-code"))


@pytest.mark.parametrize(
    ("profile", "prompt", "backend", "model"),
    [
        (RoutingProfile.SAFE, "Classify sentiment: great.", Backend.FIREWORKS, "minimax-m3"),
        (RoutingProfile.HYBRID, "Classify sentiment: great.", Backend.LOCAL, None),
        (RoutingProfile.HYBRID, "What is photosynthesis?", Backend.FIREWORKS, "minimax-m3"),
        (RoutingProfile.HYBRID, "Write a Python function for sorting.", Backend.FIREWORKS, "kimi-k2p7-code"),
        (RoutingProfile.LOCAL, "What is photosynthesis?", Backend.LOCAL, None),
    ],
)
def test_profiles(profile: RoutingProfile, prompt: str, backend: Backend, model: str | None) -> None:
    decision = decide(Task("t", prompt), profile, CATALOG)
    assert decision.backend is backend
    assert decision.model == model


def test_hard_math_uses_remote() -> None:
    decision = decide(
        Task("t", "Calculate compound interest over 5 years, then project growth."),
        RoutingProfile.HYBRID,
        CATALOG,
    )
    assert decision.category is Category.MATH
    assert decision.backend is Backend.FIREWORKS
    assert decision.reasoning_effort == "low"


def test_missing_compatible_remote_model_falls_back_local() -> None:
    decision = decide(
        Task("t", "What is photosynthesis?"),
        RoutingProfile.SAFE,
        ModelCatalog(("gemma-4-31b-it",)),
    )
    assert decision.backend is Backend.LOCAL
    assert decision.model is None


def test_long_summary_escalates_in_hybrid() -> None:
    decision = decide(
        Task("t", "Summarize this text: " + ("word " * 3000)),
        RoutingProfile.HYBRID,
        CATALOG,
    )
    assert decision.category is Category.SUMMARIZATION
    assert decision.backend is Backend.FIREWORKS
