import pytest  # noqa

from . import run_pipeline


def test_regular(tmp_path):
    run_pipeline("regular", _dir=tmp_path)
    report = tmp_path / "outdir" / "REPORTS" / "build" / "index.js"
    assert report.exists()


def test_markdown(tmp_path):
    run_pipeline("markdown", _dir=tmp_path)
    report = (
        tmp_path
        / "workdir"
        / "markdown-process"
        / ".report-workdir"
        / "src"
        / "procs"
        / "process2.svelte"
    )
    assert "<h1>Process</h1>" in report.read_text()
