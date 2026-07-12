from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Category(StrEnum):
    FACTUAL = "factual"
    MATH = "math"
    SENTIMENT = "sentiment"
    SUMMARIZATION = "summarization"
    NER = "ner"
    CODE_DEBUGGING = "code_debugging"
    LOGIC = "logic"
    CODE_GENERATION = "code_generation"


class Backend(StrEnum):
    LOCAL = "local"
    FIREWORKS = "fireworks"


class RoutingProfile(StrEnum):
    SAFE = "safe"
    HYBRID = "hybrid"
    LOCAL = "local"


@dataclass(frozen=True, slots=True)
class Task:
    task_id: str
    prompt: str

    @classmethod
    def from_dict(cls, raw: object) -> "Task":
        if not isinstance(raw, dict):
            raise ValueError("Each task must be a JSON object")
        task_id = raw.get("task_id")
        prompt = raw.get("prompt")
        if not isinstance(task_id, str) or not task_id.strip():
            raise ValueError("Each task requires a non-empty string task_id")
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError(f"Task {task_id!r} requires a non-empty string prompt")
        return cls(task_id=task_id, prompt=prompt)


@dataclass(frozen=True, slots=True)
class RouteDecision:
    category: Category
    backend: Backend
    model: str | None
    max_tokens: int
    reasoning_effort: str | None = None


@dataclass(frozen=True, slots=True)
class Result:
    task_id: str
    answer: str

    def as_dict(self) -> dict[str, str]:
        return {"task_id": self.task_id, "answer": self.answer}

