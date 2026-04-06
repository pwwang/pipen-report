"""
Patch copier for fail-safe chmod on destination files.

This is because `chmod` is not allowed for gcsfuse-mounted files.

See: https://github.com/copier-org/copier/issues/2298

The issue is solved by copier v9.11.0, however, python 3.9 supported was dropped
in that version, so we need to patch for copier before v9.11.0 to support python 3.9.
and we also need to patch to suppress the warnings for copier v9.10+.
"""
from __future__ import annotations

import warnings

from contextlib import suppress
from copier._main import Worker

_orig_render_file = Worker._render_file


def _patched_render_file(self, *args, **kwargs):
    with suppress(PermissionError), warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            category=UserWarning,
            message=".*Path permissions.*"
        )
        return _orig_render_file(self, *args, **kwargs)


Worker._render_file = _patched_render_file
