
import sys
from pipen import Proc, Pipen


class Process(Proc):
    """Example process with Markdown tag in report"""
    input = "a:var, b:var"
    output = "c:var:{{ in.a + in.b }}"
    plugin_opts = {
        "report": """<Markdown># Process</Markdown>"""
    }


def pipeline(**config):
    """Example pipeline"""
    class Process2(Process):
        ...

    return (
        Pipen("Markdown-process", **config)
        .set_start(Process2)
        .set_data([(1, 2)])
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
