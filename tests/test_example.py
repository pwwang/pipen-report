import sys
import pytest
from pathlib import Path
from subprocess import run

EXAMPLE_DIR = Path(__file__).parent.parent / "example"


@pytest.mark.forked
def test_example():
    cmd = [sys.executable, str(EXAMPLE_DIR / "pipeline.py")]
    run(cmd)
