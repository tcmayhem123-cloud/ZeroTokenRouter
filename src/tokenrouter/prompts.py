from __future__ import annotations

from .types import Category


REMOTE_SYSTEM = "Answer accurately and concisely. Follow every requested format exactly."

_LOCAL_SYSTEMS: dict[Category, str] = {
    Category.FACTUAL: "Answer the factual question directly and accurately.",
    Category.MATH: "Solve carefully. Give the result and a concise verification.",
    Category.SENTIMENT: "Label the sentiment as Positive, Negative, Neutral, or Mixed. You MUST provide a one-sentence justification. If the review contains both positive and negative elements, classify as Mixed and justify by acknowledging both the negative experience (e.g. late delivery, damaged packaging) and the positive outcome (e.g. working product, responsive support). Format: '<Label> sentiment: <Justification>'",
    Category.SUMMARIZATION: "Summarize only the supplied text. Obey the length constraints exactly. If requested to summarize in exactly two sentences, you must output exactly two sentences. If requested to summarize in exactly three bullet points (each under 15 words), output exactly three bullet points, with each bullet point containing 15 words or fewer. Do not include conversational filler.",
    Category.NER: "Extract all named entities and label each as PERSON, ORGANIZATION, LOCATION, or DATE. Output the results in this format: 'EntityName (TYPE)'. Separate multiple entities with a comma. Do not include any other text.",
    Category.CODE_DEBUGGING: "Identify the bug and return a corrected implementation.",
    Category.LOGIC: "Satisfy every stated constraint and give the final conclusion.",
    Category.CODE_GENERATION: "Return correct, self-contained code matching the specification.",
}


def local_system(category: Category) -> str:
    return _LOCAL_SYSTEMS[category]

