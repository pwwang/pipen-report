"""Report generation system for pipen"""

from typing import Any, Dict, TYPE_CHECKING, Union
from pipen import plugin, __version__ as pipen_version
from pipen.utils import get_logger

from slugify import slugify

from .manager import ReportManager

if TYPE_CHECKING:
    from pipen import Pipen, Proc

logger = get_logger("report", "info")


class PipenReport:
    """Report plugin for pipen"""

    __version__: str = None
    name = "report"

    def __init__(self) -> None:
        """Constructor"""
        self.manager: ReportManager = None

    @plugin.impl
    def on_setup(self, config: Dict[str, Any]) -> None:
        """Default configrations"""
        # process-level: The report template or file, None to disable
        config.plugin_opts.report = None
        # pipeline-level: path to npm
        config.plugin_opts.report_npm = "npm"
        # pipeline-level:
        # If we fail to install a global copy of frontend dependency
        # in the package directory (may be due to privilege issue),
        # where should we install it?
        # Make sure you have write privileges to it
        config.plugin_opts.report_nmdir = "~/.pipen-report"

    @plugin.impl
    async def on_start(self, pipen: "Pipen") -> None:
        """Check if we have the prerequisites for report generation"""
        self.manager = ReportManager(
            pipen.outdir,
            pipen.workdir,
            pipen.config.plugin_opts.report_npm,
        )
        await self.manager.check_npm_and_setup_dirs()

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
        await self.manager.build(logger)
        del self.manager
        self.manager = None
