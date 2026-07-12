from pathlib import Path

from tokenrouter.config import ModelCatalog, Settings
from tokenrouter.types import RoutingProfile


def make_settings(**overrides: object) -> Settings:
    values = {
        "profile": RoutingProfile.HYBRID,
        "fireworks_api_key": "test-key",
        "fireworks_base_url": "https://example.test/inference/v1",
        "allowed_models": (
            "accounts/fireworks/models/minimax-m3",
            "kimi-k2p7-code",
        ),
        "model_path": Path("model.gguf"),
        "input_path": Path("tasks.json"),
        "output_path": Path("results.json"),
    }
    values.update(overrides)
    return Settings(**values)


def test_catalog_returns_exact_allowlisted_ids() -> None:
    settings = make_settings()
    catalog = ModelCatalog(settings.allowed_models)
    assert catalog.general() == "accounts/fireworks/models/minimax-m3"
    assert catalog.code() == "kimi-k2p7-code"
    assert catalog.contains(catalog.general())


def test_catalog_does_not_invent_models() -> None:
    catalog = ModelCatalog(("gemma-4-31b-it",))
    assert catalog.general() is None
    assert catalog.code() is None

