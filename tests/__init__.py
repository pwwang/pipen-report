import importlib
from pathlib import Path


def run_pipeline(
    pipeline, _dir=None, **kwargs
):

    mod = importlib.import_module(f".pipelines.{pipeline}", package="tests")
    if _dir:
        kwargs["workdir"] = Path(_dir) / "workdir"
        kwargs["outdir"] = Path(_dir) / "outdir"

    mod.pipeline(**kwargs).run()
