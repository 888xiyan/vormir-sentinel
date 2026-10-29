"""Read-only Ollama discovery and safe startup model selection."""

from __future__ import annotations

import contextlib
import re
from collections.abc import Callable
from dataclasses import dataclass, replace
from typing import Literal

from vormir_sentinel.config import Config
from vormir_sentinel.model_policy import ModelCatalog, ModelProfile, RunMode, available_memory_gib
from vormir_sentinel.ollama import InstalledModel, OllamaClient, OllamaError

StartupStatus = Literal[
    "OLLAMA_READY_GPU",
    "OLLAMA_READY_CPU",
    "OLLAMA_READY_CUSTOM",
    "OLLAMA_NO_MODEL",
    "OLLAMA_NOT_RUNNING",
    "OFFLINE",
]

_SAFE_MODEL_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}$")


def is_dialogue_model(model: InstalledModel) -> bool:
    """Exclude embedding and other non-chat model families from selection."""
    family = (model.family or "").lower()
    name = model.name.lower()
    return "embedding" not in family and "embedding" not in name


@dataclass(frozen=True)
class StartupDiscovery:
    status: StartupStatus
    models: tuple[InstalledModel, ...] = ()
    endpoint: str = "http://127.0.0.1:11434"
    memory_gib: float | None = None
    message: str = ""

    @property
    def available(self) -> bool:
        return self.status != "OLLAMA_NOT_RUNNING"

    @property
    def model_names(self) -> tuple[str, ...]:
        return tuple(model.name for model in self.models)

    @property
    def dialogue_models(self) -> tuple[InstalledModel, ...]:
        return tuple(model for model in self.models if is_dialogue_model(model))

    @property
    def dialogue_model_names(self) -> tuple[str, ...]:
        return tuple(model.name for model in self.dialogue_models)


@dataclass(frozen=True)
class StartupSelection:
    mode: RunMode
    status: StartupStatus
    active_profile: ModelProfile
    profiles: tuple[ModelProfile, ...]
    source: str = "automatic"
    message: str = ""

    @property
    def model_name(self) -> str:
        return self.active_profile.model

    @property
    def mode_label(self) -> str:
        if self.active_profile.is_offline:
            return "OFFLINE"
        if self.mode == "gpu":
            return "GPU"
        if self.mode == "cpu":
            return "CPU"
        return "CUSTOM"

    @property
    def context_label(self) -> str:
        return f"{self.active_profile.context // 1024}k"


def sanitize_model_name(model: str) -> str:
    """Validate a model name before it is printed or sent to loopback Ollama."""
    cleaned = model.strip()
    if not _SAFE_MODEL_NAME.fullmatch(cleaned):
        raise ValueError(
            "Model names may contain only letters, numbers, dots, colons, slashes, "
            "underscores, and hyphens."
        )
    return cleaned


def download_command(model: str) -> str:
    """Return a command for the user to run themselves; never execute it."""
    return f"ollama pull {sanitize_model_name(model)}"


def discover_startup(
    config: Config,
    catalog: ModelCatalog,
    client: OllamaClient | None = None,
) -> StartupDiscovery:
    """Inspect loopback Ollama and installed models without changing host state."""
    endpoint = config.llm.base_url
    memory = available_memory_gib()
    active_client = client or OllamaClient(endpoint, health_timeout=1.5)
    try:
        models = active_client.list_model_metadata()
    except (OllamaError, OSError):
        return StartupDiscovery(
            status="OLLAMA_NOT_RUNNING",
            endpoint=endpoint,
            memory_gib=memory,
            message=(
                f"Ollama is not running at {endpoint}.\n"
                "Run this command yourself:\n\n  ollama serve"
            ),
        )

    dialogue_models = tuple(model for model in models if is_dialogue_model(model))
    if not dialogue_models:
        return StartupDiscovery(
            status="OLLAMA_NO_MODEL",
            models=models,
            endpoint=endpoint,
            memory_gib=memory,
            message=(
                "Ollama is running, but no local dialogue model was found.\n"
                f"Run this command yourself:\n\n  {download_command(catalog.gpu_profile.model)}"
            ),
        )

    names = {model.name for model in dialogue_models}
    if catalog.gpu_profile.model in names:
        status: StartupStatus = "OLLAMA_READY_GPU"
        message = f"Recommended GPU model found: {catalog.gpu_profile.model}"
    elif catalog.cpu_profile.model in names:
        status = "OLLAMA_READY_CPU"
        message = f"Recommended CPU model found: {catalog.cpu_profile.model}"
    else:
        status = "OLLAMA_READY_CUSTOM"
        message = "Ollama is ready with custom local models."

    return StartupDiscovery(
        status=status,
        models=models,
        endpoint=endpoint,
        memory_gib=memory,
        message=message,
    )


def profile_for_model(config: Config, catalog: ModelCatalog, model: str) -> ModelProfile:
    """Return a recommended profile or a safe in-memory custom profile."""
    cleaned = sanitize_model_name(model)
    for profile in catalog.profiles.values():
        if not profile.is_offline and profile.model == cleaned:
            return profile
    return ModelProfile(
        name="custom",
        provider="ollama",
        model=cleaned,
        display_name=cleaned,
        context=config.llm.num_ctx,
        temperature=config.llm.temperature,
        top_p=config.llm.top_p,
        repeat_penalty=1.08,
        num_predict=320,
        num_gpu=999,
    )


def _profiles_for(
    config: Config,
    catalog: ModelCatalog,
    discovery: StartupDiscovery,
    active: ModelProfile,
) -> tuple[ModelProfile, ...]:
    installed_profiles: list[ModelProfile] = []
    seen: set[str] = set()
    for model in discovery.dialogue_models:
        try:
            profile = profile_for_model(config, catalog, model.name)
        except ValueError:
            continue
        if profile.model not in seen:
            installed_profiles.append(profile)
            seen.add(profile.model)
    ordered = [
        active,
        *(profile for profile in installed_profiles if profile.model != active.model),
    ]
    ordered.append(catalog.offline_profile)
    unique: dict[str, ModelProfile] = {}
    for profile in ordered:
        unique.setdefault(profile.model, profile)
    return tuple(unique.values())


def default_selection(
    config: Config,
    catalog: ModelCatalog,
    discovery: StartupDiscovery,
    requested_mode: RunMode = "auto",
) -> StartupSelection:
    """Choose a mode without prompting or executing host commands."""
    if requested_mode == "offline" or discovery.status == "OFFLINE":
        profile = catalog.offline_profile
        return StartupSelection(
            mode="offline",
            status="OFFLINE",
            active_profile=profile,
            profiles=(profile,),
            source="offline",
            message="Offline mode selected.",
        )

    if requested_mode == "gpu":
        if discovery.status == "OLLAMA_READY_GPU":
            active = catalog.gpu_profile
        else:
            profile = catalog.offline_profile
            return StartupSelection(
                mode="offline",
                status=discovery.status,
                active_profile=profile,
                profiles=(profile,),
                source="gpu-unavailable",
                message=f"GPU model is not installed. {discovery.message}",
            )
    elif requested_mode == "cpu":
        if discovery.status == "OLLAMA_READY_CPU":
            active = catalog.cpu_profile
        else:
            profile = catalog.offline_profile
            return StartupSelection(
                mode="offline",
                status=discovery.status,
                active_profile=profile,
                profiles=(profile,),
                source="cpu-unavailable",
                message=f"CPU model is not installed. {discovery.message}",
            )
    elif discovery.status == "OLLAMA_READY_GPU":
        active = catalog.gpu_profile
    elif discovery.status == "OLLAMA_READY_CPU":
        active = catalog.cpu_profile
    elif discovery.status == "OLLAMA_READY_CUSTOM" and discovery.dialogue_models:
        active = profile_for_model(config, catalog, discovery.dialogue_models[0].name)
    else:
        profile = catalog.offline_profile
        return StartupSelection(
            mode="offline",
            status=discovery.status,
            active_profile=profile,
            profiles=(profile,),
            source="offline",
            message=discovery.message or "Offline mode selected.",
        )

    return StartupSelection(
        mode="gpu"
        if active.model == catalog.gpu_profile.model
        else ("cpu" if active.model == catalog.cpu_profile.model else "auto"),
        status=discovery.status,
        active_profile=active,
        profiles=_profiles_for(config, catalog, discovery, active),
        source="automatic",
        message=discovery.message,
    )


def selection_from_model(
    config: Config,
    catalog: ModelCatalog,
    discovery: StartupDiscovery,
    model: str,
) -> StartupSelection:
    """Select one installed model by exact name."""
    cleaned = sanitize_model_name(model)
    installed = set(discovery.dialogue_model_names)
    if cleaned not in installed:
        raise ValueError(f"Model is not installed: {cleaned}")
    active = profile_for_model(config, catalog, cleaned)
    mode: RunMode = "auto"
    if active.model == catalog.gpu_profile.model:
        mode = "gpu"
    elif active.model == catalog.cpu_profile.model:
        mode = "cpu"
    return StartupSelection(
        mode=mode,
        status=discovery.status,
        active_profile=active,
        profiles=_profiles_for(config, catalog, discovery, active),
        source="custom",
        message=f"Selected installed model: {cleaned}",
    )


def format_discovery(discovery: StartupDiscovery, catalog: ModelCatalog) -> str:
    lines = [
        f"Startup status: {discovery.status}",
        discovery.message or "Local Ollama discovery complete.",
        "",
        f"Endpoint: {discovery.endpoint} (loopback only)",
    ]
    if discovery.memory_gib is not None:
        lines.append(f"Available memory: {discovery.memory_gib:.1f} GiB")
    lines.extend(
        [
            "",
            f"Recommended GPU: {catalog.gpu_profile.model}",
            f"Recommended CPU: {catalog.cpu_profile.model}",
        ]
    )
    return "\n".join(lines)


def format_model_list(discovery: StartupDiscovery) -> str:
    if not discovery.models:
        if discovery.status == "OLLAMA_NOT_RUNNING":
            return (
                "No model list is available because Ollama is not running.\n"
                "Run this command yourself:\n\n  ollama serve"
            )
        return "No local Ollama models were found."
    rows = []
    for model in discovery.models:
        size = f"{model.size_bytes / (1024**3):.2f} GiB" if model.size_bytes else "unknown size"
        modified = model.modified_at or "unknown update time"
        label = "" if is_dialogue_model(model) else " [not selectable: embedding]"
        rows.append(f"- {model.name} ({size}, {modified}){label}")
    return "Installed Ollama models:\n" + "\n".join(rows)


def interactive_selection(
    config: Config,
    catalog: ModelCatalog,
    discovery: StartupDiscovery,
    *,
    read: Callable[[str], str],
    write: Callable[[str], None],
) -> StartupSelection:
    """Run the fixed startup selector using only in-memory choices."""
    write(format_discovery(discovery, catalog))
    write(format_model_list(discovery))
    write(
        "\nStartup selection:\n"
        "1. GPU / Qwen2.5 7B Instruct\n"
        "2. CPU / Qwen2.5 3B Instruct\n"
        "3. Custom model\n"
        "4. Offline mode\n"
        "5. Show download command"
    )

    while True:
        try:
            choice = read("Select [1-5]: ").strip()
        except (EOFError, KeyboardInterrupt):
            return default_selection(config, catalog, discovery, "offline")

        if choice in {"1", "gpu", "GPU"}:
            if discovery.status == "OLLAMA_READY_GPU":
                return default_selection(config, catalog, discovery, "gpu")
            write(
                "The recommended GPU model is not installed.\n"
                f"Run this command yourself:\n\n  {download_command(catalog.gpu_profile.model)}"
            )
        elif choice in {"2", "cpu", "CPU"}:
            if discovery.status == "OLLAMA_READY_CPU":
                return default_selection(config, catalog, discovery, "cpu")
            write(
                "The recommended CPU model is not installed.\n"
                f"Run this command yourself:\n\n  {download_command(catalog.cpu_profile.model)}"
            )
        elif choice in {"3", "custom", "Custom"}:
            write(format_model_list(discovery))
            try:
                requested = read("Installed model name: ").strip()
            except (EOFError, KeyboardInterrupt):
                return default_selection(config, catalog, discovery, "offline")
            try:
                return selection_from_model(config, catalog, discovery, requested)
            except ValueError as exc:
                write(str(exc))
                if requested:
                    with contextlib.suppress(ValueError):
                        write(f"Run this command yourself:\n\n  {download_command(requested)}")
        elif choice in {"4", "offline", "Offline"}:
            selected = default_selection(config, catalog, discovery, "offline")
            write(selected.message)
            return selected
        elif choice in {"5", "download", "Download"}:
            with contextlib.suppress(ValueError):
                write(
                    "Run this command yourself:\n\n"
                    f"  {download_command(catalog.gpu_profile.model)}\n\n"
                    "After it finishes, return to Vormir Sentinel."
                )
        else:
            write("Choose 1, 2, 3, 4, or 5.")


def replace_selection_model(
    selection: StartupSelection,
    model: str,
) -> StartupSelection:
    """Switch to another profile already present in the in-memory selection."""
    cleaned = sanitize_model_name(model)
    for profile in selection.profiles:
        if profile.model == cleaned:
            return replace(
                selection,
                active_profile=profile,
                source="slash-select",
                message=f"Selected installed model: {cleaned}",
            )
    raise ValueError(f"Model is not available in this session: {cleaned}")
