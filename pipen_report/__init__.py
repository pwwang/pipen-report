from pipen.plugin import plugin
from pipen.utils import get_logger
from .report import PipenReport
from .report_manager import PipenReportManager

__version__ = '0.0.0'

logger = get_logger('report', 'debug')

class PipenReportPlugin:
    version = __version__

    def __init__(self):
        self.report_manager = None

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

    @plugin.impl
    async def on_start(self, pipen):
        """Check if we have the prerequisites for report generation"""
        self.report_manager = PipenReportManager(pipen)
        self.report_manager.check_prerequisites()
        self.report_manager.generate_pipeline_data()

    @plugin.impl
    async def on_proc_done(self, proc):
        """Prepare the variables in report templates

        This is calling before gc, so I still have access to jobs.
        """
        if proc.plugin_opts.report:
            self.report_manager.process_report(proc)

    @plugin.impl
    async def on_complete(self, pipen):
        """Render and compile the whole report"""
        if self.report_manager.reports:
            logger.info('Building reports ...')
            self.report_manager.build()
        else:
            logger.info('Skipping reports generation, '
                        'no processes has a report template specified.')
