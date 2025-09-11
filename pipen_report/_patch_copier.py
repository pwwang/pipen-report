"""
Patch copier for fail-safe chmod on destination files.

This is because `chmod` is not allowed for gcsfuse-mounted files.

See: https://github.com/copier-org/copier/issues/2298
"""
from __future__ import annotations

import warnings
from typing import TYPE_CHECKING

from contextlib import suppress

# suppress DeprecationWarning for copier v9.10+
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    from copier import Worker  # v9.9.1
from copier.errors import YieldTagInFileError

if TYPE_CHECKING:
    from pathlib import Path
    from copier._types import AnyByStrDict


def _patched_render_file(
    self,
    src_relpath: Path,
    dst_relpath: Path,
    extra_context: AnyByStrDict | None = None,
) -> None:
    """Render one file.

    Args:
        src_relpath:
            File to be rendered. It must be a path relative to the template
            root.
        dst_relpath:
            File to be created. It must be a path relative to the subproject
            root.
        extra_context:
            Additional variables to use for rendering the template.
    """
    # TODO Get from main.render_file()
    assert not src_relpath.is_absolute()
    assert not dst_relpath.is_absolute()
    src_abspath = self.template.local_abspath / src_relpath
    if src_relpath.name.endswith(self.template.templates_suffix):
        try:
            tpl = self.jinja_env.get_template(src_relpath.as_posix())
        except UnicodeDecodeError:
            if self.template.templates_suffix:
                # suffix is not empty, re-raise
                raise
            # suffix is empty, fallback to copy
            new_content = src_abspath.read_bytes()
        else:
            new_content = tpl.render(
                **self._render_context(), **(extra_context or {})
            ).encode()
            if self.jinja_env.yield_name:
                raise YieldTagInFileError(
                    f"File {src_relpath} contains a yield tag, but it is not allowed."
                )
    else:
        new_content = src_abspath.read_bytes()
    dst_abspath = self.subproject.local_abspath / dst_relpath
    src_mode = src_abspath.stat().st_mode
    if not self._render_allowed(dst_relpath, expected_contents=new_content):
        return
    if not self.pretend:
        dst_abspath.parent.mkdir(parents=True, exist_ok=True)
        if dst_abspath.is_symlink():
            # Writing to a symlink just writes to its target, so if we want to
            # replace a symlink with a file we have to unlink it first
            dst_abspath.unlink()
        dst_abspath.write_bytes(new_content)
        with suppress(PermissionError):
            # <-- ADDED: fail-safe chmod
            # In some filesystems (e.g. gcsfuse), chmod is not allowed
            # So we suppress the PermissionError here
            dst_abspath.chmod(src_mode)


Worker._render_file = _patched_render_file
