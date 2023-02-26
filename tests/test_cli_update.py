import pytest  # noqa

import cmdy


@pytest.mark.forked
def test_update():

    out = cmdy.pipen.report("update")
    stdout = out.stdout
    assert out.rc == 0
    assert "The frontend directory:" in stdout
    assert "Running: npm update ..." in stdout
