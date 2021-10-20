"""Render the template for each process and prepare for frontend compiling"""

import functools
import inspect
import json
import shutil
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import TYPE_CHECKING, Any, Iterable, List, Mapping, Type, Union

import cmdy
from pipen.exceptions import TemplateRenderingError
from slugify import slugify
from xqute.utils import a_mkdir, asyncify

from .filters import FILTERS
from .preproc import preprocess
from .versions import version_str

if TYPE_CHECKING:  # pragma: no cover
    from logging import LoggerAdapter
    from pipen import Proc, Pipen
    from pipen.job import Job
    from pipen.template import Template

FRONTEND_DIR = Path(__file__).parent / "frontend"
# prevent liquid/jinja2 to translate these tags
PRESERVED_TAGS = {
    "{#if": "<svelte:if>",
    "{#each": "<svelte:each>",
    "{#key": "<svelte:key>",
    "{#await": "<svelte:await>",
}


def _render_file(
    engine: "Template",
    engine_opts: Mapping[str, Any],
    source: str,
    render_data: Mapping[str, Any],
    save_to: Path = None,
) -> str:
    """Render a template file"""
    # make a shortcut to
    # import {...} from "carbon-components-svelte"
    # Just do a simple replace
    source = source.replace('"@@ccs"', '"carbon-components-svelte"')
    source = source.replace("'@@ccs'", "'carbon-components-svelte'")
    source = source.replace('from "@@"', 'from "../components"')
    source = source.replace("from '@@'", "from '../components'")

    for key, val in PRESERVED_TAGS.items():
        source = source.replace(key, val)

    rendered = engine(source, **engine_opts).render(render_data)

    for key, val in PRESERVED_TAGS.items():
        rendered = rendered.replace(val, key)

    if not save_to:
        return rendered

    save_to.write_text(rendered)
    return None


def _get_reporting_procs(pipen: "Pipen") -> Iterable[Type["Proc"]]:
    """Get the procs with reporting based on the report_order"""
    return sorted(
        (
            proc for proc in pipen.procs
            if (getattr(proc, "plugin_opts") or {}).get("report", False)
        ),
        key=lambda proc: (getattr(proc, "plugin_opts") or {}).get(
            "report_order", 0
        ),
    )


class ReportManager:

    """A couple of tasks for this class:

    1. Check if the requirements for frontend installed, particularly
       npm
    2. Gather the pipeline information, i.e. which processes we should generate
       reports for, and generate a pipeline.json for the frontend
    3. Add some useful filters, but only for the report templates
    4. Render templates for each process
    5. Prepare the frontend
    6. Compile the reports

    Args:
        procs: The processes
        outdir: The pipeline output directory
        workdir: The pipeline working directory
    """

    __slots__ = ("outdir", "workdir", "reports", "npm")

    def __init__(
        self,
        outdir: Path,
        workdir: Path,
        npm: str,
    ) -> None:
        """Constructor"""
        self.outdir = outdir / "REPORTS"
        # This directory can be used to debug at frontend
        self.workdir = workdir / ".report-workdir"

        self.reports: List[Path] = []
        self.npm = npm

    async def check_npm_and_setup_dirs(self):
        """Check prerequisites and setup directories"""
        npm = await asyncify(shutil.which)(self.npm)
        if npm is None:
            raise ValueError(
                "`nodejs` and `npm` are required to generate reports."
            )
        self.npm = npm

        await asyncify(shutil.rmtree)(self.outdir, ignore_errors=True)
        await a_mkdir(self.outdir, parents=True)
        # await asyncify(shutil.rmtree)(self.workdir, ignore_errors=True)
        # clean up workdir
        for logfile in self.workdir.glob("pipen-report*.log"):
            logfile.unlink()

        pubdir = self.workdir / "public"
        if pubdir.is_symlink():
            pubdir.unlink()

        # srcdir = self.workdir / "src"
        # Shouldn't remove all src, we need procs/*.svelte to see if
        # template rendering is cached

        # await asyncify(shutil.rmtree)(srcdir, ignore_errors=True)

        # await a_mkdir(self.workdir, exist_ok=True)
        # await asyncify(shutil.copytree)(FRONTEND_DIR / "src", srcdir)
        for subd in ("components", "entries", "layouts", "pages"):
            subdir = self.workdir / "src" / subd
            await asyncify(shutil.rmtree)(subdir, ignore_errors=True)
            await asyncify(shutil.copytree)(
                FRONTEND_DIR / "src" / subd, subdir
            )
        await a_mkdir(self.workdir / "src" / "procs", exist_ok=True)

        # create dist/public
        await asyncify(pubdir.symlink_to)(self.outdir)

        # create up data in public
        await a_mkdir(pubdir / "data", parents=True, exist_ok=True)
        # no directory in the data directory
        for dfile in pubdir.joinpath("data").glob("*"):
            dfile.unlink()

    async def prepare_frontend(
        self,
        pipen: "Pipen",
        logger: "LoggerAdapter",
    ) -> None:
        """Prepare files in frontend working directory"""
        logger.debug(
            "Preparing everything in workdir for npm run build to run ..."
        )
        logger.debug("- %s", self.workdir)
        # link package.json
        pjson = self.workdir / "package.json"
        if not pjson.exists():
            pjson.symlink_to(FRONTEND_DIR / "package.json")

        # see if frontend dependencies have been installed,
        # if not, install them
        await self._install_frontend_dependencies(
            Path(pipen.config.plugin_opts.report_nmdir).expanduser(), logger
        )

        # copy global css and favicon
        await asyncify(shutil.copytree)(
            FRONTEND_DIR / "public" / "assets",
            self.workdir / "public" / "assets",
        )

        proc0 = pipen.procs[0]()
        # render index page
        _render_file(
            proc0.template,
            proc0.template_opts,
            FRONTEND_DIR.joinpath("src", "index.tpl.svelte").read_text(),
            {
                "pipeline": json.dumps(
                    {"name": pipen.name, "desc": pipen.desc}
                ),
                "procs": json.dumps(
                    [
                        {
                            "name": proc().name,
                            "slug": slugify(proc().name),
                            "desc": proc().desc or "Undescribed",
                        }
                        for proc in _get_reporting_procs(pipen)
                    ]
                ),
                "versions": version_str,
            },
            self.workdir / "src" / "pages" / "index.svelte",
        )

        # render index.html
        _render_file(
            proc0.template,
            proc0.template_opts,
            FRONTEND_DIR.joinpath("public", "index.tpl.html").read_text(),
            {"pipeline": pipen},
            self.workdir / "public" / "index.html",
        )

        # render rollup.config.js for index
        _render_file(
            proc0.template,
            proc0.template_opts,
            FRONTEND_DIR.joinpath("rollup.config.js").read_text(),
            {"proc_slug": "index"},
            self.workdir / "rollup.config.index.js",
        )

    async def render_proc_report(
        self,
        proc: "Proc",
        status: Union[str, bool],
        logger: "LoggerAdapter",
    ) -> None:
        """Render the report template for a process

        Args:
            proc: The process
            status: The status of the process
        """
        if (
            not status
            or not proc.plugin_opts
            or not proc.plugin_opts.get("report", False)
        ):
            return

        rendering_data = self._rendering_data(proc)
        slug = rendering_data["proc_slug"]
        if slug == "index":
            logger.warning(
                "Process {%s} has a slugified name 'index', "
                "renaming to 'index_'",
                proc,
            )
            slug = "index_"

        # save all the rendered reports here
        # if report is given as a string (instead of a file)
        # also save it here for caching check
        report_srcdir = self.workdir / "src" / "procs"
        report_srcdir.mkdir(exist_ok=True)

        rendered_report = report_srcdir / f"{slug}.svelte"

        # in case it's a Path object
        report = str(proc.plugin_opts["report"])

        if report.startswith("file://"):
            report_tpl = Path(report[7:])
            if not report_tpl.is_absolute():
                report_tpl = (
                    Path(inspect.getfile(proc.__class__)).parent / report_tpl
                )
            report = report_tpl.read_text()
        else:
            report_tpl = report_srcdir / f"{slug}.tpl"
            if not report_tpl.is_file() or report_tpl.read_text() != report:
                report_tpl.write_text(report)

        template_opts = self._template_opts(proc.template_opts)

        # see if we can used the cached rendered report
        if (
            status == "cached"
            and rendered_report.exists()
            and rendered_report.stat().st_mtime + 1e-3
            >= report_tpl.stat().st_mtime
        ):
            proc.log(
                "debug",
                "Process cached, skip generating report.",
                logger=logger,
            )

        else:
            proc.log(
                "debug",
                "Rendering report ...",
                logger=logger,
            )
            # avoid future run to use it in case report file failed to compile
            if rendered_report.exists():
                rendered_report.unlink()

            try:
                rendered = _render_file(
                    proc.template,
                    template_opts,
                    report,
                    rendering_data,
                )
            except Exception as exc:
                raise TemplateRenderingError(
                    f"[{proc.name}] Failed to render report file."
                ) from exc

            # preprocess the rendered report and get the toc
            rendered, toc = await preprocess(rendered, self.outdir)

            _render_file(
                proc.template,
                template_opts,
                FRONTEND_DIR.joinpath("src", "toc.tpl.svelte").read_text(),
                {"toc": json.dumps(toc)},
                self.workdir / "src" / "procs" / f"{slug}.toc.svelte",
            )

            rendered_report.write_text(rendered)

        self.reports.append(str(rendered_report))

        # Generate page that connects the layout and the report
        _render_file(
            proc.template,
            template_opts,
            FRONTEND_DIR.joinpath("src", "page.tpl.svelte").read_text(),
            rendering_data,
            self.workdir / "src" / "pages" / f"{slug}.svelte",
        )

        # Generate entry js file for rollup to work with
        _render_file(
            proc.template,
            template_opts,
            FRONTEND_DIR.joinpath("src", "entry.tpl.js").read_text(),
            rendering_data,
            self.workdir / "src" / "entries" / f"{slug}.js",
        )

        # Generate html file
        _render_file(
            proc.template,
            template_opts,
            FRONTEND_DIR.joinpath("public", "proc.tpl.html").read_text(),
            rendering_data,
            self.workdir / "public" / f"{slug}.html",
        )

        # Render rollup.config.js
        _render_file(
            proc.template,
            template_opts,
            FRONTEND_DIR.joinpath("rollup.config.js").read_text(),
            rendering_data,
            self.workdir / f"rollup.config.{slug}.js",
        )

    async def build(self, pipen: "Pipen", logger: "LoggerAdapter") -> None:
        """Build all reports

        Args:
            logger: The logger
        """
        if not self.reports:
            logger.info(
                "Skipping report generation, "
                "no processes has a report template specified."
            )
            return

        forks = pipen.config.plugin_opts.report_forks
        if forks is None:
            forks = pipen.config.forks

        logger.info("Building reports using %s core(s) ...", forks)

        # builds = [slugify(proc.name) for proc in pipen.procs]
        builds = [Path(report_file).stem for report_file in self.reports]
        builds.append("index")
        with ProcessPoolExecutor(max_workers=forks) as executor:
            rcs = executor.map(
                functools.partial(
                    self._run_npm,
                    log_prefix="BUILDING",
                    _cwd=self.workdir,
                ),
                (
                    (
                        build,
                        "run",
                        "build",
                        f"rollup.config.{build}.js",
                    )
                    for build in builds
                ),
            )

        for i, rc in enumerate(rcs):
            if rc != 0:
                logfile = self.workdir / f"pipen-report.{builds[i]}.log"
                logger.error(
                    "Failed to build report (rc=%s): %s", rc, builds[i]
                )
                logger.error("See full log at %s", logfile)
        else:
            logger.info("Reports generated at: %s", self.outdir)

    async def _install_frontend_dependencies(
        self, interdir: Path, logger: "LoggerAdapter"
    ) -> None:
        """Install the frontend dependencies.

        Strategy is that:
        1. Check if we can install a copy in the srcdir
        2. If so, install one and symlink it to distdir
        3. Otherwise install one in interdir and symlink it to distdir
        """
        srcdir = FRONTEND_DIR / "node_modules"
        distdir = self.workdir / "node_modules"

        if distdir.is_dir():
            # reuse it
            return

        if srcdir.is_dir():
            await asyncify(distdir.symlink_to)(srcdir)
            return

        logger.info("Installing frontend dependencies ...")
        try:
            self._run_npm(
                "install",
                log_prefix="INSTALLATION",
                _cwd=FRONTEND_DIR,
            )
        except (
            cmdy.CmdyReturnCodeError,
            cmdy.CmdyExecNotFoundError,
            RuntimeError,
            PermissionError,
        ):
            logger.warning(
                "Failed to install a global copy of front dependencies, "
                "installing one in `plugin_opts.report_nmdir`: %s ...",
                interdir,
            )
            await asyncify(interdir.joinpath("package.json").symlink_to)(
                interdir / "package.json"
            )
            self._run_npm(
                "install",
                log_prefix="INSTALLATION",
                _cwd=interdir,
            )
            await asyncify(distdir.symlink_to)(interdir / "node_modules")
        else:
            await asyncify(distdir.symlink_to)(FRONTEND_DIR / "node_modules")

    def _template_opts(self, template_opts) -> Mapping[str, Any]:
        """Template options for renderring
        Only supports liquid and jinja2
        """
        filters = template_opts.get("filters", {}).copy()
        filters.update(FILTERS)
        out = {
            key: val for key, val in template_opts.items() if key != "filters"
        }
        out["filters"] = filters
        return out

    def _rendering_data(self, proc: "Proc") -> Mapping[str, Any]:
        """Compute the data to render report template

        Args:
            proc: The process

        Returns:
            The data to render report template
        """

        def jobdata(job: "Job") -> Mapping[str, Any]:
            """Get data from each job"""
            data = job.template_data["job"]
            data.update(
                {
                    "in": job.template_data["in"],
                    "out": job.template_data["out"],
                }
            )
            return data

        rendering_data = {
            "proc": proc,
            "proc_slug": slugify(proc.name),
            "envs": proc.envs,
            "jobs": [jobdata(job) for job in proc.jobs],
            "procs": json.dumps(
                [
                    {
                        "name": prc.name,
                        "slug": slugify(prc.name),
                        "desc": prc.desc or "Undescribed",
                    }
                    for prc in _get_reporting_procs(proc.pipeline)
                ]
            ),
            "versions": version_str,
        }
        # first job
        rendering_data["job"] = rendering_data["jobs"][0]
        rendering_data["job0"] = rendering_data["jobs"][0]
        return rendering_data

    def _run_npm(
        self,
        *args: Any,
        log_prefix: str,
        **kwargs: Any,
    ) -> int:
        """Run a command and log the messages"""
        if len(args) == 1 and isinstance(args[0], tuple):
            args = args[0]

        if len(args) == 1:
            name = args[0]
        else:
            name, *args = args

        logfile = self.workdir / f"pipen-report.{name}.log"
        kwargs.setdefault("_exe", self.npm)

        cmd = cmdy.run(*args, **kwargs, _raise=False)
        strcmd = cmd.strcmd
        with open(logfile, "at") as flog:
            flog.write("WORKING DIRECTORY:\n")
            flog.write("--------------------\n")
            flog.write(f"{self.workdir}\n\n")

            flog.write(f"{log_prefix} COMMAND:\n")
            flog.write("--------------------\n")
            flog.write(f"{strcmd}\n\n")

            flog.write(f"{log_prefix} STDOUT:\n")
            flog.write("--------------------\n")
            flog.write(cmd.stdout)

            flog.write("\n")
            flog.write(f"{log_prefix} STDERR:\n")
            flog.write("--------------------\n")
            flog.write(cmd.stderr)

        return cmd.rc
