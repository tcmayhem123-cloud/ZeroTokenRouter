from __future__ import annotations

from .types import Category


REMOTE_SYSTEM = "Answer accurately and concisely. Follow every requested format exactly."

_LOCAL_SYSTEMS: dict[Category, str] = {
    Category.FACTUAL: (
        "Answer the factual question directly and accurately."
    ),
    Category.MATH: (
        "Solve carefully. Give the result and a concise verification."
    ),
    Category.SENTIMENT: (
        "You are a precise sentiment classifier. Classify the review as Positive, Negative, Neutral, or Mixed. "
        "You MUST provide a one-sentence justification. If the review contains both positive and negative elements, "
        "classify as Mixed and justify by acknowledging both the negative experience (e.g. late delivery, damaged packaging) "
        "and the positive outcome (e.g. working product, responsive support). Format: '<Label> sentiment: <Justification>'\n\n"
        "Example 1:\n"
        "User: Classify the sentiment: 'The camera is excellent and I love the battery life.'\n"
        "Assistant: Positive sentiment: The customer has a positive experience, noting the excellent camera and loving the battery life.\n\n"
        "Example 2:\n"
        "User: Classify the sentiment: 'The battery is great, but the fragile screen is disappointing.'\n"
        "Assistant: Mixed sentiment: Although the battery performance is great, the screen is fragile and disappointing to the user."
    ),
    Category.SUMMARIZATION: (
        "You are a precise summarization assistant. Summarize only the supplied text. Obey the length constraints exactly. "
        "If requested to summarize in exactly two sentences, you must output exactly two sentences. If requested to "
        "summarize in exactly three bullet points (each under 15 words), output exactly three bullet points, with each "
        "bullet point containing 15 words or fewer. Do not include conversational filler.\n\n"
        "Example 1:\n"
        "User: Summarize in exactly two sentences: Quantum computing leverages superposition and entanglement to perform calculations exponentially faster than classical computers. However, physical qubits are susceptible to noise. Consequently, error correction is required.\n"
        "Assistant: Quantum computing utilizes superposition and entanglement to perform calculations much faster than classical systems. However, environmental noise and decoherence require massive error correction, making commercial scalability a distant goal.\n\n"
        "Example 2:\n"
        "User: Summarize in exactly three bullet points, each no longer than 15 words: Remote work has transformed how companies operate globally. Employees gain flexibility and reduced commute times, leading to reported improvements in work-life balance. However, challenges persist around collaboration, company culture, and the blurring of personal and professional boundaries.\n"
        "Assistant:\n"
        "- Remote work improves flexibility and work-life balance.\n"
        "- Collaboration, company culture, and boundaries present persistent challenges.\n"
        "- Companies invest in digital tools and rethink office space."
    ),
    Category.NER: (
        "You are a named entity extraction assistant. Extract all named entities from the text and label each as "
        "PERSON, ORGANIZATION, LOCATION, or DATE. Output the results in this format: 'EntityName (TYPE)'. "
        "Separate multiple entities with a comma. Do not include any other text.\n\n"
        "Example 1:\n"
        "User: Extract named entities: Ada Lovelace worked with Charles Babbage in London.\n"
        "Assistant: Ada Lovelace (PERSON), Charles Babbage (PERSON), London (LOCATION)\n\n"
        "Example 2:\n"
        "User: Extract named entities: Microsoft opened an office in Nairobi in January 2024.\n"
        "Assistant: Microsoft (ORGANIZATION), Nairobi (LOCATION), January 2024 (DATE)"
    ),
    Category.CODE_DEBUGGING: (
        "Identify the bug in the provided code and return the corrected python function. Ensure the code is clean, "
        "syntactically correct, and does not contain conversational filler.\n\n"
        "Example:\n"
        "User: Debug this Python function: def is_even(n): return n % 2 == 1\n"
        "Assistant:\n"
        "def is_even(n):\n"
        "    return n % 2 == 0"
    ),
    Category.LOGIC: (
        "Satisfy every stated constraint and give the final conclusion."
    ),
    Category.CODE_GENERATION: (
        "Return a correct, self-contained Python function matching the specification. Do not output any markdown "
        "code fences, comments, or conversational text.\n\n"
        "Example:\n"
        "User: Write a Python function named clamp that limits a number to an inclusive low and high bound.\n"
        "Assistant:\n"
        "def clamp(val, min_val, max_val):\n"
        "    return max(min_val, min(val, max_val))"
    ),
}


def local_system(category: Category) -> str:
    return _LOCAL_SYSTEMS[category]

