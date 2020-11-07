from pipen.plugin import plugin
from pipen.utils import get_logger
from .report import PipenReport
from .report_manager import PipenReportManager

__version__ = '0.0.0'

logger = get_logger('report', 'info')

class PipenReportPlugin:
    version = __version__

    @plugin.impl
    def on_setup(self, plugin_opts):
        """Set the default configurations"""
        # The report template file, False to disable
        plugin_opts.report = False
        # The report directory
        # if None, will be <pipen.outdir>/Report-YYMMDD-HHmm
        # if it is a basename, no '/' in it, it will be
        # <pipen.outdir>/<report_dir>-YYMMDD-HHmm
        # otherwise the path will be used with suffix `-YYMMDD-HHmm`
        # THis cannot be overriden in processes.
        plugin_opts.report_dir = None
        # An option to
        plugin_opts.report_serve = False

    @plugin.impl
    def on_init(self, pipen):
        """Check if we have the prerequisites for report generation"""
        pipen.report_manager = PipenReportManager(pipen)
        pipen.report_manager.check_prerequisites()

    @plugin.impl
    async def on_proc_init(self, proc):
        if proc.plugin_opts.report:
            proc.report = PipenReport(proc)
        else:
            proc.report = None

    @plugin.impl
    async def on_proc_done(self, proc):
        """Prepare the variables in report templates

        This is calling before gc, so I still have access to jobs.
        """
        if proc.report:
            proc.report.prepare()

    @plugin.impl
    async def on_complete(self, pipen):
        """Render and compile the whole report"""
        logger.debug('Assembling report for the pipeline.')
        pipen.report_manager.assemble()
        logger.info('Report generated at %r', str(pipen.report_manager.path))
