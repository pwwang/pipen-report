"""pipen-report example using using cloud workdir and outdir native support"""

import os
from pipen import Proc, Pipen
from dotenv import load_dotenv

load_dotenv()
BUCKET = os.getenv("GBATCH_EXAMPLE_BUCKET")


class ImageProcess(Proc):
    """Process to create an image"""

    input = "infile:file"
    output = "outfile:file:{{in.infile.stem}}.png"
    script = """
        cp {{in.infile}} {{out.outfile}}
    """
    plugin_opts = {
        "report": """
            <script>
                import { Image } from '$lib';
            </script>
            <Image src="{{ job.out.outfile }}" />
        """
    }


class TableProcess(Proc):
    """Process to create a table"""

    requires = ImageProcess
    input = "infile:file"
    output = "outfile:file:{{in.infile.stem}}.txt"
    script = """
        echo "head1,head2" > {{out.outfile}}
        echo "data1,data2" >> {{out.outfile}}
    """
    plugin_opts = {
        "report": """
            <script>
                import { DataTable } from '$lib';
            </script>
            <DataTable src="{{ job.out.outfile }}"
                data={ {{job.out.outfile | datatable: sep=",", nrows=1}} } />
        """
    }


class PipelineCloud2(Pipen):
    """Pipeline to create an image and a table"""

    starts = ImageProcess
    data = [[f"gs://{BUCKET}/pipen-test/placeholder.png:/mnt/input/placeholder.png"]]
    outdir = f"gs://{BUCKET}/pipen-test/report-example/cloud3-outdir"
    workdir = f"gs://{BUCKET}/pipen-test/report-example/cloud3-workdir"
    loglevel = "DEBUG"
    scheduler_opts = {
        "fast_mount": f"gs://{BUCKET}/pipen-test:/mnt/input",
    }
    plugin_opts = {
        "report_loglevel": "debug",
    }


if __name__ == "__main__":
    PipelineCloud2().run(profile="gbatch")
