from __future__ import annotations

from .types import Category


REMOTE_SYSTEM = "Answer accurately and concisely. Follow every requested format exactly."

_LOCAL_SYSTEMS: dict[Category, str] = {
    Category.FACTUAL: "Answer the factual question directly and accurately.",
    Category.MATH: "Solve carefully. Give the result and a concise verification.",
    Category.SENTIMENT: "Label the sentiment and briefly justify it.",
    Category.SUMMARIZATION: "Summarize only the supplied text and obey length constraints.",
    Category.NER: "Extract entities and label each with its requested type.",
    Category.CODE_DEBUGGING: "Identify the bug and return a corrected implementation.",
    Category.LOGIC: "Satisfy every stated constraint and give the final conclusion.",
    Category.CODE_GENERATION: "Return correct, self-contained code matching the specification.",
}


def local_system(category: Category) -> str:
    return _LOCAL_SYSTEMS[category]

