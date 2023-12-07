from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pipen.utils import get_logger
from pipen import Proc
from . import defaults

if TYPE_CHECKING:
    from logging import Logger


logger = get_logger("report")


def get_config(key: str, runtime_value: Any = None) -> Any:
    """Get the configuration"""
    if runtime_value is not None:
        return runtime_value

    default = getattr(defaults, key.upper())
    return defaults.CONFIG.get(key, default)


class UnifiedLogger:  # pragma: no cover

    def __init__(self, logger: Logger, proc: Proc | str):
        self.logger = logger
        self.proc = None if not isinstance(proc, Proc) else proc

    def log(self, level: str, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a message"""
        if self.proc is None:
            getattr(self.logger, level)(msg, *args, **kwargs)

        else:
            self.proc.log(level, msg, *args, **kwargs, logger=self.logger)

    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self.log("debug", msg, *args, **kwargs)

    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self.log("info", msg, *args, **kwargs)

    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self.log("warning", msg, *args, **kwargs)

    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self.log("error", msg, *args, **kwargs)

    def critical(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self.log("critical", msg, *args, **kwargs)
