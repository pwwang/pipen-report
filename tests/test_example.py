import sys
from pathlib import Path
from subprocess import run

EXAMPLE_DIR = Path(__file__).parent.parent / "example"


def test_example():
    cmd = [sys.executable, str(EXAMPLE_DIR / "pipeline.py")]
    run(cmd)
