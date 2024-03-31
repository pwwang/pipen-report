import pytest  # noqa
from . import run_pipeline


@pytest.mark.forked
def test_run_2_times(tmp_path):
    """Test that the pipeline can be run twice."""
    run_pipeline("regular", _dir=tmp_path)
    run_pipeline("regular", _dir=tmp_path)


@pytest.mark.forked
def test_report_paging(tmp_path):
    """Test that the report tpl is loaded from a file."""
    run_pipeline("paging", _dir=tmp_path)
    report0 = tmp_path.joinpath(
        "outdir",
        "REPORTS",
        "pages",
        "Process2.js",
    )
    report1 = tmp_path.joinpath(
        "outdir",
        "REPORTS",
        "pages",
        "Process2-1.js",
    )
    report2 = tmp_path.joinpath(
        "outdir",
        "REPORTS",
        "pages",
        "Process2-2.js",
    )
    assert report0.exists()
    assert report1.exists()
    assert report2.exists()
    # run the pipeline again to trigger cleaning of the previous files
    run_pipeline("paging", _dir=tmp_path)


@pytest.mark.forked
def test_force_export(tmp_path):
    """Test process forced export"""
    run_pipeline("force_export", _dir=tmp_path)
    report = tmp_path / "outdir" / "Process21"
    assert report.exists()
    report = tmp_path / "outdir" / "Process22"
    assert not report.exists()


def test_large(tmp_path):
    """Test process forced export"""
    run_pipeline("large", _dir=tmp_path)
    report = tmp_path / "outdir" / "REPORTS" / "pages" / "Process2.js"
    assert report.exists()
