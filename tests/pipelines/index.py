
from pipen import Proc, Pipen


class Process(Proc):
    """Example process"""
    input = "a:var, b:var"
    output = "c:var:{{ in.a + in.b }}"
    plugin_opts = {
        "report": """<h1>Process</h1>"""
    }


def pipeline(**config):
    """Example pipeline"""
    class Index(Process):
        """If a process is called index, see if it gets renamed to index_.html
        """

    return (
        Pipen("Index-process", **config)
        .set_start(Index)
        .set_data([(1, 2)])
    )
