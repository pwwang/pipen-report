import tarfile
import urllib.request
from pathlib import Path

from plotnine import *
from plotnine_prism import *
from datar.all import _no_warn
from datar.all import *


# input
link = {{in.link | quote}}
groups = {{in.groups | split: ","}}
lanes = {{in.lanes | split: ","}}
# save the download file
outdir = Path({{job.outdir | quote}})
datafile = outdir / "GSE63310_RAW.tar"
# output
datadir = Path({{out.datadir | quote}})
samplefile = Path({{out.samplefile | quote}})


def download_data(link, target):
    """Download the data only when it is not downloaded"""
    if not datafile.is_file():
        resp = urllib.request.urlopen(link)
        with datafile.open("wb") as fdata:
            fdata.write(resp.read())


def unarchive_data(archive, targetdir):
    with tarfile.open(archive) as tar:
        tar.extractall(targetdir)


def collect_sampleinfo(datadir, samplefile):
    """Collect sample information"""
    df = tibble(
        samples=[
            dfile.stem.split("_", 1)[1][:-4]
            for dfile in sorted(datadir.glob("*.txt.gz"))
            if not dfile.stem.startswith("GSM1545538")
            and not dfile.stem.startswith("GSM1545541")
        ],
        group=groups,
        lane=lanes,
    )
    df.to_csv(samplefile)
    return df


def statistics(df):
    p1 = (
        ggplot(df)
        + geom_bar(aes("group"))
        + ggtitle("Number of samples per group")
        + theme_prism()
    )
    p1.save(outdir / "nsamples_per_group.png")
    p2 = (
        ggplot(df)
        + geom_bar(aes("lanes"))
        + ggtitle("Number of samples per lane")
        + theme_prism()
    )
    p2.save(outdir / "nsamples_per_lane.png")


if __name__ == "__main__":
    download_data(link, datafile)
    unarchive_data(datafile, datadir)
    df = collect_sampleinfo(datadir, samplefile)
    statistics(df)
