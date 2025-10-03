import pytest  # noqa

import sys
import subprocess as sp


@pytest.mark.forked
def test_update():

    out = sp.Popen(["pipen", "report", "update"], stdout=sp.PIPE)
    assert out.wait() == 0
    stdout = out.stdout.read().decode()
    assert "The frontend directory:" in stdout
    assert "Running: npm update ..." in stdout


@pytest.mark.forked
def test_update_first_time(tmp_path):
    nmdir = tmp_path / "nmdir"
    nmdir.mkdir()
    out = sp.Popen(
        [
            sys.executable, "-m",
            "pipen", "report", "config", "--local", "--nmdir", str(nmdir)
        ],
        cwd=str(tmp_path),
        stdout=sp.PIPE,
    )
    assert out.wait() == 0

    out = sp.Popen(
        [sys.executable, "-m", "pipen", "report", "update"],
        cwd=str(tmp_path),
        stdout=sp.PIPE,
    )
    assert out.wait() == 0
    stdout = out.stdout.read().decode()
    assert "The frontend directory:" in stdout
    assert "Running: npm install ... (first time setup)" in stdout


@pytest.mark.forked
def test_config(tmp_path):

    out = sp.Popen(
        [sys.executable, "-m", "pipen", "report", "config", "--list"],
        stdout=sp.PIPE,
    )
    assert out.wait() == 0
    stdout = out.stdout.read().decode()
    assert "Note that these values can still be overwritten by" in stdout

    out = sp.Popen(
        [sys.executable, "-m", "pipen", "report", "config", "--local", "--npm", "npm2"],
        cwd=str(tmp_path),
    )
    assert out.wait() == 0
    conffile = tmp_path / ".pipen-report.toml"
    assert conffile.exists()
    assert 'npm = "npm2"' in conffile.read_text()
