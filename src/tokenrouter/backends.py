from __future__ import annotations

import threading
import time
from collections.abc import Callable
from typing import Any, Protocol

import requests

from .config import ModelCatalog, Settings
from .prompts import REMOTE_SYSTEM, local_system
from .types import Category, RouteDecision


class BackendError(RuntimeError):
    pass


class ChatEngine(Protocol):
    def create_chat_completion(self, **kwargs: Any) -> dict[str, Any]: ...


class FireworksBackend:
    def __init__(
        self,
        settings: Settings,
        *,
        session: requests.Session | None = None,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        self._settings = settings
        self._catalog = ModelCatalog(settings.allowed_models)
        self._session = session or requests.Session()
        self._sleep = sleeper

    @property
    def available(self) -> bool:
        return bool(
            self._settings.fireworks_api_key
            and self._settings.fireworks_base_url
            and self._settings.allowed_models
        )

    def answer(self, decision: RouteDecision, prompt: str) -> str:
        if not self.available:
            raise BackendError("Fireworks credentials or allowlist are unavailable")
        if decision.model is None or not self._catalog.contains(decision.model):
            raise BackendError("Refusing to call a model absent from ALLOWED_MODELS")

        payload: dict[str, Any] = {
            "model": decision.model,
            "messages": [
                {"role": "system", "content": REMOTE_SYSTEM},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0,
            "max_tokens": decision.max_tokens,
        }
        if decision.reasoning_effort:
            payload["reasoning_effort"] = decision.reasoning_effort

        response = self._post(payload)
        if response.status_code in {400, 422} and "reasoning_effort" in payload:
            compatible_payload = dict(payload)
            compatible_payload.pop("reasoning_effort")
            response = self._post(compatible_payload, retry_transient=False)

        try:
            response.raise_for_status()
            body = response.json()
            content = body["choices"][0]["message"]["content"]
        except (requests.RequestException, ValueError, KeyError, IndexError, TypeError) as exc:
            raise BackendError("Invalid Fireworks response") from exc

        if isinstance(content, str):
            answer = content.strip()
        elif isinstance(content, list):
            answer = "".join(
                str(block.get("text", ""))
                for block in content
                if isinstance(block, dict) and block.get("type") in {None, "text"}
            ).strip()
        else:
            answer = ""
        if not answer:
            raise BackendError("Fireworks returned an empty answer")
        return answer

    def _post(
        self, payload: dict[str, Any], *, retry_transient: bool = True
    ) -> requests.Response:
        base_url = str(self._settings.fireworks_base_url).rstrip("/")
        url = f"{base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self._settings.fireworks_api_key}",
            "Content-Type": "application/json",
        }
        attempts = 2 if retry_transient else 1
        last_error: requests.RequestException | None = None
        for attempt in range(attempts):
            try:
                response = self._session.post(
                    url,
                    headers=headers,
                    json=payload,
                    # Two transient attempts plus the backoff remain below the
                    # track's 30-second per-request ceiling.
                    timeout=(3.05, 12),
                )
            except requests.RequestException as exc:
                last_error = exc
                if attempt + 1 < attempts:
                    self._sleep(0.5)
                    continue
                raise BackendError("Fireworks request failed") from exc
            if response.status_code == 429 or response.status_code >= 500:
                if attempt + 1 < attempts:
                    self._sleep(0.5)
                    continue
            return response
        raise BackendError("Fireworks request failed") from last_error


class LocalBackend:
    def __init__(
        self,
        settings: Settings,
        *,
        engine_factory: Callable[[Settings], ChatEngine] | None = None,
    ) -> None:
        self._settings = settings
        self._engine_factory = engine_factory or _default_engine_factory
        self._engine: ChatEngine | None = None
        self._lock = threading.Lock()

    def answer(self, category: Category, prompt: str, max_tokens: int) -> str:
        with self._lock:
            engine = self._get_engine()
            try:
                response = engine.create_chat_completion(
                    messages=[
                        {"role": "system", "content": local_system(category)},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0,
                    top_p=0.9,
                    max_tokens=max_tokens,
                    seed=0,
                )
                content = response["choices"][0]["message"]["content"]
            except (ValueError, KeyError, IndexError, TypeError) as exc:
                raise BackendError("Invalid local model response") from exc
        if not isinstance(content, str) or not content.strip():
            raise BackendError("Local model returned an empty answer")
        return content.strip()

    def _get_engine(self) -> ChatEngine:
        if self._engine is None:
            self._engine = self._engine_factory(self._settings)
        return self._engine


def _default_engine_factory(settings: Settings) -> ChatEngine:
    if not settings.model_path.is_file():
        raise BackendError(f"Local model is missing: {settings.model_path}")
    try:
        from llama_cpp import Llama
    except ImportError as exc:
        raise BackendError("llama-cpp-python is not installed") from exc
    return Llama(
        model_path=str(settings.model_path),
        n_ctx=settings.local_context,
        n_threads=settings.local_threads,
        n_threads_batch=settings.local_threads,
        n_batch=64,
        seed=0,
        use_mmap=True,
        verbose=False,
    )
