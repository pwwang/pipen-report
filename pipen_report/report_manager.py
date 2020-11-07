from os import PathLike
from pathlib import Path
from datetime import datetime

import cmdy

SCAFFOLDING = Path(__file__).parent / 'scaffolding'

class PipenReportManager:

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

    def check_prerequisites(self):
        """Check the prerequisites for pipen report manager

        We need to check:
        1. if the path exists for the output directory
        2. if npm or yarn is installed
        """
        if self.path.is_dir():
            raise ValueError('Report directory already exists.')

        try:
            npm_installed = cmdy.npm('-v', _raise=False).rc == 0
        except cmdy.CmdyExecNotFoundError:
            npm_installed = False

        if not npm_installed :
            raise ValueError('npm is required to '
                             'generate reports for pipen.')


    def assemble(self):
        ...
