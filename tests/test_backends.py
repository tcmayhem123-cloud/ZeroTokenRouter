from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import requests

from tokenrouter.backends import BackendError, FireworksBackend
from tokenrouter.config import Settings
from tokenrouter.types import Backend, Category, RouteDecision, RoutingProfile


class FakeResponse:
    def __init__(self, status_code: int, payload: dict[str, Any]) -> None:
        self.status_code = status_code
        self._payload = payload

    def json(self) -> dict[str, Any]:
        return self._payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")


class FakeSession:
    def __init__(self, responses: list[FakeResponse]) -> None:
        self.responses = responses
        self.calls: list[dict[str, Any]] = []

    def post(self, url: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"url": url, **kwargs})
        return self.responses.pop(0)


def settings(tmp_path: Path) -> Settings:
    return Settings(
        profile=RoutingProfile.HYBRID,
        fireworks_api_key="test-key",
        fireworks_base_url="https://proxy.test/inference/v1/",
        allowed_models=("minimax-m3", "kimi-k2p7-code"),
        model_path=tmp_path / "model.gguf",
        input_path=tmp_path / "tasks.json",
        output_path=tmp_path / "results.json",
    )


def completion(text: str = "answer") -> dict[str, Any]:
    return {"choices": [{"message": {"content": text}}]}


def test_fireworks_uses_injected_proxy_and_exact_model(tmp_path: Path) -> None:
    session = FakeSession([FakeResponse(200, completion())])
    backend = FireworksBackend(settings(tmp_path), session=session)
    decision = RouteDecision(
        Category.FACTUAL, Backend.FIREWORKS, "minimax-m3", 180, "none"
    )

    assert backend.answer(decision, "What is HTTP?") == "answer"
    assert session.calls[0]["url"] == "https://proxy.test/inference/v1/chat/completions"
    assert session.calls[0]["json"]["model"] == "minimax-m3"
    assert session.calls[0]["timeout"] == (3.05, 12)
    assert session.calls[0]["headers"]["Authorization"] == "Bearer test-key"


def test_reasoning_parameter_falls_back_once_on_compatibility_error(
    tmp_path: Path,
) -> None:
    session = FakeSession(
        [FakeResponse(400, {"error": "unsupported"}), FakeResponse(200, completion())]
    )
    backend = FireworksBackend(settings(tmp_path), session=session)
    decision = RouteDecision(
        Category.LOGIC, Backend.FIREWORKS, "minimax-m3", 260, "low"
    )

    assert backend.answer(decision, "Solve this puzzle") == "answer"
    assert len(session.calls) == 2
    assert "reasoning_effort" in session.calls[0]["json"]
    assert "reasoning_effort" not in session.calls[1]["json"]


def test_fireworks_refuses_non_allowlisted_model(tmp_path: Path) -> None:
    backend = FireworksBackend(
        settings(tmp_path), session=FakeSession([FakeResponse(200, completion())])
    )
    decision = RouteDecision(
        Category.FACTUAL, Backend.FIREWORKS, "gemma-4-31b-it", 180
    )

    with pytest.raises(BackendError, match="ALLOWED_MODELS"):
        backend.answer(decision, "prompt")
