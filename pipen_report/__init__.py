import logging

from pipen.plugin import plugin
from pipen.utils import get_logger
from .report import PipenReport
from .report_manager import PipenReportManager

__version__ = '0.0.0'

logger = get_logger('report', 'info')

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
        # report_debug = 'pipen'  # attache to pipen's config loglevel
        plugin_opts.report_debug = False

    @plugin.impl
    def on_init(self, pipen):
        if pipen.config.plugin_opts.report_debug == 'pipen':
            logger.setLevel(get_logger().logger.level)
        elif pipen.config.plugin_opts.report_debug:
            logger.setLevel(logging.DEBUG)

    @plugin.impl
    async def on_start(self, pipen):
        """Check if we have the prerequisites for report generation"""
        self.report_manager = PipenReportManager(pipen)
        self.report_manager.check_prerequisites()
        self.report_manager.generate_pipeline_data()

    @plugin.impl
    async def on_proc_done(self, proc, succeeded):
        """Prepare the variables in report templates

        This is calling before gc, so I still have access to jobs.
        """
        if proc.plugin_opts.report and succeeded:
            self.report_manager.process_report(proc, succeeded)

    @plugin.impl
    async def on_complete(self, pipen, succeeded):
        """Render and compile the whole report"""
        if not succeeded:
            return
        if self.report_manager.reports:
            logger.info('Building reports (first-time takes longer due to '
                        'dependency installation) ...')
            self.report_manager.build()
        else:
            logger.info('Skipping reports generation, '
                        'no processes has a report template specified.')
