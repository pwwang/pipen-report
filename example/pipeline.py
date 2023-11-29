"""An example of using pipen-report to generate reports"""
# also need to install pipen-filters
from pathlib import Path
from pipen import Proc, Pipen, ProcGroup


class MyProcGroup(ProcGroup):
    """A process group"""

    @ProcGroup.add_proc
    def p_pg1(self):

        class PG1(Proc):
            """Copy the image over"""
            input = "inimg:file"
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
            }

        return PG1

    @ProcGroup.add_proc
    def p_pg2(self):

        class PG2(self.p_pg1):
            """Copy the image over 2"""
            requires = self.p_pg1

        return PG2


pg = MyProcGroup()


class ProcessNoTOC(Proc):
    """Report report_toc = False"""
    input = "inimg:file"
    requires = pg.starts
    # Use variable to skip checking
    output = "outimg:file:{{in.inimg | basename}}"
    script = "cp {{in.inimg}} {{out.outimg}}"
    plugin_opts = {
        "report": """
        <script>
            import { Image, Descr } from '$lib';
        </script>
        <h1>Image</h1>
        <Descr>This is a description about the section.</Descr>
        <Image src="{{ job.in.inimg }}" />
        """,
        "report_toc": False,
    }


class ProcessWithPagingWithAVeryLongProcessName(Proc):
    """Report with paging"""
    requires = ProcessNoTOC
    input = "inimg:file"
    # Use variable to skip checking
    output = "outimg:file:{{in.inimg | basename}}"
    script = """
        cp {{in.inimg}} {{out.outimg}}
        tablefile={{job.outdir}}/table.txt
        echo -e 'A\tB\tC\tD\tE\tF\tG\tH\n' > $tablefile
        for i in {1..100}; do
            echo -e "$i$i$i\t$i$i$i\t$i$i$i\t$i$i$i\t$i$i$i\t$i$i$i\t$i$i$i\t$i$i$i" >> $tablefile
        done
    """  # noqa: E501
    plugin_opts = {
        "report": """
        <script>
            import { Image, DataTable, Descr } from '$lib';
        </script>
        <h1>Section 1</h1>
            <h2>Image</h2>
            <Descr title="Description title" style="background-color: #e4e8ff">
                <p>This is a description about the section.</p>
                <p>This is a description in another paragraph.</p>
            </Descr>
            <Image src="{{ job.out.outimg }}" style="max-width: 40%; height: auto;" />
            <h2>Table</h2>
            <DataTable
                src={{ job.outdir | joinpaths: "table.txt" | quote }}
                data={ {{job.outdir | joinpaths: "table.txt" | datatable: sep="\t"}} }
                />
        <h1>This is a very long section name</h1>
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
        """,  # noqa: E501
        "report_paging": 4,
    }


class ProcessWithoutHeadings(Proc):
    """A process without headings"""
    requires = ProcessWithPagingWithAVeryLongProcessName
    input = "inimg:file"
    output = "outimg:file:{{in.inimg | basename}}"
    script = """
        cp {{in.inimg}} {{out.outimg}}
    """
    plugin_opts = {
        "report": """
            <script>
                import { Image } from '$lib';
            </script>
            <Image src="{{ job.out.outimg }}" />
        """
    }


class Pipeline(Pipen):
    outdir = "./output"
    starts = pg.starts
    data = [[Path(__file__).parent.resolve().joinpath("placeholder.png")]]
    # plugin_opts = {
    #     "report_no_collapse_pgs": True,
    # }


if __name__ == "__main__":
    Pipeline().run()
