from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from .types import RoutingProfile


@dataclass(frozen=True, slots=True)
class Settings:
    profile: RoutingProfile
    fireworks_api_key: str | None
    fireworks_base_url: str | None
    allowed_models: tuple[str, ...]
    model_path: Path
    input_path: Path
    output_path: Path
    local_threads: int = 2
    local_context: int = 4096
    remote_workers: int = 3

    @classmethod
    def from_env(cls) -> "Settings":
        raw_profile = os.getenv("ROUTING_PROFILE", RoutingProfile.HYBRID.value).lower()
        try:
            profile = RoutingProfile(raw_profile)
        except ValueError as exc:
            choices = ", ".join(item.value for item in RoutingProfile)
            raise ValueError(f"ROUTING_PROFILE must be one of: {choices}") from exc

        raw_models = os.getenv("ALLOWED_MODELS", "")
        allowed_models = tuple(
            model.strip() for model in raw_models.split(",") if model.strip()
        )
        return cls(
            profile=profile,
            fireworks_api_key=os.getenv("FIREWORKS_API_KEY") or None,
            fireworks_base_url=os.getenv("FIREWORKS_BASE_URL") or None,
            allowed_models=allowed_models,
            model_path=Path(
                os.getenv(
                    "MODEL_PATH", "/app/models/qwen2.5-3b-instruct-q4_k_m.gguf"
                )
            ),
            input_path=Path(os.getenv("INPUT_PATH", "/input/tasks.json")),
            output_path=Path(os.getenv("OUTPUT_PATH", "/output/results.json")),
            local_threads=max(1, int(os.getenv("LOCAL_THREADS", "2"))),
            local_context=max(512, int(os.getenv("LOCAL_CONTEXT", "4096"))),
            remote_workers=max(1, int(os.getenv("REMOTE_WORKERS", "3"))),
        )


class ModelCatalog:
    """Selects only exact IDs supplied by the grading harness."""

    GENERAL_SUFFIXES = ("minimax-m3",)
    CODE_SUFFIXES = ("kimi-k2p7-code", "minimax-m3")

    def __init__(self, allowed_models: tuple[str, ...]):
        self.allowed_models = allowed_models

    def general(self) -> str | None:
        return self._select(self.GENERAL_SUFFIXES)

    def code(self) -> str | None:
        return self._select(self.CODE_SUFFIXES)

    def contains(self, model: str) -> bool:
        return model in self.allowed_models

    def _select(self, suffixes: tuple[str, ...]) -> str | None:
        for suffix in suffixes:
            for model in self.allowed_models:
                normalized = model.rstrip("/").lower()
                if normalized == suffix or normalized.endswith(f"/{suffix}"):
                    return model
        return None

