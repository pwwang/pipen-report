
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
