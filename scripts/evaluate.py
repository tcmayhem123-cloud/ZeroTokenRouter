from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


def normalized(text: str) -> str:
    return " ".join(text.lower().split())


def score_answer(answer: str, expected: dict[str, Any]) -> tuple[bool, list[str]]:
    text = normalized(answer)
    failures: list[str] = []

    for keyword in expected.get("all", []):
        if normalized(str(keyword)) not in text:
            failures.append(f"missing {keyword!r}")

    any_keywords = [normalized(str(item)) for item in expected.get("any", [])]
    if any_keywords and not any(keyword in text for keyword in any_keywords):
        failures.append(f"none of {any_keywords!r}")

    if "number" in expected:
        target = float(expected["number"])
        numbers = [float(value) for value in re.findall(r"-?\d+(?:\.\d+)?", text)]
        if not any(abs(number - target) <= 1e-6 for number in numbers):
            failures.append(f"missing numeric answer {target:g}")

    max_sentences = expected.get("max_sentences")
    if max_sentences is not None:
        sentences = [part for part in re.split(r"(?<=[.!?])\s+", answer.strip()) if part]
        if len(sentences) > int(max_sentences):
            failures.append(f"more than {max_sentences} sentence(s)")

    return not failures, failures


def main() -> int:
    parser = argparse.ArgumentParser(description="Score a results.json against local checks")
    parser.add_argument("--tasks", type=Path, default=Path("data/simulated_eval.json"))
    parser.add_argument("--results", type=Path, default=Path("output/results.json"))
    parser.add_argument("--required", type=int, default=17)
    args = parser.parse_args()

    tasks = json.loads(args.tasks.read_text(encoding="utf-8"))
    results = json.loads(args.results.read_text(encoding="utf-8"))
    answers = {
        item.get("task_id"): item.get("answer", "")
        for item in results
        if isinstance(item, dict)
    }

    passed = 0
    for task in tasks:
        task_id = task["task_id"]
        answer = answers.get(task_id, "")
        ok, failures = score_answer(answer, task.get("expect", {}))
        passed += int(ok)
        marker = "PASS" if ok else "FAIL"
        details = "" if ok else f" — {', '.join(failures) or 'missing answer'}"
        print(f"{marker} {task_id}{details}")

    print(f"\nScore: {passed}/{len(tasks)}; required: {args.required}/{len(tasks)}")
    return 0 if passed >= args.required else 1


if __name__ == "__main__":
    raise SystemExit(main())

