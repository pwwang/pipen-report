import logging
from os import PathLike
from pathlib import Path
from datetime import datetime
import json

from slugify import slugify
from pipen.exceptions import TemplateRenderingError
import cmdy

from .filters import datatable

PRESERVED_TAGS = {
    '{#if': '<svelte:if>',
    '{#each': '<svelte:each>',
    '{#key': '<svelte:key>',
    '{#await': '<svelte:await>',
}

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

    def process_report(self, proc, status):

        from . import logger
        report = str(proc.plugin_opts.report)
        if report.startswith('file://'):
            report = report[7:]
        report_file = Path(proc.workdir) / f'{slugify(proc.name)}.svx'
        if (status == 'cached' and
                len(report) < 512 and
                report_file.exists() and
                report_file.stat().st_mtime >= Path(report).stat().st_mtime):
            proc.log('debug',
                     'Process cached, skip generating report.',
                     logger=logger)
            self.reports.append(str(report_file))
            return

        # avoid future run to use it in case report file failed to compile
        if report_file.exists():
            report_file.unlink()

        def jobdata(job):
            data = job.rendering_data['job']
            data.update({'in': job.rendering_data['in'],
                         'out': job.rendering_data['out']})
            return data

        rendering_data = {
            'proc': {key: val for key, val in proc.__dict__.items()
                     if key in ('lang', 'forks', 'name', 'desc', 'size')},
            'args': proc.args,
            'jobs': [jobdata(job) for job in proc.jobs]
        }
        # first job
        rendering_data['job'] = rendering_data['jobs'][0]
        rendering_data['job0'] = rendering_data['jobs'][0]
        rendering_data['report'] = {
            'datatable': datatable
        }

        # render report with process/job data
        if len(report) < 512 and Path(report).is_file():
            report = Path(report).read_text()

        for key, val in PRESERVED_TAGS.items():
            report = report.replace(key, val)

        template = proc.template(report, **proc.envs)

        try:
            rendered = template.render(rendering_data)
        except Exception as exc:
            raise TemplateRenderingError(
                f'[{proc.name}] Failed to render report file.'
            ) from exc

        for key, val in PRESERVED_TAGS.items():
            rendered = rendered.replace(val, key)
        report_file.write_text(rendered)

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
        logger.debug('Command: %s', cmd.strcmd)
        if result.rc != 0 or result.stderr:
            for line in result.stderr.splitlines():
                logger.error(line)
        else:
            logger.info('Reports generated at %r', str(self.path))