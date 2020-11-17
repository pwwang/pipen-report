from os import PathLike
from pathlib import Path
from datetime import datetime
import json

from slugify import slugify
from liquid import LiquidPython
from liquid.python.parser import NodeScanner, NodeTag, NodeOutput
import cmdy

# disable {#  #} for liquid
NodeScanner.NODES = (NodeOutput, NodeTag)

SCAFFOLDING = Path(__file__).parent / 'scaffolding'

class PipenReportManager:
    __slots__ = ('pipen', 'path', 'pipeline_datafile',
                 'pipen_report_svx_version', 'reports')

    def __init__(self, pipen):
        self.pipen = pipen
        config_report_dir = pipen.config.plugin_opts.report_dir
        suffix = datetime.today().strftime('-%y%m%d-%H%M')
        if not config_report_dir:
            self.path = Path(pipen.outdir) / f'Report{suffix}'
        elif (isinstance(config_report_dir, str) and
                '/' not in config_report_dir):
            self.path = Path(pipen.outdir) / f'{config_report_dir}{suffix}'
        else:
            path = Path(config_report_dir)
            self.path = path.parent / f'{path.name}{suffix}'

        self.pipen_report_svx_version = None
        self.pipeline_datafile = None
        self.reports = []

    def check_prerequisites(self):
        """Check the prerequisites for pipen report manager

        Check if pipen-report-svx is installed
        """
        try:
            self.pipen_report_svx_version = cmdy.pipen_report_svx(
                '--version',
                _raise=False,
                _exe='pipen-report-svx'
            ).stdout.strip()

        except cmdy.CmdyExecNotFoundError:
            pass

        if not self.pipen_report_svx_version:
            raise ValueError('pipen-report-svx is required to '
                             'generate reports for pipen.')

    def generate_pipeline_data(self):
        from pipen import __version__ as pipen_version
        from . import __version__ as  pipen_report_version
        data = {
            'name': self.pipen.name,
            'desc': self.pipen.desc,
            'versions': {
                'pipen': pipen_version,
                'pipen-report': pipen_report_version,
                'pipen-report-svx': self.pipen_report_svx_version
            },
            'processes': [
                {'name': proc.name,
                 'slug': slugify(proc.name),
                 'desc': proc.desc}
                for proc in self.pipen.procs
                if proc.plugin_opts.report
            ]
        }

        # save it as json
        self.pipeline_datafile = Path(self.pipen.config.workdir) / 'pipeline.json';
        with self.pipeline_datafile.open('w') as fdata:
            json.dump(data, fdata)

    def process_report(self, proc):

        def jobdata(job):
            data = job.rendering_data['job']
            data.update({'in': job.rendering_data['in'],
                         'out': job.rendering_data['out']})
            return data

        rendering_data = {
            'proc': proc,
            'args': proc.args,
            'jobs': [jobdata(job) for job in proc.jobs]
        }
        # first job
        rendering_data['job'] = rendering_data['jobs'][0]
        rendering_data['job0'] = rendering_data['jobs'][0]

        # render report with process/job data
        template = LiquidPython(proc.plugin_opts.report)
        report_file = Path(proc.workdir) / f'{slugify(proc.name)}.svx'
        with report_file.open('w') as frpt:
            frpt.write(template.render(**rendering_data))

        self.reports.append(str(report_file))

    def build(self):
        from . import logger
        cmd = cmdy.pipen_report_svx(
            reports=self.reports,
            outdir=self.path,
            metadata=self.pipeline_datafile,
            _exe='pipen-report-svx'
        ).hold()
        result = cmd.run()
        if result.rc != 0 or result.stderr:
            logger.error('Command: %s', cmd.strcmd)
            for line in result.stderr.splitlines():
                logger.error(line)
