from typing import Any

from . import defaults


def get_config(key: str, runtime_value: Any = None) -> Any:
    """Get the configuration"""
    if runtime_value is not None:
        return runtime_value

    default = getattr(defaults, key.upper())
    return defaults.CONFIG.get(key, default)
