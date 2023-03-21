"""An example of using pipen-report to generate reports"""
# also need to install pipen-filters
from pathlib import Path
from pipen import Proc, Pipen


class ProcessNoTOC(Proc):
    """Report without TOC"""
    input = "inimg:file"
    # Use variable to skip checking
    output = "outimg:file:{{in.inimg | basename}}"
    script = "cp {{in.inimg}} {{out.outimg}}"
    plugin_opts = {
        "report": """
        <script>
            import { Image } from '$lib';
        </script>
        <h1>Image</h1>
        <Image src="{{ job.in.inimg }}" />
        """,
        "report_toc": False,
    }


class ProcessWithPaging(Proc):
    """Report with paging"""
    requires = ProcessNoTOC
    input = "inimg:file"
    # Use variable to skip checking
    output = "outimg:file:{{in.inimg | basename}}"
    script = """
        cp {{in.inimg}} {{out.outimg}}
        tablefile={{job.outdir}}/table.txt
        echo -e 'A\tB\tC\n' > $tablefile
        echo -e '1\t2\t3\n' >> $tablefile
        echo -e '4\t5\t6\n' >> $tablefile
        echo -e '7\t8\t9\n' >> $tablefile
        echo -e '10\t11\t12\n' >> $tablefile
        echo -e '13\t14\t15\n' >> $tablefile
        echo -e '16\t17\t18\n' >> $tablefile
        echo -e '19\t20\t21\n' >> $tablefile
    """
    plugin_opts = {
        "report": """
        <script>
            import { Image, DataTable } from '$lib';
        </script>
        <h1>Image</h1>
        <Image src="{{ job.out.outimg }}" />
        <h1>Table</h1>
        <DataTable
            src={{ job.outdir | joinpaths: "table.txt" | quote }}
            data={ {{job.outdir | joinpaths: "table.txt" | datatable: sep="\t"}} }
            />
        <h1>Image</h1>
        <Image src="{{ job.out.outimg }}" />
        <h1>Table</h1>
        <DataTable
            src={{ job.outdir | joinpaths: "table.txt" | quote }}
            data={ {{job.outdir | joinpaths: "table.txt" | datatable: sep="\t"}} }
            />
        <h1>Image</h1>
        <Image src="{{ job.out.outimg }}" />
        <h1>Table</h1>
        <DataTable
            src={{ job.outdir | joinpaths: "table.txt" | quote }}
            data={ {{job.outdir | joinpaths: "table.txt" | datatable: sep="\t"}} }
            />
        <h1>Image</h1>
        <Image src="{{ job.out.outimg }}" />
        <h1>Table</h1>
        <DataTable
            src={{ job.outdir | joinpaths: "table.txt" | quote }}
            data={ {{job.outdir | joinpaths: "table.txt" | datatable: sep="\t"}} }
            />
        <h1>Image</h1>
        <Image src="{{ job.out.outimg }}" />
        <h1>Table</h1>
        <DataTable
            src={{ job.outdir | joinpaths: "table.txt" | quote }}
            data={ {{job.outdir | joinpaths: "table.txt" | datatable: sep="\t"}} }
            />
        <h1>Image</h1>
        <Image src="{{ job.out.outimg }}" />
        <h1>Table</h1>
        <DataTable
            src={{ job.outdir | joinpaths: "table.txt" | quote }}
            data={ {{job.outdir | joinpaths: "table.txt" | datatable: sep="\t"}} }
            />
        <h1>Image</h1>
        <Image src="{{ job.out.outimg }}" />
        <h1>Table</h1>
        <DataTable
            src={{ job.outdir | joinpaths: "table.txt" | quote }}
            data={ {{job.outdir | joinpaths: "table.txt" | datatable: sep="\t"}} }
            />
        <h1>Image</h1>
        <Image src="{{ job.out.outimg }}" />
        <h1>Table</h1>
        <DataTable
            src={{ job.outdir | joinpaths: "table.txt" | quote }}
            data={ {{job.outdir | joinpaths: "table.txt" | datatable: sep="\t"}} }
            />
        """,
        "report_paging": 4,
    }


class Pipeline(Pipen):
    outdir = "./output"
    starts = ProcessNoTOC
    data = [[Path(__file__).parent.resolve().joinpath("placeholder.png")]]


if __name__ == "__main__":
    Pipeline().run()
