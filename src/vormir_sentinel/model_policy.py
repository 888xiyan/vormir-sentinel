"""GPU/CPU/offline model profile selection without host command execution."""

from __future__ import annotations

import os
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, cast

from vormir_sentinel.config import ConfigError

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODELS_PATH = PROJECT_ROOT / "config" / "models.toml"

RunMode = Literal["auto", "gpu", "cpu", "offline"]


class ModelPolicyError(ConfigError):
    """Raised when the local model catalog is malformed."""


@dataclass(frozen=True)
class ModelProfile:
    name: str
    provider: str
    model: str
    display_name: str
    context: int = 4096
    temperature: float = 0.8
    top_p: float = 0.9
    repeat_penalty: float = 1.08
    num_predict: int = 320
    num_gpu: int | None = None
    threads: int | None = None

    @property
    def is_offline(self) -> bool:
        return self.provider == "offline"

    def request_options(self) -> dict[str, int | float]:
        options: dict[str, int | float] = {
            "num_ctx": self.context,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "repeat_penalty": self.repeat_penalty,
            "num_predict": self.num_predict,
        }
        if self.num_gpu is not None:
            options["num_gpu"] = self.num_gpu
        if self.threads is not None:
            options["threads"] = self.threads
        return options


@dataclass(frozen=True)
class ModelCatalog:
    gpu_profile_name: str
    cpu_profile_name: str
    offline_profile_name: str
    profiles: dict[str, ModelProfile]
    minimum_gpu_memory_gib: float = 6.5
    minimum_available_memory_gib: float = 2.5

    @classmethod
    def load(cls, path: str | Path | None = None) -> ModelCatalog:
        selected = Path(path).expanduser() if path is not None else DEFAULT_MODELS_PATH
        if not selected.exists():
            if path is not None:
                raise ModelPolicyError(f"Model catalog not found: {selected}")
            return _fallback_catalog()

        try:
            with selected.open("rb") as handle:
                data = tomllib.load(handle)
        except (OSError, tomllib.TOMLDecodeError) as exc:
            raise ModelPolicyError(f"Cannot read model catalog {selected}: {exc}") from exc

        selection = data.get("selection")
        profile_data = data.get("profiles")
        detection = data.get("detection", {})
        if not isinstance(selection, dict) or not isinstance(profile_data, dict):
            raise ModelPolicyError("Model catalog requires [selection] and [profiles].")
        if not isinstance(detection, dict):
            raise ModelPolicyError("[detection] must be a table.")

        profiles: dict[str, ModelProfile] = {}
        for name, raw in profile_data.items():
            if not isinstance(raw, dict):
                raise ModelPolicyError(f"Profile {name!r} must be a table.")
            profiles[name] = _parse_profile(name, raw)

        gpu = _selection_name(selection, "gpu_profile", profiles)
        cpu = _selection_name(selection, "cpu_profile", profiles)
        offline = _selection_name(selection, "offline_profile", profiles)

        return cls(
            gpu_profile_name=gpu,
            cpu_profile_name=cpu,
            offline_profile_name=offline,
            profiles=profiles,
            minimum_gpu_memory_gib=_positive_float(detection, "minimum_gpu_vram_gib", 6.5),
            minimum_available_memory_gib=_positive_float(
                detection, "minimum_available_memory_gib", 2.5
            ),
        )

    @property
    def gpu_profile(self) -> ModelProfile:
        return self.profiles[self.gpu_profile_name]

    @property
    def cpu_profile(self) -> ModelProfile:
        return self.profiles[self.cpu_profile_name]

    @property
    def offline_profile(self) -> ModelProfile:
        return self.profiles[self.offline_profile_name]

    def candidates(self, mode: RunMode) -> tuple[ModelProfile, ...]:
        """Return ordered model profiles for a requested run mode."""
        emergency = self.profiles.get("gpu_emergency")
        if mode == "offline":
            return (self.offline_profile,)
        if mode == "gpu":
            return tuple(profile for profile in (self.gpu_profile, emergency) if profile)
        if mode == "cpu":
            return (self.cpu_profile,)

        memory = available_memory_gib()
        if memory is not None and memory < self.minimum_available_memory_gib:
            return (self.offline_profile,)
        if memory is None or memory >= self.minimum_gpu_memory_gib:
            return tuple(
                profile
                for profile in (self.gpu_profile, emergency, self.cpu_profile, self.offline_profile)
                if profile
            )
        return (self.cpu_profile, self.offline_profile)


def _positive_float(table: dict[str, object], key: str, default: float) -> float:
    value = table.get(key, default)
    if isinstance(value, bool) or not isinstance(value, int | float) or value <= 0:
        raise ModelPolicyError(f"[detection] {key} must be a positive number.")
    return float(value)


def _selection_name(
    selection: dict[str, object], key: str, profiles: dict[str, ModelProfile]
) -> str:
    value = selection.get(key)
    if not isinstance(value, str) or value not in profiles:
        raise ModelPolicyError(f"[selection] {key} must name an existing profile.")
    return value


def _parse_profile(name: str, raw: dict[str, object]) -> ModelProfile:
    provider = raw.get("provider")
    model = raw.get("model")
    display_name = raw.get("display_name")
    if not isinstance(provider, str) or not isinstance(model, str):
        raise ModelPolicyError(f"Profile {name!r} requires string provider and model.")
    if not isinstance(display_name, str):
        raise ModelPolicyError(f"Profile {name!r} requires display_name.")

    num_gpu = raw.get("num_gpu")
    threads = raw.get("threads")
    return ModelProfile(
        name=name,
        provider=provider,
        model=model,
        display_name=display_name,
        context=_profile_int(raw, "context", 4096),
        temperature=_profile_number(raw, "temperature", 0.8),
        top_p=_profile_number(raw, "top_p", 0.9),
        repeat_penalty=_profile_number(raw, "repeat_penalty", 1.08),
        num_predict=_profile_int(raw, "num_predict", 320),
        num_gpu=_profile_optional_int("num_gpu", num_gpu),
        threads=_profile_optional_int("threads", threads),
    )


def _profile_int(raw: dict[str, object], key: str, default: int) -> int:
    value = raw.get(key, default)
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ModelPolicyError(f"Profile field {key!r} must be a positive integer.")
    return value


def _profile_number(raw: dict[str, object], key: str, default: float) -> float:
    value = raw.get(key, default)
    if isinstance(value, bool) or not isinstance(value, int | float) or value < 0:
        raise ModelPolicyError(f"Profile field {key!r} must be a non-negative number.")
    return float(value)


def _profile_optional_int(key: str, value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ModelPolicyError(f"Profile field {key!r} must be a non-negative integer.")
    return value


def _fallback_catalog() -> ModelCatalog:
    profiles = {
        "gpu_primary": ModelProfile(
            name="gpu_primary",
            provider="ollama",
            model="qwen2.5:7b-instruct-q4_K_M",
            display_name="Qwen2.5 7B Instruct / Q4_K_M",
            context=8192,
            temperature=0.85,
            top_p=0.90,
            repeat_penalty=1.08,
            num_predict=320,
            num_gpu=999,
        ),
        "cpu_fallback": ModelProfile(
            name="cpu_fallback",
            provider="ollama",
            model="qwen2.5:3b-instruct-q4_K_M",
            display_name="Qwen2.5 3B Instruct / Q4_K_M",
            context=4096,
            temperature=0.82,
            top_p=0.90,
            repeat_penalty=1.10,
            num_predict=220,
            threads=12,
        ),
        "story_only": ModelProfile(
            name="story_only",
            provider="offline",
            model="none",
            display_name="Vormir Offline Story",
        ),
    }
    return ModelCatalog(
        gpu_profile_name="gpu_primary",
        cpu_profile_name="cpu_fallback",
        offline_profile_name="story_only",
        profiles=profiles,
    )


def available_memory_gib() -> float | None:
    """Return estimated available system memory without executing host commands."""
    try:
        if sys.platform.startswith("linux"):
            return _linux_available_memory_gib()
        if sys.platform == "win32":
            return _windows_available_memory_gib()
        return _portable_available_memory_gib()
    except (AttributeError, OSError, ValueError):
        return None


def _linux_available_memory_gib() -> float | None:
    meminfo = Path("/proc/meminfo")
    if not meminfo.exists():
        return _portable_available_memory_gib()
    values: dict[str, int] = {}
    for line in meminfo.read_text(encoding="ascii").splitlines():
        key, separator, rest = line.partition(":")
        if not separator:
            continue
        parts = rest.split()
        if parts and parts[0].isdigit():
            values[key] = int(parts[0]) * 1024
    available = values.get("MemAvailable")
    if available is None:
        available = sum(values.get(key, 0) for key in ("MemFree", "Buffers", "Cached"))
    return available / (1024**3)


def _windows_available_memory_gib() -> float | None:
    import ctypes

    class MemoryStatusEx(ctypes.Structure):
        _fields_ = [
            ("length", ctypes.c_uint32),
            ("memory_load", ctypes.c_uint32),
            ("total_physical", ctypes.c_uint64),
            ("available_physical", ctypes.c_uint64),
            ("total_page_file", ctypes.c_uint64),
            ("available_page_file", ctypes.c_uint64),
            ("total_virtual", ctypes.c_uint64),
            ("available_virtual", ctypes.c_uint64),
            ("available_extended_virtual", ctypes.c_uint64),
        ]

    status = MemoryStatusEx()
    status.length = ctypes.sizeof(MemoryStatusEx)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):  # type: ignore[attr-defined]
        return None
    return cast(float, status.available_physical / (1024**3))


def _portable_available_memory_gib() -> float | None:
    pages = os.sysconf("SC_AVPHYS_PAGES")
    page_size = os.sysconf("SC_PAGE_SIZE")
    if pages <= 0 or page_size <= 0:
        return None
    return float(pages * page_size / (1024**3))
