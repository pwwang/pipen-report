import pytest  # noqa

from . import run_pipeline


@pytest.mark.forked
def test_regular(tmp_path):
    run_pipeline("single", _dir=tmp_path)

    report_workdir = tmp_path / "workdir" / "Single-process" / ".report-workdir"
    assert report_workdir.exists()
    assert report_workdir.joinpath("public").is_symlink()

    # reports generated
    assert tmp_path.joinpath("outdir", "REPORTS", "index.html").exists()
    # run it again to clear files in public/data
    run_pipeline("single", _dir=tmp_path)


@pytest.mark.forked
def test_noreport(tmp_path):
    run_pipeline("noreport", _dir=tmp_path)

    report = tmp_path / "outdir" / "REPORTS" / "procs" / "process2" / "index.js"
    assert not report.exists()


@pytest.mark.forked
def test_noreport2(tmp_path):
    run_pipeline("noreport2", _dir=tmp_path)

    report = tmp_path / "outdir" / "REPORTS" / "procs" / "process2" / "index.js"
    assert not report.exists()
    report = tmp_path / "outdir" / "REPORTS" / "procs" / "process3" / "index.js"
    assert report.exists()


@pytest.mark.forked
def test_errant(tmp_path):
    run_pipeline("errant", _dir=tmp_path)

    report = tmp_path / "outdir" / "REPORTS" / "procs"
    assert not report.exists()
