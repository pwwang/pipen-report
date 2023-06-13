"""Report generation system for pipen"""
from __future__ import annotations

from typing import TYPE_CHECKING, Union
from pipen import plugin
from pipen.utils import get_logger

from .utils import get_config
from .versions import __version__  # noqa: F401
from .report_manager import ReportManager

if TYPE_CHECKING:
    from pipen import Pipen, Proc

logger = get_logger("report")


class PipenReport:
    """Report plugin for pipen

    Configurations:
        report: The report template or file, None to disable
        report_order: The order of the process to show in the index page and
            app menu
        report_toc: Whether include TOC for the process report or not
        report_paging: Split the report for a process by h1's
            None: don't split; 3: 3 h1's in a page
        report_loglevel: logging level
        report_force_export: Force the process to export output when
            report template is given
        report_npm: Path to npm
        report_nmdir: Where should the frontend dependencies installed?
            By default, the frontend dependencies will be installed in
            frontend/ of the python package directory. However, this
            directory may not be writable. In this case, the frontend
            dependencies will be installed in the directory specified.
        report_nobuild: Don't build the final report.
            If True only preprare the environment
            Say if you want to do the building manually
        report_extlibs: External components to be used in the report
        report_no_collapse_pgs: Don't collapse the procgroups in the index page
    """

    version = __version__
    name = "report"

    @plugin.impl
    async def on_init(self, pipen: Pipen) -> None:
        """Default configrations"""
        # pipeline-level
        # logging level
        pipen.config.plugin_opts.setdefault("report_loglevel", "info")
        # pipeline-level
        # Force the process to export output when report template is given
        pipen.config.plugin_opts.setdefault("report_force_export", True)
        # pipeline-level
        pipen.config.plugin_opts.setdefault("report_npm", None)
        # pipeline-level
        pipen.config.plugin_opts.setdefault("report_nmdir", None)
        # pipeline-level
        pipen.config.plugin_opts.setdefault("report_nobuild", None)
        # pipeline-level
        pipen.config.plugin_opts.setdefault("report_extlibs", None)
        # pipeline-level
        pipen.config.plugin_opts.setdefault("report_no_collapse_pgs", False)

        # process-level: The report template or file, None to disable
        pipen.config.plugin_opts.setdefault("report", None)
        # process-level
        # The order of the process to show in the index page and app menu
        pipen.config.plugin_opts.setdefault("report_order", 0)
        # process-level
        # Whether include TOC for the process report or not
        pipen.config.plugin_opts.setdefault("report_toc", True)
        # process-level
        # Split the report for a process by h1's
        # None: don't split; 3: 3 h1's in a page
        pipen.config.plugin_opts.setdefault("report_paging", False)

    @plugin.impl
    async def on_start(self, pipen: "Pipen") -> None:
        """Check if we have the prerequisites for report generation"""
        loglevel = pipen.config.plugin_opts.report_loglevel
        logger.setLevel(
            loglevel
            if isinstance(loglevel, int)
            else loglevel.upper()
        )
        self.manager = ReportManager(
            pipen.config.plugin_opts or {},
            pipen.outdir,
            pipen.workdir,
        )
        self.manager.check_npm_and_setup_dirs()
        self.manager.init_pipeline_data(pipen)

    @plugin.impl
    def on_proc_create(self, proc: Proc) -> None:
        """For a non-export process to export if report template is given"""
        # proc.plugin_opts not updated yet, check pipeline options
        try:
            pipeline_plugin_opts = proc.pipeline.config.get("plugin_opts", {})
        except AttributeError:  # pragma: no cover
            # in case pipeline initialization fails
            return

        proc_plugin_opts = proc.plugin_opts or {}
        if not proc_plugin_opts.get(
            "report_force_export",
            pipeline_plugin_opts.get("report_force_export", False)
        ):
            return

        if not proc_plugin_opts.get("report", False):
            return
        if proc.export is not None:
            return

        proc.export = True

    @plugin.impl
    async def on_proc_done(
        self, proc: "Proc", succeeded: Union[str, bool]
    ) -> None:
        """Generate reports for each process"""
        self.manager.render_proc_report(proc, succeeded)

    @plugin.impl
    async def on_complete(self, pipen: "Proc", succeeded: bool) -> None:
        """Render and compile the entire report"""
        if not succeeded:
            return

        if not get_config(
            "nobuild",
            pipen.config.plugin_opts.get("report_nobuild"),
        ):
            await self.manager.build(pipen)

        del self.manager
        self.manager = None
