
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
