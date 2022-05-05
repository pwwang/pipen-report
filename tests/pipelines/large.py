
from pipen import Proc, Pipen


class Process(Proc):
    """Example process"""
    input = "a:var, b:var"
    output = "c:var:{{ in.a + in.b }}"
    plugin_opts = {
        "report": """
            <h1>Process</h1><p>{{ job.in.a }} + {{ job.in.b }} = {{ job.out.c }}</p>
        """ * 1000
    }


def pipeline(**config):
    """Example pipeline"""
    class Process2(Process):
        ...

    return (
        Pipen("Large-report", **config)
        .set_start(Process2)
        .set_data([(1, 2)])
    )
