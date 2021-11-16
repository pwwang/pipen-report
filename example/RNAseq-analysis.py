"""A reimplementation of https://f1000research.com/articles/5-1408/v3"""
# also requires:
# pipen-filters

from pipen import Proc, Pipen


class DataPreparation(Proc):
    """Download and prepare the data"""

    input = "link,groups,lanes"
    # output a data directory and a sample information file
    output = "datadir:dir:data, samplefile:file:samples.txt"
    # Let's use python to do this
    lang = "python"
    script = "file://scripts/DataPreparation.py"
    plugin_opts = {"report": "file://reports/DataPreparation.svelte"}


class DataPreprocessing(Proc):
    """Data transformation, filtering and normalization"""

    requires = DataPreparation
    input = "datadir:dir, samplefile:file"
    # preprocessed expression file (RDS)
    output = "exprfile:file:exprs.rds"
    # Use R
    lang = "Rscript"
    script = "file://scripts/DataPreprocessing.R"
    plugin_opts = {
        "report": "file://reports/DataPreprocessing.svelte",
        "report_toc": False,
        # "report_force_export": False,
    }


class DEAnalysis(Proc):
    """Differential expression analysis"""

    requires = DataPreparation, DataPreprocessing
    input = "samplefile:file, exprfile:file"
    output = "outdir:dir:results"
    lang = "Rscript"
    script = "file://scripts/DEAnalysis.R"
    plugin_opts = {"report": "file://reports/DEAnalysis.svelte"}


if __name__ == "__main__":

    Pipen(
        name="RNA-seq analysis",
        desc=__doc__,
        outdir="./output",
        plugin_opts={"report_forks": 4},
    ).set_start(DataPreparation).set_data(
        [
            (
                "https://www.ncbi.nlm.nih.gov/geo/download/"
                "?acc=GSE63310&format=file",
                "LP,ML,Basal,Basal,ML,LP,Basal,ML,LP",
                "L004,L004,L004,L006,L006,L006,L006,L008,L008",
            )
        ]
    ).run()
