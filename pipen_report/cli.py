"""Provide a command line interface for the pipen_report plugin"""
from __future__ import annotations

import stat
import http.server
import socketserver
import subprocess as sp
from pathlib import Path
from typing import TYPE_CHECKING

import rtoml
from copier import run_copy
from pipen.cli import CLIPlugin

from .defaults import NPM, NMDIR, LOCAL_CONFIG, GLOBAL_CONFIG, CONFIG_KEYS
from .utils import get_config


if TYPE_CHECKING:
    from argx import ArgumentParser, Namespace


class PipenCliReport(CLIPlugin):
    """CLI utility for pipen-report"""
    from .versions import __version__

    name = "report"

    def __init__(
        self,
        parser: ArgumentParser,
        subparser: ArgumentParser,
    ) -> None:
        super().__init__(parser, subparser)
        config_command = subparser.add_command(
            "config",
            help="Configure pipen-report",
            exit_on_void=True,
        )
        config_command.add_argument(
            "--local",
            "-l",
            help=(
                "Save the configuration locally (./.pipen-report.toml)? "
                "Otherwise, the configuration will be saved globally "
                "in the user's home directory (~/.pipen-report.toml). "
                "The local configuration has higher priority than the "
                "global configuration."
            ),
            action="store_true",
            default=False,
        )
        config_command.add_argument(
            "--list",
            help="List the configuration",
            action="store_true",
            default=False,
        )
        config_command.add_argument(
            "--extlibs",
            help="External components to be used in the report",
        )
        config_command.add_argument(
            "--npm",
            help="The path to npm",
            default=NPM,
        )
        config_command.add_argument(
            "--nmdir",
            help=(
                "Where should the frontend dependencies installed?\n"
                "By default, the frontend dependencies will be installed in "
                "frontend/ of the python package directory. However, this "
                "directory may not be writable. In this case, the frontend "
                "dependencies will be installed in the directory specified."
            ),
            default=NMDIR,
        )
        config_command.add_argument(
            "--nobuild",
            help=(
                "Don't build the final report. "
                "If True only preprare the environment "
                "Say if you want to do the building manually"
            ),
            action="store_true",
            default=False,
        )
        subparser.add_command(
            "update",
            help="Install/Update the frontend dependencies",
        )
        serve_command = subparser.add_command(
            "serve",
            help="Serve the report",
        )
        serve_command.add_argument(
            "--port",
            "-p",
            help="The port to serve the report",
            default=18520,
            type=int,
        )
        serve_command.add_argument(
            "--host",
            help="The host to serve the report",
            default="127.0.0.1"
        )
        serve_command.add_argument(
            "--reportdir",
            "-r",
            help=(
                "The directory of the reports, where the REPORTS/ directory is"
            ),
            required=True,
            type=Path,
        )

    def exec_command(self, args: Namespace) -> None:
        """Execute the command"""
        if args.COMMAND2 == "config":
            self._config(args)
        elif args.COMMAND2 == "update":
            self._update(args)
        elif args.COMMAND2 == "serve":  # pragma: no cover
            self._serve(args)
        else:  # pragma: no cover
            super().exec_command(args)

    def _config(self, args: Namespace) -> None:
        """Execute the config command"""
        if args.list:
            print("Note that these values can still be overwritten by:")
            print(
                "\033[4m\033[1m"
                "pipeline.plugin_opts.report_<key> = <value>"
                "\033[0m\033[0m"
            )
            print("")
            keylen = max(len(key) for key in CONFIG_KEYS)
            for key in CONFIG_KEYS:
                print(
                    f"\033[4m\033[1m{key}\033[0m\033[0m".ljust(keylen + 17, ' ')
                    + f"= {get_config(key)}"
                )
            return

        config_file = LOCAL_CONFIG if args.local else GLOBAL_CONFIG

        config = {}
        config["npm"] = args.npm
        config["nmdir"] = args.nmdir

        rtoml.dump(config, config_file)
        print("The configuration is saved to")
        print(f"\033[4m{config_file}\033[0m")

    def _update(self, args: Namespace) -> None:
        """Execute the update command"""
        nmdir = Path(get_config("nmdir")).resolve()
        if nmdir != Path(NMDIR).resolve():  # pragma: no cover
            run_copy(NMDIR, nmdir, overwrite=True, quiet=True)

        if not (nmdir.stat().st_mode & stat.S_IWUSR):  # pragma: no cover
            print("The frontend directory is not writable:")
            print(f"\033[4m{nmdir}\033[0m")
            print("")
            print("You should either:")
            print(
                "1. Run `sudo pipen report update` "
                "to install/update the frontend dependencies"
            )
            print(
                "2. Run `pipen report config --nmdir <dir>` "
                "to specify a different directory to install "
                "the frontend dependencies"
            )

        else:
            print("The frontend directory:")
            print(f"\033[4m{nmdir}\033[0m")
            print("")
            print("Running: npm update ...")
            p = sp.Popen(
                [get_config("npm"), "update"],
                cwd=str(nmdir),
                stdout=sp.PIPE,
                stderr=sp.STDOUT,
            )
            for line in p.stdout:
                print(line.decode(), end="")
            p.wait()

    def _serve(self, args: Namespace) -> None:  # pragma: no cover
        """Execute the serve command"""
        reportdir = args.reportdir
        port = args.port
        host = args.host

        if not (reportdir / "REPORTS").exists():
            print("The REPORTS/ directory is not found in:")
            print(f" \033[4m{reportdir}\033[0m")
            print("The report is not generated yet?")
            return

        print(f"Serving the report and data at http://{host}:{port}/")
        print(f"Find the report page: http://{host}:{port}/REPORTS/")
        print("Press Ctrl+C to stop the server")
        print("")

        class Handler(http.server.SimpleHTTPRequestHandler):
            """The request handler"""
            def __init__(self, *args, **kwargs) -> None:
                kwargs["directory"] = reportdir
                super().__init__(*args, **kwargs)

            def do_GET(self) -> None:
                """Handle the GET request"""
                if self.path == "/REPORTS":
                    self.path = "/REPORTS/index.html"

                try:
                    super().do_GET()
                except BrokenPipeError as e:
                    self.log_error(str(e))

        with socketserver.TCPServer((host, port), Handler) as httpd:
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                pass
