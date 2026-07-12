from __future__ import annotations

from .classifier import classify, is_simple_math
from .config import ModelCatalog
from .types import Backend, Category, RouteDecision, RoutingProfile, Task


_MAX_TOKENS: dict[Category, int] = {
    Category.FACTUAL: 180,
    Category.MATH: 220,
    Category.SENTIMENT: 120,
    Category.SUMMARIZATION: 180,
    Category.NER: 180,
    Category.CODE_DEBUGGING: 420,
    Category.LOGIC: 260,
    Category.CODE_GENERATION: 420,
}

_LOCAL_HYBRID = {
    Category.SENTIMENT,
    Category.SUMMARIZATION,
    Category.NER,
}

_CODE = {Category.CODE_DEBUGGING, Category.CODE_GENERATION}
_MAX_LOCAL_PROMPT_CHARS = 12_000


def decide(task: Task, profile: RoutingProfile, catalog: ModelCatalog) -> RouteDecision:
    category = classify(task.prompt)
    max_tokens = _MAX_TOKENS[category]

    if profile is RoutingProfile.LOCAL:
        return RouteDecision(category, Backend.LOCAL, None, max_tokens)

    if profile is RoutingProfile.HYBRID:
        local_candidate = category in _LOCAL_HYBRID or (
            category is Category.MATH and is_simple_math(task.prompt)
        )
        if local_candidate and len(task.prompt) <= _MAX_LOCAL_PROMPT_CHARS:
            return RouteDecision(category, Backend.LOCAL, None, max_tokens)

    model = catalog.code() if category in _CODE else catalog.general()
    if model is None:
        return RouteDecision(category, Backend.LOCAL, None, max_tokens)

    reasoning_effort = "low" if category in {Category.MATH, Category.LOGIC} else "none"
    return RouteDecision(
        category=category,
        backend=Backend.FIREWORKS,
        model=model,
        max_tokens=max_tokens,
        reasoning_effort=reasoning_effort,
    )
