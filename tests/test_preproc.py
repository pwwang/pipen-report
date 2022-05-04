import pytest  # noqa

from . import run_pipeline


def test_regular(tmp_path):
    run_pipeline("regular", _dir=tmp_path)
    report = tmp_path / "outdir" / "REPORTS" / "build" / "index.js"
    assert report.exists()
