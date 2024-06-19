from pathlib import Path
import sys
from pipen import Proc, Pipen

HERE = Path(__file__).parent


class Process(Proc):
    """Example process"""
    input = "a:var, b:var"
    output = "c:var:{{ in.a + in.b }}"
    plugin_opts = {
        "report": """
            <script>
                import Component from '$extlibs/Component.svelte';
            </script>
            <h1>Process</h1>
            <Component text="Hello world" />
        """
    }


def pipeline(**config):
    """Example pipeline"""
    class Index(Process):
        """If a process is called index, see if it gets renamed to index_.html
        """
    config.setdefault("plugin_opts", {})["report_extlibs"] = (
        str(HERE.resolve() / "extlibs")
    )
    return (
        Pipen("Extlibs-process", **config)
        .set_start(Index)
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

