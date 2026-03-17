"""pipen-report example using pipen-gcs to localize the cloud files

This example runs the jobs locally and use google cloud storage as the outdir.
The workdir is still local, but pipen-gcs will help to localize the input files
from cloud storage to local workdir before running the jobs.

When the jobs are done, the output files will be automatically uploaded to the
cloud outdir.

Since the output files are generated locally, the report generation can also
happen locally without needing to download the files from cloud storage again.
"""

import os
from pipen import Proc, Pipen
from dotenv import load_dotenv
import pipen_gcs  # noqa: F401

load_dotenv()
BUCKET = os.getenv("BUCKET")


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


class ImageProcessNonexport(ImageProcess):
    """Process to create an image"""

    requires = ImageProcess
    export = False


class TableProcess(Proc):
    """Process to create a table"""

    requires = ImageProcessNonexport
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


class PipelineCloud1(Pipen):
    """Pipeline to create an image and a table"""

    starts = ImageProcess
    data = [[f"gs://{BUCKET}/pipen-report-example/placeholder.png"]]
    outdir = f"gs://{BUCKET}/pipen-report-example/cloud1-outdir"


if __name__ == "__main__":
    PipelineCloud1().run()
