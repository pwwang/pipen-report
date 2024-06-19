import sys
from pathlib import Path
from pipen import Proc, Pipen


class Process(Proc):
    """Example process"""
    input = "img:file"
    output = "out:file:{{ in.img | filename }}.png"
    script = """
        cp {{ in.img }} {{ out.out }}
    """
    template_opts = {
        "filters": {"filename": lambda x: Path(x).stem}
    }
    plugin_opts = {
        "report": """
            <h1>Process</h1>
            <h2>Image</h2>
            <img src="{{job.out.out}}" />
            <img src="" />
            <img src="%s" />
        """ % (Path(__file__).parent.parent / "data" / "x.png")
    }


class ReportNoH1(Proc):
    """Report with no H1"""
    input = "a:var"
    output = "c:var:{{ in.a }}"
    plugin_opts = {
        "report": """{{job.out.c}}"""
    }


def pipeline(**config):
    """Example pipeline"""
    class Process2(Process):
        ...

    class ReportNoH1_1(ReportNoH1):
        ...

    return (
        Pipen("Single-process", **config)
        .set_start(Process2, ReportNoH1_1)
        .set_data([Path(__file__).parent.parent / "data" / "x.png"], [1])
    )


if __name__ == "__main__":
    if len(sys.argv) > 1:
        pipeline(
            plugins=["-args"],
            workdir=sys.argv[1],
            outdir=sys.argv[2],
        ).run()
    else:
        pipeline().run()
