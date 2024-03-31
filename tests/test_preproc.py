import pytest  # noqa

from . import run_pipeline


@pytest.mark.forked
def test_regular(tmp_path):
    run_pipeline("regular", _dir=tmp_path)
    report = tmp_path / "outdir" / "REPORTS" / "pages" / "_index.js"
    assert report.exists()


@pytest.mark.forked
def test_markdown(tmp_path):
    run_pipeline("markdown_", _dir=tmp_path)
    report = tmp_path.joinpath(
        "workdir",
        "Markdown-process",
        ".report-workdir",
        "src",
        "pages",
        "Process2",
        "proc.svelte",
    )
    assert "<h1>Process</h1>" in report.read_text()


@pytest.mark.forked
def test_extlibs(tmp_path):
    run_pipeline("extlibs", _dir=tmp_path)
    report = tmp_path / "outdir" / "REPORTS" / "pages" / "Index.js"
    assert "Hello world" in report.read_text()
