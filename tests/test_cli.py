import pytest  # noqa

import cmdy


@pytest.mark.forked
def test_update():

    out = cmdy.pipen.report("update")
    stdout = out.stdout
    assert out.rc == 0
    assert "The frontend directory:" in stdout
    assert "Running: npm update ..." in stdout


@pytest.mark.forked
def test_config(tmp_path):

    out = cmdy.pipen.report("config", "--list")
    stdout = out.stdout
    assert out.rc == 0
    assert "Note that these values can still be overwritten by" in stdout

    out = cmdy.pipen.report("config", "--local", "--npm", "npm2", _cwd=tmp_path)
    conffile = tmp_path / ".pipen-report.toml"
    assert conffile.exists()
    assert 'npm = "npm2"' in conffile.read_text()
