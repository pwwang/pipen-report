"""pipen-report example using using cloud workdir and outdir native support"""

# # NOT RUN
# # This example needs to run on Google Cloud Platform

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


class ImageProcessNonexport(ImageProcess):
    """Process to create an image without exporting the output"""

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


class PipelineCloud3(Pipen):
    """Pipeline to create an image and a table"""

    starts = ImageProcess
    data = [["/mnt/disks/input/placeholder.png"]]
    outdir = f"gs://{BUCKET}/pipen-test/report-example/cloud3-outdir"
    workdir = f"gs://{BUCKET}/pipen-test/report-example/cloud3-workdir"
    loglevel = "DEBUG"
    scheduler_opts = {
        "mount": f"gs://{BUCKET}/pipen-test:/mnt/disks/input",
    }
    plugin_opts = {
        "report_loglevel": "debug",
    }


if __name__ == "__main__":
    PipelineCloud3().run(profile="gbatch")
