import pytest  # noqa

import cmdy


def test_update():

    out = cmdy.pipen.report("update")
    stdout = out.stdout
    assert out.rc == 0
    assert "WORKING DIRECTORY" in stdout
    assert "Running" in stdout
