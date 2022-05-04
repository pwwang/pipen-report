import pytest  # noqa

from . import run_pipeline


def test_regular(tmp_path):
    run_pipeline("single", _dir=tmp_path)

    report_workdir = tmp_path / "workdir" / "single-process" / ".report-workdir"
    assert report_workdir.exists()
    assert report_workdir.joinpath("public").is_symlink()

    # reports generated
    assert tmp_path.joinpath("outdir", "REPORTS", "index.html").exists()
    # run it again to clear files in public/data
    run_pipeline("single", _dir=tmp_path)


def test_noreport(tmp_path):
    run_pipeline("noreport", _dir=tmp_path)

    report = tmp_path / "outdir" / "REPORTS" / "build" / "process2.js"
    assert not report.exists()


def test_noreport2(tmp_path):
    run_pipeline("noreport2", _dir=tmp_path)

    report = tmp_path / "outdir" / "REPORTS" / "build" / "process2.js"
    assert not report.exists()
    report = tmp_path / "outdir" / "REPORTS" / "build" / "process3.js"
    assert report.exists()


def test_errant(tmp_path):
    run_pipeline("errant", _dir=tmp_path)

    report = tmp_path / "outdir" / "REPORTS" / "index.html"
    assert not report.exists()


