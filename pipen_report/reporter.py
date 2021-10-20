"""Report generation system for pipen"""

from typing import Any, Dict, TYPE_CHECKING, Union
from pipen import plugin
from pipen.utils import get_logger


from .manager import ReportManager
from .versions import __version__

if TYPE_CHECKING:
    from pipen import Pipen, Proc

logger = get_logger("report")


class PipenReport:
    """Report plugin for pipen"""

    __version__: str = __version__
    name = "report"

    def __init__(self) -> None:
        """Constructor"""
        self.manager: ReportManager = None

    @plugin.impl
    def on_setup(self, config: Dict[str, Any]) -> None:
        """Default configrations"""
        # process-level: The report template or file, None to disable
        config.plugin_opts.report = None
        # process-level
        # The order of the process to show in the index page and app menu
        config.plugin_opts.report_order = 0
        # pipeline-level: path to npm
        config.plugin_opts.report_npm = "npm"
        # pipeline-level:
        # If we fail to install a global copy of frontend dependency
        # in the package directory (may be due to privilege issue),
        # where should we install it?
        # Make sure you have write privileges to it
        config.plugin_opts.report_nmdir = "~/.pipen-report"
        # pipeline-level
        # Don't build the final report, only preprare the environment
        # Say if you want to do the building manually
        config.plugin_opts.report_nobuild = False
        # pipeline-level
        # logging level
        config.plugin_opts.report_logging = "info"
        # pipeline-level
        # How many cores to use to build the reports for processes
        # If None, use config.forks
        config.plugin_opts.report_forks = None
        # pipeline-level
        # Force the process to export output when report template is given
        config.plugin_opts.report_force_export = True

    @plugin.impl
    async def on_start(self, pipen: "Pipen") -> None:
        """Check if we have the prerequisites for report generation"""
        loglevel = pipen.config.plugin_opts.report_logging
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
        try:
            pipeline_plugin_opts = proc.pipeline.config.get("plugin_opts", {})
        except AttributeError:
            # in case pipeline initialization fails
            return

        if not pipeline_plugin_opts.get(
            "report_force_export", True
        ):
            return

        proc_plugin_opts = proc.plugin_opts or {}
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
