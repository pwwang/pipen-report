
import sys
from pipen import Proc, Pipen


class Process(Proc):
    """Example process"""
    input = "a:var, b:var"
    output = "c:var:{{ in.a + in.b }}"
    plugin_opts = {
        "report": "file://paging.tpl",
        "report_paging": 1,
    }


def pipeline(**config):
    """Example pipeline"""
    class Process2(Process):
        ...

    return (
        Pipen("Report_paging", **config)
        .set_start(Process2)
        .set_data([(1, 2)])
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
