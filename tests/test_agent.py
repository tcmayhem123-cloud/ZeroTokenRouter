from __future__ import annotations

import json
from pathlib import Path

from tokenrouter.agent import Agent, load_tasks, write_results
from tokenrouter.backends import BackendError
from tokenrouter.config import Settings
from tokenrouter.types import Category, RoutingProfile, Task


class FakeLocal:
    def answer(self, category: Category, prompt: str, max_tokens: int) -> str:
        return f"local:{category.value}"


class FakeRemote:
    available = True

    def __init__(self, fail: bool = False) -> None:
        self.fail = fail

    def answer(self, decision: object, prompt: str) -> str:
        if self.fail:
            raise BackendError("simulated")
        return "remote:ok"


def settings(tmp_path: Path, profile: RoutingProfile = RoutingProfile.HYBRID) -> Settings:
    return Settings(
        profile=profile,
        fireworks_api_key="test-key",
        fireworks_base_url="https://example.test/inference/v1",
        allowed_models=("minimax-m3", "kimi-k2p7-code"),
        model_path=tmp_path / "model.gguf",
        input_path=tmp_path / "tasks.json",
        output_path=tmp_path / "results.json",
    )


def test_agent_preserves_order_and_routes(tmp_path: Path) -> None:
    agent = Agent(settings(tmp_path), local=FakeLocal(), remote=FakeRemote())
    results = agent.run(
        [
            Task("sentiment", "Classify sentiment: great."),
            Task("factual", "What is photosynthesis?"),
        ]
    )
    assert [result.task_id for result in results] == ["sentiment", "factual"]
    assert results[0].answer.startswith("Positive sentiment:")
    assert results[1].answer == "remote:ok"


class FakeLocalFail:
    def answer(self, category: Category, prompt: str, max_tokens: int) -> str:
        raise BackendError("local failed")


def test_remote_failure_falls_back_locally(tmp_path: Path) -> None:
    agent = Agent(settings(tmp_path), local=FakeLocalFail(), remote=FakeRemote(fail=True))
    result = agent.run([Task("factual", "What is photosynthesis?")])[0]
    assert result.answer.startswith("Unable to produce a verified answer")


def test_load_and_atomic_write(tmp_path: Path) -> None:
    task_path = tmp_path / "tasks.json"
    task_path.write_text('[{"task_id":"t1","prompt":"Hello"}]', encoding="utf-8")
    tasks = load_tasks(task_path)
    assert tasks == [Task("t1", "Hello")]

    output_path = tmp_path / "nested" / "results.json"
    agent = Agent(
        settings(tmp_path, RoutingProfile.LOCAL),
        local=FakeLocal(),
        remote=FakeRemote(),
    )
    write_results(output_path, agent.run(tasks))
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload == [{"task_id": "t1", "answer": "local:factual"}]
