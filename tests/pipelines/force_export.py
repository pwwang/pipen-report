
import sys
from pipen import Proc, Pipen


class Process(Proc):
    """Example process"""
    input = "a:var, b:var"
    output = "c:var:{{ in.a }}"


def pipeline(**config):
    """Example pipeline"""
    class Process21(Process):
        # This process is not exported,
        # But will be forced to export, since report is set
        plugin_opts = {"report": "<h1>Process2</h1>"}

    class Process22(Process):
        # This process is not exported,
        # But will not be forced to export, since report_force_export is False
        plugin_opts = {
            "report": "<h1>Process2</h1>",
            "report_force_export": False,
        }

    class Process3(Process):
        requires = Process21, Process22
        export = False
        plugin_opts = {"report": "<h1>Process3</h1>"}

    return (
        Pipen("Force-report", **config)
        .set_start(Process21, Process22)
        .set_data([1], [1])
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
