
import sys
from pipen import Proc, Pipen


class Process(Proc):
    """Example process"""
    input = "a:var"
    output = "c:var:{{ in.a }}"


def pipeline(**config):
    """Example pipeline"""
    class Process2(Process):
        ...

    return (
        Pipen("Noreport", **config)
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
