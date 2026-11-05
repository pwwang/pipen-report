"""A guided tour of pipen-report

Run from the repo root:

    uv run python example/pipeline.py

and open `output/REPORTS/index.html` afterwards. Each process demonstrates
one way of authoring a report; docstrings become the descriptions in the UI.
"""

from pathlib import Path

# pipen-filters provides the extra template filters used below (e.g. basename)
from pipen import Pipen, Proc, ProcGroup

HERE = Path(__file__).parent.resolve()


class Assets(ProcGroup):
    """Demo assets staged for the example reports"""

    @ProcGroup.add_proc
    def p_stage(self):
        class StageAssets(Proc):
            """Copy the demo image and Plotly figure into the output directory"""

            input = "inimg:file, inplot:file"
            output = (
                "outimg:file:{{in.inimg | basename}}, "
                "outplot:file:{{in.inplot | basename}}"
            )
            script = r"""
cp {{in.inimg}} {{out.outimg}}
cp {{in.inplot}} {{out.outplot}}
"""
            plugin_opts = {
                "report": r"""
<script>
    import { Image, Descr } from '$lib';
</script>

<h1>Staged assets</h1>
<Descr title="Where the example files come from">
    This process copies the two demo files out of the pipeline data, so
    every downstream process has its own copies to work with.
</Descr>
<Image src="{{ job.out.outimg }}" />
""",
            }

        return StageAssets

    @ProcGroup.add_proc
    def p_manifest(self):
        class AssetManifest(self.p_stage):
            """Describe the staged assets in a manifest table"""

            requires = self.p_stage
            input = "outimg:file, outplot:file"
            input_data = lambda ch: ch[["outimg", "outplot"]]
            output = "outmanifest:file:assets.tsv"
            script = r"""
outdir={{job.outdir}} img={{in.outimg}} plot={{in.outplot}} python3 - <<'PY'
import os
from pathlib import Path

outdir = Path(os.environ["outdir"])
rows = [
    ("File", "Size", "Kind"),
    ("placeholder.png", os.path.getsize(os.environ["img"]), "PNG figure"),
    ("plotly.html", os.path.getsize(os.environ["plot"]), "Plotly figure"),
]
(outdir / "assets.tsv").write_text(
    "\n".join("\t".join(map(str, r)) for r in rows)
)
PY
"""
            plugin_opts = {
                "report": r"""
<script>
    import { DataTable, Descr } from '$lib';
</script>

<h1>Asset manifest</h1>
<Descr title="What this table is">
    This process requires `StageAssets` and summarises the files it
    staged. Procs in a ProcGroup are grouped in the index page.
</Descr>
<DataTable src="{{ job.out.outmanifest }}" />
""",
            }

        return AssetManifest


assets = Assets()


class ImageCopy(Proc):
    """Copy the staged placeholder image; subclasses add their report"""

    input = "outimg:file"
    input_data = lambda ch: ch[["outimg"]]
    output = "outimg:file:{{in.outimg | basename}}"
    script = "cp {{in.outimg}} {{out.outimg}}"


class ProcsInSvelte(Proc):
    """Report authored as a Svelte template, using every builtin component"""

    requires = assets.starts
    input = "outimg:file, outplot:file"
    input_data = lambda ch: ch[["outimg", "outplot"]]
    output = (
        "outimg:file:{{in.outimg | basename}}, "
        "outplot:file:{{in.outplot | basename}}"
    )
    script = r"""
cp {{in.outimg}} {{out.outimg}}
cp {{in.outplot}} {{out.outplot}}
outdir={{job.outdir}} python3 - <<'PY'
import os
from pathlib import Path

outdir = Path(os.environ["outdir"])
(outdir / "qc.tsv").write_text(
    "Sample\tTotal_reads\tMapping_rate\tDuplication_rate\tMean_insert_size\n"
    "WT-1\t28400000\t96.1\t12.3\t187\n"
    "WT-2\t31200000\t95.4\t11.8\t192\n"
    "KO-1\t27900000\t94.8\t13.5\t179\n"
    "KO-2\t29600000\t95.9\t12.1\t186\n"
    "HET-1\t30100000\t96.4\t10.9\t190\n"
    "HET-2\t28800000\t95.2\t11.4\t183\n"
)
PY
cat > {{job.outdir}}/tracks.html <<'HTML'
<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Read coverage, WT-1</title>
<style>body { font-family: system-ui; margin: 2rem; }
.track { margin: .4rem 0; background: #0f62fe; height: 10px; }</style></head><body>
<h2>Read coverage along chromosome 1 (mock)</h2>
<div class="track" style="width: 88%"></div><div class="track" style="width: 72%"></div>
<div class="track" style="width: 95%"></div><div class="track" style="width: 61%"></div>
</body></html>
HTML
"""
    plugin_opts = {
        "report": r"""
<script>
    import { Image, DataTable, Descr, Iframe, Plotly, Math } from '$lib';
</script>

<h1>Overview</h1>
<Descr title="A report written as a Svelte template">
    The process renders this Svelte file with liquid, then pipen-report
    preprocesses the resource paths and compiles it.
</Descr>
<h2>Metrics by formula</h2>
<p>The mean insert size is <Math>\bar{x} = \frac{1}{n} \sum_{i=1}^{n} x_i</Math>,
    and the duplication rate is
    <Math displayMode>d = \frac{n_{dup}}{n_{total}}</Math></p>

<h1>QC metrics</h1>
<Descr title="Table 1: per-sample alignment metrics">
    DataTable reads a TSV written by the job script; the toolbar
    downloads the source file.
</Descr>
<DataTable src="{{ job.outdir }}/qc.tsv" />

<h1>Figures</h1>
<h2>Fragment size distribution</h2>
<Descr title="Figure 1: fragment size distribution">
    Image shows the figure with a download toolbar offering the PNG
    itself and the interactive Plotly version.
</Descr>
<Image src="{{ job.out.outimg }}"
    download={ [
        {"src": "{{ job.out.outimg }}", "tip": "PNG placeholder figure"},
        {"src": "{{ job.out.outplot }}", "tip": "Interactive Plotly version"}
    ] } />
<h2>Read coverage</h2>
<Descr title="Figure 2: read coverage">
    Plotly embeds a Plotly figure saved as HTML by an analysis step.
</Descr>
<Plotly src="{{ job.out.outplot }}" title="Read coverage across the reference" />
<h2>Browser tracks</h2>
<Descr title="Figure 3: mock browser tracks">
    Iframe embeds a local HTML page generated by this job.
</Descr>
<Iframe style="height:50vh" src="{{ job.outdir }}/tracks.html" title="Genome browser" />
""",
    }


class ProcsInJSON(ImageCopy):
    """The same components, authored as report.json rendered by render_job"""

    requires = assets.starts
    script = r"""
cp {{in.outimg}} {{out.outimg}}
outdir={{job.outdir}} img={{out.outimg}} python3 - <<'PY'
import json
import os
from pathlib import Path

outdir = os.environ["outdir"]
img = os.environ["img"]
tsv = f"{outdir}/alignment_summary.tsv"
Path(tsv).write_text(
    "Sample\tTotal_reads\tMapped_reads\tMapping_rate\n"
    "WT-1\t28400000\t27326400\t96.2\n"
    "WT-2\t31200000\t29702400\t95.2\n"
    "KO-1\t27900000\t26481000\t94.9\n"
    "KO-2\t29600000\t28386400\t95.9\n"
    "HET-1\t30100000\t29016400\t96.4\n"
)

report = {
    "Flat layout": {
        "Description": {"What this report is": {"flat": [{
            "kind": "descr", "title": "Authored as JSON", "markdown": True,
            "content": (
                "This report is a `report.json` file rendered by "
                "`render_job` and the `render_ui`/`render_component` "
                "filters. Each section below shows one kind of component."
            )}]}},
        "Error": {"A warning for the reader": {"flat": [{
            "kind": "error", "title": "Sample HET-3",
            "content": "Coverage below 10x, excluded from the summary."}]}},
        "Lists": {
            "Ordered list": {"flat": [{
                "kind": "list", "ordered": True,
                "items": ["Trim adapters", "Align reads", "Call variants"]}]},
            "Unordered list": {"flat": [{
                "kind": "list",
                "items": ["All samples passed QC", "Mapping rate above 94%"]}]},
        },
        "Tables": {
            "From a src path": {"flat": [{
                "kind": "table", "src": tsv}]},
            "From a data file": {"flat": [{
                "kind": "table", "src": False, "pageSize": 3,
                "data": {"file": tsv}}]},
        },
        "Image": {"A figure with download options": {"flat": [{
            "kind": "image", "src": img,
            "download": [{"src": img, "tip": "PNG placeholder figure"}]}]}},
        "Tag": {"Any tag, e.g. Markdown": {"flat": [{
            "kind": "tag", "tag": "Markdown",
            "slot": (
                "- **WT-1**: mapping rate 96.2%\n"
                "- **KO-1**: mapping rate 94.9%"
            )}]}},
    },
    "Tabs": {"#": {"#": {"tabs": [
        {"name": "Alignment summary", "contents": [
            {"kind": "table", "src": tsv}]},
        {"name": "File manifest", "contents": [{
            "kind": "list", "items": ["alignment_summary.tsv", "placeholder.png"]}]},
        {"name": "Coverage figure", "contents": [{"kind": "image", "src": img}]},
    ]}}},
    "Table of images": {"#": {"#": {"table_of_images:3": [
        {"title": "Fragment size, WT-1", "descr": "Insert size: 187 bp", "src": img},
        {"title": "Fragment size, KO-1", "descr": "Insert size: 179 bp", "src": img},
        {"title": "Fragment size, HET-1", "descr": "Insert size: 190 bp", "src": img},
    ]}}},
    "Accordion": {"#": {"#": {"accordion": [
        {"title": "Alignment", "contents": [
            {"kind": "descr", "content": "Paired-end alignment with BWA-MEM."},
            {"kind": "list", "items": ["Reference: GRCh38", "Mapper: BWA-MEM"]}]},
        {"title": "Variant calling", "contents": [
            {"kind": "table", "data": {"file": tsv}}]},
    ]}}},
}

Path(f"{outdir}/report.json").write_text(
    json.dumps(report, indent=2, ensure_ascii=False)
)
PY
"""
    plugin_opts = {
        "report": r"""
<script>
    import { Image, DataTable, Descr } from '$lib';
    import {
        Accordion, AccordionItem, Tabs, Tab, TabContent,
        InlineNotification, OrderedList, UnorderedList, ListItem,
    } from '$ccs';
</script>

{{ job | render_job }}
""",
    }


class ProcsNoTOC(ImageCopy):
    """Report with the table of contents disabled"""

    requires = assets.starts
    plugin_opts = {
        "report": r"""
<script>
    import { Image, Descr } from '$lib';
</script>

<h1>A report without a table of contents</h1>
<Descr title="report_toc = False">
    The sections below render as usual, but the sidebar table of
    contents is hidden for this process.
</Descr>
<Image src="{{ job.out.outimg }}" />
""",
        "report_toc": False,
    }


class ProcsMultipleJobs(Proc):
    """A process with two jobs, each rendering a different figure"""

    requires = assets.starts
    input = "infigure:file"
    input_data = lambda ch: [ch.outimg[0], ch.outplot[0]]
    output = "outfigure:file:{{in.infigure | basename}}"
    script = "cp {{in.infigure}} {{out.outfigure}}"
    plugin_opts = {
        "report": r"""
<script>
    import { Image, Plotly, Descr } from '$lib';
</script>

<h1>Job 0: figure as an image</h1>
<Descr>Job 0 received the PNG placeholder and renders it with Image.</Descr>
<Image src="{{ jobs[0].out.outfigure }}" />

<h1>Job 1: figure as a Plotly plot</h1>
<Descr>Job 1 received the Plotly HTML file and renders it with Plotly.</Descr>
<Plotly src="{{ jobs[1].out.outfigure }}" title="Figure rendered by job 1" />
""",
        "report_multiple_jobs": True,
    }


class ProcsWithPaging(ImageCopy):
    """Report with paging: one section per sample, three sections per page"""

    requires = assets.starts
    script = r"""
cp {{in.outimg}} {{out.outimg}}
outdir={{job.outdir}} python3 - <<'PY'
import json
import os
import random
from pathlib import Path

outdir = os.environ["outdir"]

samples = [
    "WT-1", "WT-2", "WT-3",
    "KO-1", "KO-2", "KO-3",
    "HET-1", "HET-2", "HET-3",
]

report = {}
for i, sample in enumerate(samples):
    rng = random.Random(i)
    total = 26000000 + rng.randrange(0, 7000000, 100000)
    mapped = round(total * (94.0 + rng.random() * 3.0))
    Path(f"{outdir}/sample-{sample}.tsv").write_text(
        "Metric\tValue\n"
        f"Total reads\t{total}\nMapped reads\t{mapped}\n"
        f"Mapping rate\t{mapped / total * 100:.1f}%\n"
        f"Duplication rate\t{round(8 + rng.random() * 8, 1)}%\n"
        f"Mean insert size\t{170 + rng.randrange(0, 50, 2)} bp\n"
    )
    report[f"Sample {sample}"] = {"#": {"#": {"flat": [
        {"kind": "descr", "title": f"QC summary for {sample}",
         "content": f"{mapped / total * 100:.1f}% of the {total} reads mapped."},
        {"kind": "table", "pageSize": 4,
         "data": {"file": f"{outdir}/sample-{sample}.tsv"}},
    ]}}}

Path(f"{outdir}/report.json").write_text(
    json.dumps(report, indent=2, ensure_ascii=False)
)
PY
"""
    plugin_opts = {
        "report": r"""
<script>
    import { DataTable, Descr } from '$lib';
</script>

{{ job | render_job }}
""",
        "report_paging": 3,
    }


class Pipeline(Pipen):
    """Example pipeline: a guided tour of pipen-report"""

    outdir = "./output"
    starts = assets.starts
    data = [[(HERE / "placeholder.png", HERE / "plotly.html")]]
    plugin_opts = {"report_force_build": True}


if __name__ == "__main__":
    Pipeline().run()
