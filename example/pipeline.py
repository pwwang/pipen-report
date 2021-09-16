import sys

from pathlib import Path
from pipen import Proc, Pipen

HERE = Path(__file__).parent

# You don't need this if you have pipen_report installed
sys.path.insert(0, HERE.parent.as_posix())
from pipen_report import PipenReport

class Subset(Proc):
    """Subset the input data using pandas"""

    input = "name"
    output = "outfile:file:mpg-subset.csv"
    lang = "python"
    script = """
        from datar.datasets import mpg
        from datar.all import f, select
        out = mpg >> select(f.model, f.displ)
        out.to_csv("{{out.outfile}}")
    """
    plugin_opts = {"report": "file://Subset.svelte"}


class Plot(Proc):
    """Plot the data"""

    requires = Subset
    input = "datafile:file"
    output = "plotfile:file:mpg.png"
    lang = "python"
    script = """
        import pandas
        from plotnine import *
        data = pandas.read_csv("{{in.datafile}}")
        p = (
            ggplot(data)
            + geom_boxplot(aes(x="model", y="displ"))
            + theme(axis_text_x=element_text(angle=90, vjust=1.5, hjust=1))
        )
        p.save("{{out.plotfile}}")
    """
    plugin_opts = {
        "report": """
            <script>
                import { Image } from "@@";
            </script>
            <h1>displ vs model from mpg data</h1>
            <Image src="{{job.out.plotfile}}"  />
        """
    }


if __name__ == "__main__":
    Pipen(
        name="plot-mpg",
        desc="Awesome pipeline",
        outdir=HERE / "output",
        plugins=[PipenReport],
        plugin_opts={"report_logging": "debug", "report_forks": 4}
    ).run(Subset)
