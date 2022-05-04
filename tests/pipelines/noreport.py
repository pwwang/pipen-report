
from pipen import Proc, Pipen


class Process(Proc):
    """Example process"""
    input = "a:var"
    output = "c:var:{{ in.a }}"


def pipeline(**config):
    """Example pipeline"""
    class Process2(Process):
        ...

    class Process3(Process):
        requires = Process2
        export = False
        # even when report is True
        plugin_opts = {"report": True}

    return (
        Pipen("Noreport", **config)
        .set_start(Process2)
        .set_data([1])
    )
