from __future__ import annotations

import json
import os
import re
import struct
from hashlib import md5
from functools import wraps
from pathlib import Path
from tempfile import gettempdir
from typing import TYPE_CHECKING, Any, Callable, Pattern

from panpath import PanPath
from pipen.utils import get_logger
from pipen import Proc  # type: ignore[import]
from . import defaults

if TYPE_CHECKING:
    from logging import Logger


logger = get_logger("report")


async def a_re_sub(  # pragma: no cover
    pattern: str | Pattern,
    repl: Callable,
    string: str,
    count: int = 0,
    flags: int = 0,
) -> str:
    """Async version of re.sub() that accepts an async replacement function.

    Args:
        pattern: The regex pattern to search for
        repl: An async function that takes a Match object and returns a
            replacement string
        string: The string to search in
        count: Maximum number of pattern occurrences to be replaced (0 = all)
        flags: Regex flags

    Returns:
        The string with replacements applied
    """
    if isinstance(pattern, str):
        pattern = re.compile(pattern, flags)

    matches = list(pattern.finditer(string))

    if count > 0:
        matches = matches[:count]

    if not matches:
        return string

    # Process matches in reverse order to maintain correct positions
    result = string
    for match in reversed(matches):
        replacement = await repl(match)
        result = result[:match.start()] + replacement + result[match.end():]

    return result


async def a_copy_all(src: PanPath, dst: PanPath, cachedir: str | None = None) -> None:
    """Asynchronously copy all contents from src to dst PanPath."""
    if not await src.a_exists():
        # In case it is a local path that doesn't exist, try to get from cloud
        # if it is cached path
        cloudpath = get_cloudpath(src, cachedir) if cachedir else None
        if not cloudpath:
            raise FileNotFoundError(f"Source path not found: {src}")
        src = cloudpath

    await dst.parent.a_mkdir(parents=True, exist_ok=True)
    if await src.a_is_dir():
        await src.a_copytree(dst)
    else:
        await src.a_copy(dst)


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


def get_fspath(path: PanPath, cachedir: str) -> str:
    """Get the fspath of a PanPath, using cachedir if necessary"""
    cloud_fspath = PanPath(cachedir)
    parts = [
        cloud_fspath,
        path.parts[0].replace(":", ""),
        *path.parts[1:],
    ]
    return os.path.join(*parts)


def get_cloudpath(path: str | PanPath, cachedir: str | PanPath) -> PanPath | None:
    """Get the cloud path of a PanPath, using cachedir if necessary"""
    path_str = str(path)
    cachedir_str = str(cachedir)

    if not path_str.startswith(cachedir_str):
        return None

    path = PanPath(path)
    cachedir = PanPath(cachedir)
    cloudpath = path_str[len(cachedir_str) :].lstrip("/").replace("/", "://", 1)
    return PanPath(cloudpath)


def cache_fun(func: Callable) -> Callable:
    """Decorator to cache the result of an async function to disk"""

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        str_args = _stringify(args)
        str_kwargs = _stringify(kwargs)
        str_preprocess = _stringify(
            Path(__file__).parent.joinpath("preprocess.py").read_text()
        )
        str_utils = _stringify(Path(__file__).read_text())
        sig = md5(
            f"{str_args}\n{str_kwargs}\n{str_preprocess}\n{str_utils}".encode("utf-8")
        ).hexdigest()
        sigfile = os.path.join(
            gettempdir(),
            f"pipen-report.{func.__name__}.{sig}.json",
        )

        if not os.path.exists(sigfile):
            result = await func(*args, **kwargs)
            with open(sigfile, "w") as fout:
                json.dump(result, fout)
        else:
            with open(sigfile, "r") as fin:
                result = json.load(fin)

        return result

    return wrapper


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


def _convertToPx(value):  # pragma: no cover
    matched = re.match(r"(\d+(?:\.\d+)?)?([a-z]*)$", value)
    if not matched:
        raise ValueError("unknown length value: %s" % value)

    length, unit = matched.groups()
    if unit == "":
        return float(length)
    elif unit == "cm":
        return float(length) * 96 / 2.54
    elif unit == "mm":
        return float(length) * 96 / 2.54 / 10
    elif unit == "in":
        return float(length) * 96
    elif unit == "pc":
        return float(length) * 96 / 6
    elif unit == "pt":
        return float(length) * 96 / 6
    elif unit == "px":
        return float(length)

    raise ValueError("unknown unit type: %s" % unit)


async def get_imagesize(  # pragma: no cover
    filepath: str | PanPath,
    cachedir: str | PanPath,
) -> tuple[int, int]:
    """
    Return (width, height) for a given img file content

    Code borrowed and adapted from imagesize package
    (https://github.com/shibukawa/imagesize_py/blob/master/imagesize/imagesize.py)

    Note that for cloud files, for the image types that seeking is required to
    determine the dimensions, this function may not work properly.

    Args:
        filepath: a local or cloud file path
        cachedir: if filepath is a path from cachedir and it doesn't exist locally,
            we try to get it from the cloud

    Returns:
        Tuple[int, int]: width and height of the image
    """
    height = -1
    width = -1

    filepath = PanPath(filepath)
    if not await filepath.a_exists():
        cloudpath = get_cloudpath(filepath, cachedir)
        if not cloudpath:
            raise FileNotFoundError(f"File not found: {filepath}")

        filepath = cloudpath

    async with filepath.a_open("rb") as fhandle:
        head = await fhandle.read(31)
        size = len(head)
        # handle GIFs
        if size >= 10 and head[:6] in (b"GIF87a", b"GIF89a"):
            # Check to see if content_type is correct
            try:
                width, height = struct.unpack("<hh", head[6:10])
            except struct.error:
                raise ValueError("Invalid GIF file")
        # see png edition spec bytes are below chunk length then and finally the
        elif (
            size >= 24
            and head.startswith(b"\211PNG\r\n\032\n")
            and head[12:16] == b"IHDR"
        ):
            try:
                width, height = struct.unpack(">LL", head[16:24])
            except struct.error:
                raise ValueError("Invalid PNG file")
        # Maybe this is for an older PNG version.
        elif size >= 16 and head.startswith(b"\211PNG\r\n\032\n"):
            # Check to see if we have the right content type
            try:
                width, height = struct.unpack(">LL", head[8:16])
            except struct.error:
                raise ValueError("Invalid PNG file")
        # handle JPEGs
        elif size >= 2 and head.startswith(b"\377\330"):
            try:
                # cloud file handle doesn't support backward seek
                await fhandle.seek(0)  # Read 0xff next
                size = 2
                ftype = 0
                while not 0xC0 <= ftype <= 0xCF or ftype in [0xC4, 0xC8, 0xCC]:
                    await fhandle.seek(size, 1)
                    byte = await fhandle.read(1)
                    while ord(byte) == 0xFF:
                        byte = await fhandle.read(1)
                    ftype = ord(byte)
                    size = struct.unpack(">H", await fhandle.read(2))[0] - 2
                # We are at a SOFn block
                await fhandle.seek(1, 1)  # Skip `precision' byte.
                height, width = struct.unpack(">HH", await fhandle.read(4))
            except (struct.error, TypeError):
                raise ValueError("Invalid JPEG file")
        # handle JPEG2000s
        elif size >= 12 and head.startswith(b"\x00\x00\x00\x0cjP  \r\n\x87\n"):
            await fhandle.seek(48)
            try:
                height, width = struct.unpack(">LL", await fhandle.read(8))
            except struct.error:
                raise ValueError("Invalid JPEG2000 file")
        # handle big endian TIFF
        elif size >= 8 and head.startswith(b"\x4d\x4d\x00\x2a"):
            offset = struct.unpack(">L", head[4:8])[0]
            await fhandle.seek(offset)
            ifdsize = struct.unpack(">H", await fhandle.read(2))[0]
            for i in range(ifdsize):
                tag, datatype, count, data = struct.unpack(
                    ">HHLL", await fhandle.read(12)
                )
                if tag == 256:
                    if datatype == 3:
                        width = int(data / 65536)
                    elif datatype == 4:
                        width = data
                    else:
                        raise ValueError(
                            "Invalid TIFF file: width column data type "
                            "should be SHORT/LONG."
                        )
                elif tag == 257:
                    if datatype == 3:
                        height = int(data / 65536)
                    elif datatype == 4:
                        height = data
                    else:
                        raise ValueError(
                            "Invalid TIFF file: height column data type "
                            "should be SHORT/LONG."
                        )
                if width != -1 and height != -1:
                    break
            if width == -1 or height == -1:
                raise ValueError(
                    "Invalid TIFF file: width and/or height IDS entries are missing."
                )
        elif size >= 8 and head.startswith(b"\x49\x49\x2a\x00"):
            offset = struct.unpack("<L", head[4:8])[0]
            await fhandle.seek(offset)
            ifdsize = struct.unpack("<H", await fhandle.read(2))[0]
            for i in range(ifdsize):
                tag, datatype, count, data = struct.unpack(
                    "<HHLL", await fhandle.read(12)
                )
                if tag == 256:
                    width = data
                elif tag == 257:
                    height = data
                if width != -1 and height != -1:
                    break
            if width == -1 or height == -1:
                raise ValueError(
                    "Invalid TIFF file: width and/or height IDS entries are missing."
                )
        # handle little endian BigTiff
        elif size >= 8 and head.startswith(b"\x49\x49\x2b\x00"):
            bytesize_offset = struct.unpack("<L", head[4:8])[0]
            if bytesize_offset != 8:
                raise ValueError(
                    "Invalid BigTIFF file: Expected offset to be 8, "
                    f"found {offset} instead."
                )
            offset = struct.unpack("<Q", head[8:16])[0]
            await fhandle.seek(offset)
            ifdsize = struct.unpack("<Q", await fhandle.read(8))[0]
            for i in range(ifdsize):
                tag, datatype, count, data = struct.unpack(
                    "<HHQQ", await fhandle.read(20)
                )
                if tag == 256:
                    width = data
                elif tag == 257:
                    height = data
                if width != -1 and height != -1:
                    break
            if width == -1 or height == -1:
                raise ValueError(
                    "Invalid BigTIFF file: width and/or height IDS entries are missing."
                )

        # handle SVGs
        elif size >= 5 and (head.startswith(b"<?xml") or head.startswith(b"<svg")):
            await fhandle.seek(0)
            data = await fhandle.read(1024)
            try:
                data = data.decode("utf-8")
                width = re.search(r'[^-]width="(.*?)"', data).group(1)
                height = re.search(r'[^-]height="(.*?)"', data).group(1)
            except Exception:
                raise ValueError("Invalid SVG file")
            width = _convertToPx(width)
            height = _convertToPx(height)

        # handle Netpbm
        elif head[:1] == b"P" and head[1:2] in b"123456":
            await fhandle.seek(2)
            sizes = []

            while True:
                next_chr = await fhandle.read(1)

                if next_chr.isspace():
                    continue

                if next_chr == b"":
                    raise ValueError("Invalid Netpbm file")

                if next_chr == b"#":
                    await fhandle.readline()
                    continue

                if not next_chr.isdigit():
                    raise ValueError("Invalid character found on Netpbm file")

                size = next_chr
                next_chr = await fhandle.read(1)

                while next_chr.isdigit():
                    size += next_chr
                    next_chr = await fhandle.read(1)

                sizes.append(int(size))

                if len(sizes) == 2:
                    break

                await fhandle.seek(-1, os.SEEK_CUR)
            width, height = sizes
        elif head.startswith(b"RIFF") and head[8:12] == b"WEBP":
            if head[12:16] == b"VP8 ":
                width, height = struct.unpack("<HH", head[26:30])
            elif head[12:16] == b"VP8X":
                width = struct.unpack("<I", head[24:27] + b"\0")[0]
                height = struct.unpack("<I", head[27:30] + b"\0")[0]
            elif head[12:16] == b"VP8L":
                b = head[21:25]
                width = (((b[1] & 63) << 8) | b[0]) + 1
                height = (((b[3] & 15) << 10) | (b[2] << 2) | ((b[1] & 192) >> 6)) + 1
            else:
                raise ValueError("Unsupported WebP file")

    return width, height
