import pytest  # noqa

import cmdy
from pathlib import Path

from . import run_pipeline


def test_inject_default(tmp_path):

    run_pipeline("single", _dir=tmp_path)

    to_inject = Path(__file__).parent / "data" / "to_inject.html"
    cmd = cmdy.pipen.report(
        "inject",
        reportdir=tmp_path / "outdir" / "REPORTS",
        _=to_inject,
    ).hold()
    print("")
    print("Running:")
    print(cmd.strcmd)
    out = cmd.run().wait()
    assert out.rc == 0
    assert (
        "Injected"
        in tmp_path.joinpath(
            "outdir", "REPORTS", "build", "index.js"
        ).read_text()
    )


def test_inject_with_given_title(tmp_path):

    run_pipeline("single", _dir=tmp_path)

    to_inject = Path(__file__).parent / "data" / "to_inject.html"
    cmd = cmdy.pipen.report(
        "inject",
        title="MyTitle",
        reportdir=tmp_path / "outdir" / "REPORTS",
        _=to_inject,
    ).hold()
    print("")
    print("Running:")
    print(cmd.strcmd)
    out = cmd.run().wait()
    assert out.rc == 0
    assert (
        "MyTitle"
        in tmp_path.joinpath(
            "outdir", "REPORTS", "build", "index.js"
        ).read_text()
    )



def test_inject_with_no_title_in_page(tmp_path):

    run_pipeline("single", _dir=tmp_path)

    to_inject = Path(__file__).parent / "data" / "to_inject_no_title.html"
    cmd = cmdy.pipen.report(
        "inject",
        reportdir=tmp_path / "outdir" / "REPORTS",
        _=to_inject,
    ).hold()
    print("")
    print("Running:")
    print(cmd.strcmd)
    out = cmd.run().wait()
    assert out.rc == 0
    assert (
        "to_inject_no_title"
        in tmp_path.joinpath(
            "outdir", "REPORTS", "build", "index.js"
        ).read_text()
    )


def test_inject_with_existing_name(tmp_path):

    run_pipeline("single", _dir=tmp_path)

    to_inject = Path(__file__).parent / "data" / "index.html"
    cmd = cmdy.pipen.report(
        "inject",
        reportdir=tmp_path / "outdir" / "REPORTS",
        _=to_inject,
    ).hold()
    print("")
    print("Running:")
    print(cmd.strcmd)
    out = cmd.run().wait()
    assert out.rc == 0
    assert (
        "index_1"
        in tmp_path.joinpath(
            "outdir", "REPORTS", "build", "index.js"
        ).read_text()
    )
