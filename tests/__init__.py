import sys
from pathlib import Path
from subprocess import run


def run_pipeline(pipeline, _dir=None):
    """Run a pipeline in a subprocess."""
    pipeline_file = Path(__file__).parent / "pipelines" / f"{pipeline}.py"
    pipeline_file = pipeline_file.resolve()
    cmd = [sys.executable, str(pipeline_file)]
    if _dir:
        workdir = Path(_dir) / "workdir"
        outdir = Path(_dir) / "outdir"
        cmd += [str(workdir), str(outdir)]

    run(cmd)
