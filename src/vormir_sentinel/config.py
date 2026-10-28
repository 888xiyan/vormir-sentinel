"""Configuration loading with explicit safety invariants."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "app.toml"


class ConfigError(ValueError):
    """Raised when runtime configuration is invalid or unsafe."""


@dataclass(frozen=True)
class AppConfig:
    language: str = "zh-CN"
    safe_mode: bool = False
    low_stimulation: bool = False
    skip_installation_on_return: bool = True


@dataclass(frozen=True)
class LLMConfig:
    provider: str = "ollama"
    base_url: str = "http://127.0.0.1:11434"
    model: str = "qwen2.5:7b-instruct-q4_K_M"
    temperature: float = 0.85
    top_p: float = 0.90
    num_ctx: int = 8192
    stream: bool = True


@dataclass(frozen=True)
class OutputConfig:
    workspace: Path = Path("./vormir-output")
    allow_desktop_output: bool = False
    allow_overwrite: bool = False


@dataclass(frozen=True)
class SafetyConfig:
    allow_network: bool = False
    allow_local_inference: bool = True
    allow_filesystem_exploration: bool = False
    allow_real_command_execution: bool = False


@dataclass(frozen=True)
class Config:
    app: AppConfig = AppConfig()
    llm: LLMConfig = LLMConfig()
    output: OutputConfig = OutputConfig()
    safety: SafetyConfig = SafetyConfig()
    source_path: Path | None = None


def _expect_type(section: str, key: str, value: Any, expected: type[Any]) -> Any:
    if not isinstance(value, expected):
        raise ConfigError(f"Invalid configuration: [{section}] {key} must be {expected.__name__}.")
    return value


def _bool(section: str, key: str, value: Any) -> bool:
    return bool(_expect_type(section, key, value, bool))


def _str(section: str, key: str, value: Any) -> str:
    return str(_expect_type(section, key, value, str))


def _int(section: str, key: str, value: Any, *, minimum: int = 0) -> int:
    # bool is an int subclass, so reject it explicitly.
    if isinstance(value, bool):
        raise ConfigError(f"Invalid configuration: [{section}] {key} must be int.")
    result = int(_expect_type(section, key, value, int))
    if result < minimum:
        raise ConfigError(f"Invalid configuration: [{section}] {key} must be >= {minimum}.")
    return result


def _float(section: str, key: str, value: Any, *, minimum: float, maximum: float) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise ConfigError(f"Invalid configuration: [{section}] {key} must be a number.")
    result = float(value)
    if not minimum <= result <= maximum:
        raise ConfigError(
            f"Invalid configuration: [{section}] {key} must be between {minimum} and {maximum}."
        )
    return result


def _table(data: dict[str, Any], name: str) -> dict[str, Any]:
    value = data.get(name, {})
    if not isinstance(value, dict):
        raise ConfigError(f"Invalid configuration: [{name}] must be a table.")
    return value


def load_config(path: str | Path | None = None) -> Config:
    """Load a TOML configuration or return the built-in safe defaults."""
    selected = Path(path).expanduser() if path is not None else DEFAULT_CONFIG_PATH
    if not selected.exists():
        if path is not None:
            raise ConfigError(f"Configuration file not found: {selected}")
        return Config(source_path=None)

    try:
        with selected.open("rb") as handle:
            data = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise ConfigError(f"Cannot read configuration {selected}: {exc}") from exc

    app_data = _table(data, "app")
    llm_data = _table(data, "llm")
    output_data = _table(data, "output")
    safety_data = _table(data, "safety")

    app = AppConfig(
        language=_str("app", "language", app_data.get("language", "zh-CN")),
        safe_mode=_bool("app", "safe_mode", app_data.get("safe_mode", False)),
        low_stimulation=_bool("app", "low_stimulation", app_data.get("low_stimulation", False)),
        skip_installation_on_return=_bool(
            "app",
            "skip_installation_on_return",
            app_data.get("skip_installation_on_return", True),
        ),
    )

    llm = LLMConfig(
        provider=_str("llm", "provider", llm_data.get("provider", "ollama")),
        base_url=_str("llm", "base_url", llm_data.get("base_url", "http://127.0.0.1:11434")),
        model=_str("llm", "model", llm_data.get("model", "qwen2.5:7b-instruct-q4_K_M")),
        temperature=_float(
            "llm", "temperature", llm_data.get("temperature", 0.85), minimum=0.0, maximum=2.0
        ),
        top_p=_float("llm", "top_p", llm_data.get("top_p", 0.90), minimum=0.0, maximum=1.0),
        num_ctx=_int("llm", "num_ctx", llm_data.get("num_ctx", 8192), minimum=1),
        stream=_bool("llm", "stream", llm_data.get("stream", True)),
    )

    workspace_value = _str("output", "workspace", output_data.get("workspace", "./vormir-output"))
    output = OutputConfig(
        workspace=Path(workspace_value).expanduser(),
        allow_desktop_output=_bool(
            "output",
            "allow_desktop_output",
            output_data.get("allow_desktop_output", False),
        ),
        allow_overwrite=_bool(
            "output", "allow_overwrite", output_data.get("allow_overwrite", False)
        ),
    )

    safety = SafetyConfig(
        allow_network=_bool("safety", "allow_network", safety_data.get("allow_network", False)),
        allow_local_inference=_bool(
            "safety",
            "allow_local_inference",
            safety_data.get("allow_local_inference", True),
        ),
        allow_filesystem_exploration=_bool(
            "safety",
            "allow_filesystem_exploration",
            safety_data.get("allow_filesystem_exploration", False),
        ),
        allow_real_command_execution=_bool(
            "safety",
            "allow_real_command_execution",
            safety_data.get("allow_real_command_execution", False),
        ),
    )

    if safety.allow_network:
        raise ConfigError(
            "Unsafe configuration rejected: remote networking must remain false; "
            "only loopback Ollama inference is supported."
        )
    if safety.allow_real_command_execution:
        raise ConfigError(
            "Unsafe configuration rejected: allow_real_command_execution must remain false."
        )
    if safety.allow_filesystem_exploration:
        raise ConfigError(
            "Unsafe configuration rejected: allow_filesystem_exploration must remain false."
        )

    return Config(
        app=app,
        llm=llm,
        output=output,
        safety=safety,
        source_path=selected.resolve(),
    )


def apply_cli_overrides(
    config: Config,
    *,
    safe_mode: bool = False,
    low_stimulation: bool = False,
    offline: bool = False,
) -> Config:
    """Apply immutable CLI overrides while preserving non-negotiable safety rules."""
    app = config.app
    safety = config.safety

    if safe_mode:
        app = replace(app, safe_mode=True, low_stimulation=True)
    if low_stimulation:
        app = replace(app, low_stimulation=True)
    if safe_mode or offline:
        safety = replace(
            safety,
            allow_network=False,
            allow_local_inference=False,
            allow_filesystem_exploration=False,
            allow_real_command_execution=False,
        )

    return replace(config, app=app, safety=safety)
