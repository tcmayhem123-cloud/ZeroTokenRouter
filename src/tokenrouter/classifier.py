from __future__ import annotations

import re

from .types import Category


_PATTERNS: tuple[tuple[Category, re.Pattern[str]], ...] = (
    (
        Category.CODE_DEBUGGING,
        re.compile(
            r"\b(debug|bug|buggy|fix (?:this|the) (?:code|function)|"
            r"find and fix|corrected implementation|why does (?:this|the) code)\b",
            re.IGNORECASE,
        ),
    ),
    (
        Category.CODE_GENERATION,
        re.compile(
            r"\b(write|implement|create|generate)\b.{0,40}\b"
            r"(python|javascript|typescript|function|class|algorithm|code)\b|"
            r"\breturn (?:a|the) (?:function|implementation)\b",
            re.IGNORECASE | re.DOTALL,
        ),
    ),
    (
        Category.SENTIMENT,
        re.compile(
            r"\b(sentiment|positive,? negative|negative,? positive|"
            r"classify (?:the )?(?:review|tone|opinion))\b",
            re.IGNORECASE,
        ),
    ),
    (
        Category.SUMMARIZATION,
        re.compile(r"\b(summari[sz]e|summary|condense|one-sentence)\b", re.IGNORECASE),
    ),
    (
        Category.NER,
        re.compile(
            r"\b(named entit(?:y|ies)|\bner\b|extract (?:all )?(?:the )?entit(?:y|ies)|"
            r"label (?:the )?entit|person,? org(?:ani[sz]ation)?,? location)\b",
            re.IGNORECASE,
        ),
    ),
    (
        Category.LOGIC,
        re.compile(
            r"\b(logic puzzle|deduc|constraint|each (?:has|owns|uses)|"
            r"different pet|who (?:owns|sits|lives)|exactly one|truth[- ]teller)\b",
            re.IGNORECASE,
        ),
    ),
)

_MATH_PATTERN = re.compile(
    r"\b(calculate|compute|how many|how much|percentage|percent|"
    r"arithmetic|solve|equation|average|probability|remaining|total|projection)\b|[%×÷]",
    re.IGNORECASE,
)

_HARD_MATH_PATTERN = re.compile(
    r"\b(compound|interest|probability|projection|growth|rate|ratio|"
    r"system of equations|quadratic|derivative|integral|consecutive|then)\b",
    re.IGNORECASE,
)


def classify(prompt: str) -> Category:
    for category, pattern in _PATTERNS:
        if pattern.search(prompt):
            return category
    if _MATH_PATTERN.search(prompt):
        return Category.MATH
    return Category.FACTUAL


def is_simple_math(prompt: str) -> bool:
    if _HARD_MATH_PATTERN.search(prompt):
        return False
    numbers = re.findall(r"(?<![A-Za-z])[-+]?\d+(?:\.\d+)?", prompt)
    return 1 <= len(numbers) <= 4 and len(prompt) <= 420
