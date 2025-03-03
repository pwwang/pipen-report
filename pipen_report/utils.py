from __future__ import annotations

import json
from os import path
from hashlib import md5
from functools import wraps
from tempfile import gettempdir
from typing import TYPE_CHECKING, Any, Callable

from cloudpathlib.exceptions import OverwriteNewerCloudError
from pipen.utils import get_logger
from pipen import Proc
from . import defaults

if TYPE_CHECKING:
    from pathlib import Path
    from logging import Logger


logger = get_logger("report")


def get_config(key: str, runtime_value: Any = None) -> Any:
    """Get the configuration"""
    if runtime_value is not None:
        return runtime_value

    default = getattr(defaults, key.upper())
    return defaults.CONFIG.get(key, default)


def _stringify(obj: Any) -> str:
    """Stringify an object"""
    if isinstance(obj, list):
        return "[" + ", ".join(map(_stringify, obj)) + "]"
    if isinstance(obj, tuple):
        return "(" + ", ".join(map(_stringify, obj)) + ")"
    if isinstance(obj, dict):
        return "{" + ", ".join(f"{k}: {_stringify(obj[k])}" for k in sorted(obj)) + "}"
    if callable(obj):
        return f"<callable {obj.__name__}>"
    if isinstance(obj, Proc):
        return repr(obj.__class__)
    return repr(obj)


def cache_fun(func: Callable) -> Callable:
    """Decorator to cache the result of a function to disk"""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        str_args = _stringify(args)
        str_kwargs = _stringify(kwargs)
        sig = md5(f"{str_args}\n{str_kwargs}".encode("utf-8")).hexdigest()
        sigfile = path.join(
            gettempdir(),
            f"pipen-report.{func.__name__}.{sig}.json",
        )

        if not path.exists(sigfile):
            result = func(*args, **kwargs)
            with open(sigfile, "w") as fout:
                json.dump(result, fout)
        else:
            with open(sigfile, "r") as fin:
                result = json.load(fin)

        return result

    return wrapper


def rsync_to_cloud(path: Path) -> None:
    # path must have a spec attribute and it must be a cloud path
    if path.is_file():
        try:
            path.spec._upload_local_to_cloud(force_overwrite_to_cloud=False)
        except OverwriteNewerCloudError:
            path.spec._upload_local_to_cloud(force_overwrite_to_cloud=True)
    else:  # is_dir()
        path.spec.mkdir(parents=True, exist_ok=True)
        for subpath in path.iterdir():
            setattr(subpath, "spec", path.spec / subpath.name)
            rsync_to_cloud(subpath)


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
