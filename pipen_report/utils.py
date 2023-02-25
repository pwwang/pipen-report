from typing import Any

from . import defaults


def get_config(key: str) -> Any:
    """Get the configuration"""
    default = getattr(defaults, key.upper())
    return defaults.CONFIG.get(key, default)
