"""pipen-report example using using cloud workdir and outdir native support

This example runs the jobs locally but operates the files directly on Google
Cloud Storage using pipen's native cloud path support. The outdir and workdir are
both set to cloud storage paths. In the job scripts, we use `cloudsh` commands to
manipulate the files on cloud storage directly.

Since the output files are generated on cloud storage, when generating the report,
the files that are needed will be downloaded from cloud storage automatically.
"""

import os
from pipen import Proc, Pipen
from dotenv import load_dotenv

load_dotenv()
BUCKET = os.getenv("BUCKET")


class ImageProcess(Proc):
    """Process to create an image"""

    input = "infile:file"
    output = "outfile:file:{{in.infile.stem}}.png"
    script = """
        cloudsh cp {{in.infile}} {{out.outfile}}
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
    """Process to create an image without exporting output to cloud"""

    requires = ImageProcess
    export = False


class TableProcess(Proc):
    """Process to create a table"""

    requires = ImageProcessNonexport
    input = "infile:file"
    output = "outfile:file:{{in.infile.stem}}.txt"
    script = """
        echo "head1,head2" | cloudsh sink {{out.outfile}}
        echo "data1,data2" | cloudsh sink -a {{out.outfile}}
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
    data = [[f"gs://{BUCKET}/pipen-report-example/placeholder.png"]]
    outdir = f"gs://{BUCKET}/pipen-report-example/cloud2-outdir"
    workdir = f"gs://{BUCKET}/pipen-report-example/cloud2-workdir"
    plugin_opts = {
        "report_loglevel": "debug",
    }


if __name__ == "__main__":
    PipelineCloud2().run()
