
import sys
from pipen import Proc, Pipen


class Process(Proc):
    """Example process"""
    input = "a:var"
    output = "c:var:{{ in.a }}"
    plugin_opts = {
        "report": """<h1>Process</h1>"""
    }


def pipeline(**config):
    """Example pipeline"""
    class Process2(Process):
        script = "exit 1"

    return (
        Pipen("Errant", **config)
        .set_start(Process2)
        .set_data([1])
    )


if __name__ == "__main__":
    if len(sys.argv) > 1:
        pipeline(
            plugins=["no:args"],
            workdir=sys.argv[1],
            outdir=sys.argv[2],
        ).run()
    else:
        pipeline().run()

