"""Report generation system for pipen"""

from typing import TYPE_CHECKING, Union
from pipen import plugin
from pipen.utils import get_logger


from .manager import ReportManager
from .versions import __version__  # noqa: F401

if TYPE_CHECKING:
    from pipen import Pipen, Proc

logger = get_logger("report")


class PipenReport:
    """Report plugin for pipen"""

    __version__: str = __version__  # noqa: F811
    name = "report"

    def __init__(self) -> None:  # pragma: no cover
        """Constructor"""
        self.manager: ReportManager = None

    @plugin.impl
    async def on_init(self, pipen: "Pipen") -> None:
        """Default configrations"""
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
        # pipeline-level: path to npm
        pipen.config.plugin_opts.setdefault("report_npm", "npm")
        # pipeline-level:
        # If we fail to install a global copy of frontend dependency
        # in the package directory (may be due to privilege issue),
        # where should we install it?
        # Make sure you have write privileges to it
        pipen.config.plugin_opts.setdefault("report_nmdir", "~/.pipen-report")
        # pipeline-level
        # Don't build the final report, only preprare the environment
        # Say if you want to do the building manually
        pipen.config.plugin_opts.setdefault("report_nobuild", False)
        # pipeline-level
        # logging level
        pipen.config.plugin_opts.setdefault("report_loglevel", "info")
        # pipeline-level
        # How many cores to use to build the reports for processes
        # If None, use config.forks
        pipen.config.plugin_opts.setdefault("report_forks", None)
        # pipeline-level
        # Force the process to export output when report template is given
        pipen.config.plugin_opts.setdefault("report_force_export", True)

    @plugin.impl
    async def on_start(self, pipen: "Pipen") -> None:
        """Check if we have the prerequisites for report generation"""
        loglevel = pipen.config.plugin_opts.report_loglevel
        logger.setLevel(
            loglevel if isinstance(loglevel, int) else loglevel.upper()
        )
        self.manager = ReportManager(
            pipen.outdir,
            pipen.workdir,
            pipen.config.plugin_opts.report_npm,
        )
        await self.manager.check_npm_and_setup_dirs()

    @plugin.impl
    def on_proc_init(self, proc: "Proc") -> None:
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
        await self.manager.render_proc_report(proc, succeeded, logger)

    @plugin.impl
    async def on_complete(self, pipen: "Proc", succeeded: bool) -> None:
        """Render and compile the entire report"""
        if not succeeded:
            return

        await self.manager.prepare_frontend(pipen, logger)
        if not pipen.config.plugin_opts.report_nobuild:
            await self.manager.build(pipen, logger)

        del self.manager
        self.manager = None
