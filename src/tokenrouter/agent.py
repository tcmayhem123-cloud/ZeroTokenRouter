from __future__ import annotations

import json
import logging
import os
import re
import tempfile
from concurrent.futures import Future, ThreadPoolExecutor
from pathlib import Path

from .backends import BackendError, FireworksBackend, LocalBackend
from .config import ModelCatalog, Settings
from .fast_answers import answer as fast_answer
from .routing import decide
from .types import Backend, Category, Result, RouteDecision, RoutingProfile, Task
from .verification import verify_answer

LOGGER = logging.getLogger("tokenrouter")


class Agent:
    def __init__(
        self,
        settings: Settings,
        *,
        local: LocalBackend | None = None,
        remote: FireworksBackend | None = None,
    ) -> None:
        self.settings = settings
        self.catalog = ModelCatalog(settings.allowed_models)
        self.local = local or LocalBackend(settings)
        self.remote = remote or FireworksBackend(settings)

    def run(self, tasks: list[Task]) -> list[Result]:
        decisions = {
            task.task_id: decide(task, self.settings.profile, self.catalog)
            for task in tasks
        }
        answers: dict[str, str] = {}
        remote_jobs: dict[str, Future[str]] = {}
        local_results: dict[str, str] = {}
        
        # 1. First pass: Run local candidate tasks and verify them
        unverified_tasks: list[Task] = []
        for task in tasks:
            decision = decisions[task.task_id]
            if decision.backend is Backend.LOCAL:
                local_ans = self._answer_local(task, decision)
                local_results[task.task_id] = local_ans
                
                # Verify local response format and compliance
                if verify_answer(decision.category, task.prompt, local_ans):
                    answers[task.task_id] = local_ans
                else:
                    unverified_tasks.append(task)

        # 2. Second pass: Run remote tasks and escalated local tasks in parallel
        with ThreadPoolExecutor(max_workers=self.settings.remote_workers) as pool:
            for task in tasks:
                decision = decisions[task.task_id]
                needs_remote = (
                    decision.backend is Backend.FIREWORKS or
                    (task in unverified_tasks and self.remote.available)
                )
                if needs_remote and self.remote.available:
                    # If this is an escalated local task, construct a remote RouteDecision
                    escalation_decision = decision
                    if decision.backend is Backend.LOCAL:
                        is_code = decision.category in {Category.CODE_DEBUGGING, Category.CODE_GENERATION}
                        model = self.catalog.code() if is_code else self.catalog.general()
                        escalation_decision = RouteDecision(
                            category=decision.category,
                            backend=Backend.FIREWORKS,
                            model=model,
                            max_tokens=decision.max_tokens,
                            reasoning_effort="low" if decision.category in {Category.MATH, Category.LOGIC} else "none"
                        )
                    remote_jobs[task.task_id] = pool.submit(
                        self.remote.answer, escalation_decision, task.prompt
                    )
            
            # 3. Third pass: Collect results, falling back to local if remote fails
            for task in tasks:
                if task.task_id in answers:
                    continue  # Already resolved locally
                
                future = remote_jobs.get(task.task_id)
                if future is not None:
                    try:
                        answers[task.task_id] = future.result()
                    except Exception as exc:
                        LOGGER.warning(
                            "Remote route failed for %s; using local fallback: %s",
                            task.task_id,
                            type(exc).__name__,
                        )
                        answers[task.task_id] = local_results.get(
                            task.task_id,
                            self._answer_local(task, decisions[task.task_id])
                        )
                else:
                    # No remote job ran; use local result
                    answers[task.task_id] = local_results.get(
                        task.task_id,
                        self._answer_local(task, decisions[task.task_id])
                    )

        return [Result(task.task_id, answers[task.task_id]) for task in tasks]

    def _answer_local(self, task: Task, decision: RouteDecision) -> str:
        deterministic = fast_answer(decision.category, task.prompt)
        if deterministic is not None:
            return deterministic
        try:
            return self.local.answer(
                decision.category, task.prompt, decision.max_tokens
            )
        except BackendError as exc:
            LOGGER.error(
                "Local route failed for %s; using deterministic emergency answer: %s",
                task.task_id,
                type(exc).__name__,
            )
            return emergency_answer(decision.category, task.prompt)


def emergency_answer(category: Category, prompt: str) -> str:
    """Last-resort schema preservation; normal submissions use Qwen or Fireworks."""
    if category is Category.SENTIMENT:
        text = prompt.lower()
        positives = sum(word in text for word in ("great", "good", "excellent", "love"))
        negatives = sum(word in text for word in ("bad", "poor", "hate", "scratch"))
        label = "mixed" if positives and negatives else "positive" if positives else "negative"
        return f"{label.capitalize()} sentiment."
    if category is Category.SUMMARIZATION:
        body = prompt.split(":", 1)[-1].strip()
        sentence = re.split(r"(?<=[.!?])\s+", body)[0]
        return sentence[:500] or "No source text was provided."
    if category is Category.NER:
        names = re.findall(r"\b(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b", prompt)
        unique = list(dict.fromkeys(names))
        return "; ".join(f"{name}: ENTITY" for name in unique) or "No named entities."
    if category is Category.MATH:
        expression = re.search(r"(-?\d+(?:\.\d+)?)\s*([+\-*/])\s*(-?\d+(?:\.\d+)?)", prompt)
        if expression:
            left, op, right = expression.groups()
            values = {"+": float(left) + float(right), "-": float(left) - float(right), "*": float(left) * float(right)}
            if op == "/" and float(right) != 0:
                value = float(left) / float(right)
            else:
                value = values.get(op)
            if value is not None:
                return f"{value:g}"
    return "Unable to produce a verified answer with the available inference backends."


def load_tasks(path: Path) -> list[Task]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("tasks.json must contain a JSON array")
    tasks = [Task.from_dict(item) for item in raw]
    ids = [task.task_id for task in tasks]
    if len(ids) != len(set(ids)):
        raise ValueError("task_id values must be unique")
    return tasks


def write_results(path: Path, results: list[Result]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = [result.as_dict() for result in results]
    handle, temporary_name = tempfile.mkstemp(
        dir=path.parent, prefix="results-", suffix=".json"
    )
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as temporary:
            json.dump(payload, temporary, ensure_ascii=False, indent=2)
            temporary.write("\n")
        os.replace(temporary_name, path)
    except Exception:
        Path(temporary_name).unlink(missing_ok=True)
        raise


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    try:
        settings = Settings.from_env()
        tasks = load_tasks(settings.input_path)
        results = Agent(settings).run(tasks)
        write_results(settings.output_path, results)
    except Exception:
        LOGGER.exception("Agent execution failed")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
