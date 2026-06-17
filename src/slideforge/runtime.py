"""Mutable runtime configuration for SlideForge."""

from . import settings


def reset_runtime_config() -> None:
    globals().update(settings.DEFAULT_CONFIG)
    globals()["SUBTITLE_MAX_CHARS"] = SUBTITLE_LINE_CHARS * SUBTITLE_MAX_LINES


def apply_config(overrides: dict[str, object]) -> None:
    for key, value in overrides.items():
        if value is None:
            continue
        normalized_key = str(key).replace("-", "_").lower()
        config_name = settings.CONFIG_ALIASES.get(normalized_key)
        if not config_name:
            continue
        globals()[config_name] = settings.coerce_config_value(config_name, value)

    globals()["SUBTITLE_MAX_CHARS"] = SUBTITLE_LINE_CHARS * SUBTITLE_MAX_LINES


reset_runtime_config()
