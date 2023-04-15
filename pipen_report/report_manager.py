from __future__ import annotations
import inspect
import json

import shutil
import sys
from os import PathLike
from pathlib import Path
from typing import TYPE_CHECKING, Any, List, Mapping, MutableMapping, Type

import cmdy
from cmdy.cmdy_exceptions import CmdyReturnCodeError
from copier import run_auto
from slugify import slugify
from pipen import Proc
from pipen.exceptions import TemplateRenderingError
from pipen.template import TemplateLiquid, TemplateJinja2
from pipen.utils import get_base

from .filters import FILTERS
from .preprocess import preprocess
from .utils import get_config
from .versions import version_str

if TYPE_CHECKING:
    from pipen import Pipen
    from pipen.job import Job
    from pipen.template import Template


def _render_file(
    engine: Type[Template],
    engine_opts: MutableMapping[str, Any],
    source: str,
    render_data: Mapping[str, Any],
) -> str:
    """Render a template file"""
    if engine in (TemplateLiquid, TemplateJinja2):
        # Avoid {#if ... } being treated as jinja comments
        engine_opts["comment_start_string"] = "{!"
        engine_opts["comment_end_string"] = "!}"
    return engine(source, **engine_opts).render(render_data)


class ReportManager:

    def __init__(
        self,
        plugin_opts: Mapping[str, Any],
        outdir: str | PathLike,
        workdir: str | PathLike,
    ) -> None:
        self.outdir = Path(outdir) / "REPORTS"
        self.workdir = Path(workdir) / ".report-workdir"
        self.npm = get_config("npm", plugin_opts.get("report_npm"))
        self.nmdir = Path(get_config("nmdir", plugin_opts.get("report_nmdir")))
        self.extlibs = get_config("extlibs", plugin_opts.get("report_extlibs"))
        self.nobuild = get_config("nobuild", plugin_opts.get("report_nobuild"))
        self.has_reports = False

    def check_npm_and_setup_dirs(self) -> None:
        """Check if npm is available"""
        from .report_plugin import logger

        logger.debug("Checking npm and frontend dependencies ...")

        npm = shutil.which(self.npm)
        if npm is None:  # pragma: no cover
            logger.error(
                "Cannot find npm. Please install it or specify the path "
                "to npm by:"
            )
            logger.error("> pipen report config [--local] --npm <path/to/npm>")
            sys.exit(1)

        if not self.nmdir.is_dir():  # pragma: no cover
            logger.error("Invalid nmdir: %s", self.nmdir)
            logger.error(
                "Run `pipen report config [--local] --nmdir ...` to set it"
            )
            sys.exit(1)

        # check if frontend dependencies are installed
        if not (self.nmdir / "node_modules").is_dir():  # pragma: no cover
            logger.error("Frontend dependencies are not installed")
            logger.error("Run `pipen report update` to install them")
            sys.exit(1)

        pubdir = self.workdir / "public"
        if pubdir.is_symlink():
            pubdir.unlink()

        nmdir = self.workdir / "node_modules"
        if nmdir.is_symlink():
            nmdir.unlink()

        # Copy nmdir to workdir
        try:
            run_auto(
                str(self.nmdir),
                self.workdir,
                data=None if not self.extlibs else {"extlibs": self.extlibs},
                quiet=True,
                overwrite=True,
            )
        except Exception as e:  # pragma: no cover
            logger.error("Failed to copy frontend dependencies to workdir")
            logger.error("nmdir: %s", self.nmdir)
            logger.error("workdir: %s", self.workdir)
            logger.error("ERROR: %s", e)
            sys.exit(1)

        pubdir = self.workdir / "public"
        run_auto(str(pubdir), self.outdir, overwrite=True, quiet=True)
        shutil.rmtree(pubdir)
        pubdir.symlink_to(self.outdir)

        nmdir.symlink_to(self.nmdir / "node_modules")

    def _template_opts(self, template_opts) -> Mapping[str, Any]:
        """Template options for renderring
        Only supports liquid and jinja2
        """
        out = template_opts.copy()
        out["filters"] = {**template_opts.get("filters", {}), **FILTERS}
        return out

    def _rendering_data(self, proc: "Proc") -> Mapping[str, Any]:
        """Compute the data to render report template

        Args:
            proc: The process

        Returns:
            The data to render report template
        """

        def jobdata(job: Job) -> Mapping[str, Any]:
            """Get data from each job"""
            data = job.template_data["job"].copy()
            data.update(
                {
                    "in": job.template_data["in"],
                    "in_": job.template_data["in_"],
                    "out": job.template_data["out"],
                }
            )
            return data

        rendering_data = {
            "proc": proc,
            "envs": proc.envs,
            "jobs": [jobdata(job) for job in proc.jobs],
        }
        # first job
        rendering_data["job"] = rendering_data["jobs"][0]
        rendering_data["job0"] = rendering_data["jobs"][0]
        return rendering_data

    def _npm_run_build(self, *args: Any, **kwargs: Any) -> None:
        """Run a command and log the messages"""
        from .report_plugin import logger

        logfile = self.workdir / "pipen-report.log"
        kwargs.setdefault("_exe", self.npm)

        chars_to_log = " → "
        chars_to_error = "(!)"

        with open(logfile, "wt") as flog:
            flog.write("WORKING DIRECTORY:\n")
            flog.write("--------------------\n")
            flog.write(f"{self.workdir.resolve()}\n\n")

            try:
                for line in cmdy.run("run", "build", *args, **kwargs).iter(
                    cmdy.STDERR
                ):
                    flog.write(line)
                    if chars_to_log in line:
                        line = line.replace("\033[1m", "[bold]")
                        line = line.replace("\033[22m", "[/bold]")
                        line = line.replace("\033[39m", "")
                        logger.info(f"- {line.rstrip()}")
                    elif chars_to_error in line:  # pragma: no cover
                        line = line.replace("\033[1m", "[bold]")
                        line = line.replace("\033[22m", "[/bold]")
                        line = line.replace("\033[33m", "[red]")
                        line = line.replace("\033[39m", "[/red]")
                        logger.error(f"- {line.rstrip()}")
                        raise RuntimeError("Failed to build reports")
            except CmdyReturnCodeError as e:  # pragma: no cover
                flog.write(str(e))
                logger.error("Failed to build reports")
                logger.error("See %s for details", logfile)
            except RuntimeError as e:  # pragma: no cover
                logger.error(str(e))
                logger.error("See %s for details", logfile)
            else:
                logger.info("View the reports at %s", self.outdir)
                logger.info("Or run the following command to serve them:")
                logger.info("> pipen report serve -r %s", self.outdir.parent)

    def write_data(self, pipen: Pipen) -> None:
        """Write data to workdir"""
        datafile = self.workdir / "src" / "data.json"
        data = {
            "pipeline": {
                "name": pipen.name,
                "desc": pipen.desc,
            },
            "versions": version_str,
            "procs": [],
        }

        for proc in pipen.procs:
            if not (getattr(proc, "plugin_opts") or {}).get("report", False):
                continue

            data["procs"].append(
                {
                    "name": proc.name,
                    "desc": proc.desc,
                    "slug": slugify(proc.name),
                    "npages": 1,
                    "report_toc": True,
                    "order": (
                        (proc.plugin_opts or {}).get("report_order", 0) * 1000
                        + (proc.order or 0)
                    ),
                }
            )

        with datafile.open("w") as f:
            json.dump(data, f, indent=2)

    def _update_proc_meta(self, proc: Proc, npages: int) -> None:
        """Update the number of pages for a process"""
        datafile = self.workdir / "src" / "data.json"
        with datafile.open() as f:
            data = json.load(f)

        for p in data["procs"]:
            if p["name"] == proc.name:
                p["npages"] = npages
                p["desc"] = proc.desc
                p["report_toc"] = proc.plugin_opts.get("report_toc", True)
                break

        with datafile.open("w") as f:
            json.dump(data, f, indent=2)

    def render_proc_report(self, proc: Proc, status: str | bool) -> None:
        """Render the report template for a process

        Args:
            proc: The process
            status: The status of the process
        """
        from .report_plugin import logger

        if (
            not status
            or not proc.plugin_opts
            or not proc.plugin_opts.get("report", False)
        ):
            return

        self.has_reports = True

        proc.log("debug", "Rendering report ...", logger=logger)
        slug = slugify(proc.name)
        rendering_data = self._rendering_data(proc)

        # Render the report
        # in case it's a Path object
        report = str(proc.plugin_opts["report"])
        report_toc = proc.plugin_opts.get("report_toc", True)
        report_paging = proc.plugin_opts.get("report_paging", False)
        if report.startswith("file://"):
            report_tpl = Path(report[7:])
            if not report_tpl.is_absolute():
                base = get_base(
                    proc.__class__,
                    Proc,
                    report,
                    lambda klass: None
                    if klass.plugin_opts is None
                    else str(klass.plugin_opts.get("report", None)),
                )
                report_tpl = Path(inspect.getfile(base)).parent / report_tpl
            report = report_tpl.read_text()

        template_opts = self._template_opts(proc.template_opts)

        try:
            rendered = _render_file(
                proc.template,
                template_opts,  # type: ignore[arg-type]
                report,
                rendering_data,
            )
        except Exception as exc:  # pragma: no cover
            raise TemplateRenderingError(
                f"[{proc.name}] Failed to render report file."
            ) from exc

        # preprocess the rendered report and get the toc
        rendered_parts, toc = preprocess(
            rendered,
            self.outdir,
            report_toc,
            report_paging,
        )

        if len(toc) > 10 and not report_paging:  # pragma: no cover
            proc.log(
                "warning",
                "There are > 10 sections in the report, "
                "enable paging (`report_paging`) ?",
                logger=logger,
            )

        npages = len(rendered_parts)
        # Update npages in data.json
        self._update_proc_meta(proc, npages)

        for i, rendered_part in enumerate(rendered_parts):
            self._render_page(
                rendered=rendered_part,
                name=proc.name,
                slug=slug,
                page=i,
                toc=toc,
            )

    def _render_page(
        self,
        rendered: str,
        name: str,
        slug: str,
        page: int,
        toc: List[Mapping[str, Any]] | None,
    ):
        """Render a page of the report"""
        tpl_dir = self.nmdir.joinpath("src", "pages", "proc")
        if page == 0:
            dest_dir = self.workdir.joinpath("src", "pages", slug)
        else:
            dest_dir = self.workdir.joinpath("src", "pages", f"{slug}-{page}")

        run_auto(
            str(tpl_dir),
            dest_dir,
            overwrite=True,
            quiet=True,
            data={"name": name, "page": page},
        )
        rendered_report = dest_dir / "proc.svelte"

        if rendered_report.exists():
            rendered_report.unlink()
        rendered_report.write_text(rendered)

        with dest_dir.joinpath("toc.json").open("w") as f:
            json.dump(toc, f, indent=2)
        # if page == 0:
        #     with dest_dir.joinpath("toc.json").open("w") as f:
        #         json.dump(toc, f, indent=2)
        # else:
        #     # symlink the toc file for other pages
        #     tocfile = self.workdir.joinpath("src", "pages", slug, "toc.json")
        #     desttocfile = dest_dir.joinpath("toc.json")
        #     if desttocfile.exists() or desttocfile.is_symlink():
        #         desttocfile.unlink()
        #     desttocfile.symlink_to(tocfile.resolve())
        return rendered_report

    async def build(self, pipen: Pipen) -> None:
        """Build all reports

        Args:
            logger: The logger
        """
        from .report_plugin import logger

        if not self.has_reports:
            logger.info(
                "Skipping report generation, no process generates a report."
            )
            return

        logger.info("Building reports ...")
        self._npm_run_build(_cwd=self.workdir)
