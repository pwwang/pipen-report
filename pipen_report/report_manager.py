from __future__ import annotations

import inspect
import json
import re
import shutil
import sys
import asyncio
import textwrap
import traceback
import functools
from contextlib import suppress
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, List, Mapping, MutableMapping, Type

from liquid import Liquid
from copier import run_copy
from panpath import CloudPath, PanPath
from xqute.path import SpecCloudPath, MountedPath
from pipen import Proc, ProcGroup
from pipen.defaults import ProcInputType, ProcOutputType
from pipen.exceptions import TemplateRenderingError
from pipen.template import TemplateLiquid, TemplateJinja2
from pipen.utils import get_base, desc_from_docstring, get_marked

from .filters import FILTERS
from .preprocess import preprocess
from .utils import (
    UnifiedLogger,
    get_config,
    logger,
    get_fspath,
    get_cloudpath,
    a_copy_all,
)
from .versions import version_str

if TYPE_CHECKING:
    from pipen import Pipen
    from pipen.job import Job
    from pipen.template import Template

ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


def _parse_imports(text: str) -> list[tuple[str, str]]:
    """Parse (specifier, statement) for import/export statements in a file

    For svelte files, only the <script> blocks are parsed. For plain js files,
    the whole text is parsed.
    """
    blocks = re.findall(r"<script[^>]*>(.*?)</script>", text, re.S)
    if not blocks:
        blocks = [text]

    out = []
    for block in blocks:
        block = re.sub(r"(?s)/\*.*?\*/", "", block)
        block = re.sub(r"(?m)//.*$", "", block)
        for m in re.finditer(
            # skip `export let/const/function/class` (no `from`), avoid matching
            # the whole block when an import appears after some `export let`
            r"(?ms)^\s*(?:import|export)\b(?:\s+(?!let\b|const\b|var\b|"
            r"function\b|class\b))[^'\"]*?from\s+['\"]([^'\"]+)['\"]\s*;?",
            block,
        ):
            out.append((m.group(1), m.group(0)))
        for spec in re.findall(r"(?m)^\s*import\s+['\"]([^'\"]+)['\"]\s*;?", block):
            out.append((spec, f"import '{spec}'"))
    return out


def _import_names(statement: str) -> list[str] | None:
    """Extract imported/exported names from an import/export statement

    Returns None for side-effect imports and `export *` statements.
    """
    stmt = statement.strip()
    if re.match(r"^(?:import\s+['\"]|export\s+\*)", stmt):
        return None
    names = []
    m = re.search(r"{([^}]*)}", stmt)
    if m:
        names = [n.strip() for n in m.group(1).split(",") if n.strip()]
    m = re.match(r"^(?:import|export)\s+(\w+)", stmt)
    if m:
        names.append(f"default as {m.group(1)}")
    return names


class NPMBuildingError(Exception):
    """Error when npm run build failed"""


class ReportManager:

    def __init__(
        self,
        plugin_opts: Mapping[str, Any],
        outdir: Path | CloudPath,
        workdir: Path | CloudPath,
        cachedir_for_cloud: str,
        page_chat: bool,
    ) -> None:
        """Initialize the report manager"""
        outdir = outdir / "REPORTS"

        # Make sure outdir and workdir are local paths
        if isinstance(outdir, SpecCloudPath):
            # modified by plugins like pipen-gcs
            self.outdir = MountedPath(
                get_fspath(outdir, cachedir_for_cloud), spec=outdir
            )
        elif isinstance(outdir, CloudPath):
            self.outdir = MountedPath(
                get_fspath(outdir, cachedir_for_cloud), spec=outdir
            )
        else:
            self.outdir = MountedPath(outdir)

        workdir = workdir / ".report-workdir"
        if isinstance(workdir, CloudPath):
            self.workdir = MountedPath(
                get_fspath(workdir, cachedir_for_cloud), spec=workdir
            )
        else:
            self.workdir = MountedPath(workdir)

        self.npm = get_config("npm", plugin_opts.get("report_npm"))
        self.nmdir = PanPath(get_config("nmdir", plugin_opts.get("report_nmdir")))
        self.extlibs = get_config("extlibs", plugin_opts.get("report_extlibs"))
        self.nobuild = get_config("nobuild", plugin_opts.get("report_nobuild"))
        self.no_collapse_pgs = plugin_opts.get("report_no_collapse_pgs") or []
        self.cachedir_for_cloud = cachedir_for_cloud
        self.page_chat = page_chat
        self.has_reports = False
        # Used to pass to the UI for rendering
        self.pipeline_data = None

        if isinstance(self.no_collapse_pgs, str):  # pragma: no cover
            self.no_collapse_pgs = [self.no_collapse_pgs]

    async def check_npm_and_setup_dirs(self) -> None:
        """Check if npm is available"""

        logger.info("Checking npm and frontend dependencies ...")

        npm = shutil.which(self.npm)
        if npm is None:  # pragma: no cover
            logger.error(
                "Cannot find npm. Please install it or specify the path to npm by:"
            )
            logger.error("$ pipen report config [--local] --npm <path/to/npm>")
            sys.exit(1)

        if not await self.nmdir.a_is_dir():  # pragma: no cover
            logger.error("Invalid nmdir: %s", self.nmdir)
            logger.error("Run `pipen report config [--local] --nmdir ...` to set it")
            sys.exit(1)

        # check if frontend dependencies are installed
        if not await (self.nmdir / "node_modules").a_is_dir():  # pragma: no cover
            logger.error("Frontend dependencies are not installed")
            logger.error("Run `pipen report update` to install them")
            sys.exit(1)

        await self.workdir.a_mkdir(parents=True, exist_ok=True)

        pubdir = self.workdir / "public"
        if await pubdir.a_is_symlink():
            await pubdir.a_unlink()

        nmdir = self.workdir / "node_modules"
        if await nmdir.a_is_symlink() or await nmdir.a_is_file():
            await nmdir.a_unlink()
        if await nmdir.a_exists():
            await nmdir.a_rmtree()

        exdir = self.workdir / "src" / "extlibs"
        with suppress(Exception):
            await exdir.a_rmtree()
        with suppress(Exception):
            await exdir.a_mkdir(parents=True, exist_ok=True)

        # Check if self.workdir is writable
        try:
            testfile = self.workdir / ".writetest"
            await testfile.a_write_text("test")
            await testfile.a_unlink()
        except Exception:  # pragma: no cover
            logger.error("The report workdir is not writable:")
            logger.error("  %s", self.workdir)
            traces = traceback.format_exc().splitlines()
            for trace in traces:
                logger.debug(trace)
            sys.exit(1)

        # Copy rollup config file to workdir
        rollup_config = await self.nmdir.joinpath(
            "rollup.config.js.jinja"
        ).a_read_text()
        rollup_config = Liquid(rollup_config, from_file=False).render(
            extlibs=self.extlibs
        )
        await self.workdir.joinpath("rollup.config.js").a_write_text(rollup_config)

        await self.nmdir.joinpath("public").a_copytree(self.outdir)
        await self.nmdir.joinpath("src").a_copytree(self.workdir / "src")
        await self.nmdir.joinpath("package.json").a_copy(self.workdir / "package.json")

        node_lockfile = self.nmdir.joinpath("package-lock.json")
        bun_lockfile = self.nmdir.joinpath("bun.lock")
        if not await bun_lockfile.a_exists() and not await node_lockfile.a_exists():
            logger.error("Frontend package lock file not found.")
            logger.error("Run `pipen report install` to create it.")
            sys.exit(1)

        if await bun_lockfile.a_exists():
            await bun_lockfile.a_copy(self.workdir / "bun.lock")
        else:
            await node_lockfile.a_copy(self.workdir / "package-lock.json")

        await pubdir.a_symlink_to(self.outdir.resolve(), True)
        await nmdir.a_symlink_to(self.nmdir / "node_modules", True)

        if self.extlibs:
            await exdir.joinpath(Path(self.extlibs).name).a_symlink_to(self.extlibs)

    def _template_opts(self, template_opts) -> Mapping[str, Any]:
        """Template options for renderring
        Only supports liquid and jinja2
        """
        out = template_opts.copy()
        out["filters"] = {**template_opts.get("filters", {}), **FILTERS}
        return out

    def _rendering_data(self, proc: Proc) -> Mapping[str, Any]:
        """Compute the data to render report template

        Args:
            proc: The process

        Returns:
            The data to render report template
        """

        def jobdata(job: Job) -> Mapping[str, Any]:
            """Get data from each job"""

            # Do not use the mounted paths, since we are not building
            # in the job execution environment
            indata = {}
            for inkey, intype in proc.input.type.items():

                if intype == ProcInputType.VAR or job.input[inkey] is None:
                    indata[inkey] = job.input[inkey]
                    continue

                if intype in (ProcInputType.FILE, ProcInputType.DIR):
                    indata[inkey] = job.input[inkey].spec

                if intype in (ProcInputType.FILES, ProcInputType.DIRS):
                    indata[inkey] = [f.spec for f in job.input[inkey]]

            outdata = {}
            for outkey, outtype in job._output_types.items():

                if outtype == ProcOutputType.VAR:
                    outdata[outkey] = job.output[outkey]
                    continue

                outdata[outkey] = job.output[outkey].spec

            data = job.template_data["job"].copy()
            data.update(
                {
                    "in": indata,
                    "in_": indata,
                    "out": outdata,
                }
            )
            return data

        rendering_data = {
            "proc": proc,
            "envs": proc.envs,
            "jobs": [jobdata(job) for job in sorted(proc.jobs, key=lambda j: j.index)],
        }
        # first job
        rendering_data["job"] = rendering_data["jobs"][0]
        rendering_data["job0"] = rendering_data["jobs"][0]

        return rendering_data

    async def _npm_run_build(
        self,
        cwd: Path,
        proc: str,
        ulogger: UnifiedLogger,
        force_build: bool,
        cached: bool,
        npages: int = 1,
        procgroup: str | None = None,
    ) -> None:
        """Run a command and log the messages

        proc is ProcGroup:Proc or Proc
        """
        logfile = self.workdir / "pipen-report.log"
        if proc == "_index":
            await logfile.a_write_text("")
            destfile = self.outdir.joinpath("pages", "_index.js")
            ini_datafile = self.workdir / "src" / "init_data.json"
            src_changed = (
                not await ini_datafile.a_exists()
                or not await destfile.a_exists()
                or (await ini_datafile.a_stat()).st_mtime
                > (await destfile.a_stat()).st_mtime
            )
            proc_or_pg = proc
        else:
            proc_or_pg = (
                proc
                if not procgroup
                or self.no_collapse_pgs is True
                or procgroup in self.no_collapse_pgs
                else f"{procgroup}/{proc}"
            )
            srcfile = self.workdir.joinpath("src", "pages", proc, "proc.svelte")
            destfile = self.outdir.joinpath("pages", f"{proc}.js")
            src_changed = (
                not await destfile.a_exists()
                or (await srcfile.a_stat()).st_mtime
                > (await destfile.a_stat()).st_mtime
            )

        if await destfile.a_exists() and not force_build and cached and not src_changed:
            if proc == "_index":
                ulogger.info("Home page cached, skipping report building")
                ulogger.info(f"- workdir: {self.workdir}")
            else:
                ulogger.info("Report pages cached, skipping building.")

            return

        ulogger.debug(
            f"Destination exists: {await destfile.a_exists()}; "
            f"force_build: {force_build}; "
            f"cached: {cached}; "
            f"src_changed: {src_changed}"
        )
        if proc_or_pg == "_index":
            ulogger.info(f"Building home page (workdir={self.workdir}) ...")
        elif proc_or_pg == "_vendor":
            ulogger.info("Building shared chunks ...")
        elif npages == 1:
            ulogger.info("Building report ...")
        else:
            ulogger.info(f"Building report ({npages} pages) ...")

        chars_to_error = "(!)"
        errors_to_ignore = {
            # "(!) Unresolved dependencies":
            # "May be ignored if you are using external libraries",
            # "(!) Circular dependency":
            # "Brought by page-chat.js, will be ignored",
            # "(!) Use of eval is strongly discouraged":
            # "Brought by page-chat.js, will be ignored",
        }
        errored = False

        async with logfile.a_open("a") as flog:
            await flog.write("\n")
            await flog.write(f"# BUILDING {proc_or_pg} ...\n")
            await flog.write("----------------------------------------\n")

            try:
                p = await asyncio.create_subprocess_exec(
                    self.npm,
                    "run",
                    "build",
                    "--",
                    f"--configProc={proc_or_pg}",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.STDOUT,
                    cwd=str(cwd),
                )
                async for line in p.stdout:
                    line = line.decode()
                    logline = ansi_escape.sub("", line).rstrip()
                    # src/pages/_index/index.js → public/index/index.js
                    await flog.write(ansi_escape.sub("", line))
                    if " → " in logline and logline.startswith("src/pages/"):
                        ulogger.info(f"- {logline.split(' → ')[0]}")

                    if logline.startswith(chars_to_error):  # pragma: no cover
                        if logline in errors_to_ignore:
                            ulogger.warning(
                                f"  {logline} ({errors_to_ignore[logline]})"
                            )
                        else:
                            ulogger.error(f"  {logline}")
                            errored = True

                    if errored:  # pragma: no cover
                        # Early stop
                        p.terminate()
                        p.kill()
                        raise NPMBuildingError

                if await p.wait() != 0:  # pragma: no cover
                    raise NPMBuildingError

            except Exception as e:  # pragma: no cover
                with suppress(FileNotFoundError):
                    await destfile.a_unlink()

                if not isinstance(e, NPMBuildingError):
                    await flog.write(str(e))
                    for line in str(e).splitlines():
                        ulogger.error(f"  {line.rstrip()}")

                ulogger.error(f"(!) Failed. See: {logfile}")
                sys.exit(1)

    async def init_pipeline_data(self, pipen: Pipen) -> None:
        """Write data to workdir"""
        self.pipeline_data = {
            "pipeline": {
                "name": pipen.name,
                "desc": pipen.desc,
            },
            "page_chat": self.page_chat,
            "versions": version_str,
            "entries": [
                # Either a proc or a procgroup
            ],
        }

        procgroups = {}
        for i, proc in enumerate(pipen.procs):
            if not (getattr(proc, "plugin_opts") or {}).get("report", False):
                continue

            entry = {
                "name": proc.name,
                "desc": proc.desc or desc_from_docstring(proc, Proc),
                "npages": 1,
                "report_toc": True,
                "order": ((proc.plugin_opts or {}).get("report_order", 0) * 1000 + i),
            }

            pg = proc.__meta__["procgroup"]
            if self.no_collapse_pgs is True or (
                pg and pg.name in self.no_collapse_pgs
            ):  # pragma: no cover
                pg = None

            if pg and pg.name not in procgroups:
                procgroups[pg.name] = {
                    "name": pg.name,
                    "desc": desc_from_docstring(pg.__class__, ProcGroup),
                    "order": entry["order"],
                    "procs": [entry],
                }
                self.pipeline_data["entries"].append(procgroups[pg.name])
            elif pg:
                procgroups[pg.name]["order"] = min(
                    procgroups[pg.name]["order"], entry["order"]
                )
                procgroups[pg.name]["procs"].append(entry)
            else:
                self.pipeline_data["entries"].append(entry)

        self.pipeline_data["entries"].sort(key=lambda x: x["order"])

        # Write the initial data to check if home page is cached
        datafile = self.workdir / "src" / "init_data.json"
        if (
            not await datafile.a_exists()
            or json.loads(await datafile.a_read_text()) != self.pipeline_data
        ):
            await datafile.a_write_text(json.dumps(self.pipeline_data, indent=2))

    async def collect_vendor_imports(self, pipen: Pipen) -> None:
        """Collect node_modules imports used by all report pages

        Walks the page chrome and the `<script>` blocks of all report templates,
        following relative/aliased imports into local files, keeping the
        import/export statements of node_modules modules. These are the inputs
        for the shared chunks build (--configProc=_vendor).
        """
        statements: list[str] = []
        visited: set[str] = set()
        self._vendor_module_imports: list[tuple[str, str]] = []
        # A single report page has nothing to share; skip the shared build and
        # let the page compile its own node_modules (see rollup.config)
        self._vendor_needed = (
            sum(
                1
                for proc in pipen.procs
                if (getattr(proc, "plugin_opts") or {}).get("report", False)
            )
            > 1
        )
        if not self._vendor_needed:
            return
        src = self.workdir / "src"

        # Page chrome
        start_files = list((src / "layouts").glob("*.svelte"))
        start_files += [
            src / "components" / "PageNavButton.svelte",
            src / "pages" / "proc" / "index.svelte",
            src / "pages" / "_index" / "index.svelte",
        ]
        for path in start_files:
            if await path.a_exists():
                await self._walk_imports(path, visited, statements)

        # Report templates of all processes
        for proc in pipen.procs:
            report = (getattr(proc, "plugin_opts") or {}).get("report", False)
            if not report:
                continue

            report = str(report)
            if report.startswith("file://"):
                report_tpl = PanPath(report[7:])
                if not report_tpl.is_absolute():
                    base = get_base(
                        proc.__class__,
                        Proc,
                        report,
                        lambda klass: (
                            None
                            if klass.plugin_opts is None
                            else str(klass.plugin_opts.get("report", None))
                        ),
                    )
                    report_tpl = PanPath(inspect.getfile(base)).parent / report_tpl
                report = await report_tpl.a_read_text()

            # Relative imports in a template resolve against the rendered page dir
            await self._walk_text(
                report, src / "pages" / proc.name, visited, statements
            )

        # Same module is imported with different quotes/whitespace in
        # different files; merge names per specifier so the union input has
        # one statement per specifier (no duplicate bindings).
        merged: dict[str, list[str]] = {}
        others: list[str] = []
        seen_specs: set[str] = set()
        for stmt in statements:
            names = _import_names(stmt)
            if names is None:
                # side-effect imports / `export *` stay as-is, once per module
                m = re.match(r"(?s)^.*?from\s+['\"]([^'\"]+)['\"]", stmt)
                key = m.group(1) if m else stmt
                if key not in seen_specs:
                    seen_specs.add(key)
                    others.append(stmt)
                continue
            # statements can span multiple lines (`import {\n a,\n b\n } from 'x'`)
            spec = re.match(r"(?s)^.*?from\s+['\"]([^'\"]+)['\"]\s*;?\s*$", stmt)
            if spec is None:  # pragma: no cover
                continue
            spec = spec.group(1)
            for name in names:
                if name not in merged.setdefault(spec, []):
                    merged[spec].append(name)
        # The pages import the carbon components by subpath (the
        # optimizeImports preprocess rewrites barrel imports to subpaths), so
        # the shared build must provide an entry per subpath module
        merged = await self._expand_carbon_barrels(merged)

        def emit_names(names: list[str]) -> str:
            return ", ".join(
                sorted(
                    {"default" if n.startswith("default as ") else n for n in names}
                )
            )

        # Modules imported by subpath (carbon components) and any module with
        # a `default` import get their own entry file: the pages import them by
        # the vendor path, and only an entry chunk exports exactly the names
        # the page asks for (`default`) — shared chunks export the module's
        # internal variable name instead. Everything else is chunked per
        # package and re-exported from the main entry.
        def has_default(names: list[str]) -> bool:
            return any(n == "default" or n.startswith("default as ") for n in names)

        def is_carbon(spec: str) -> bool:
            return spec.split("/")[0] in ("carbon-components-svelte", "carbon-icons-svelte")

        self.vendor_imports = [
            f"export {{ {emit_names(names)} }} from '{spec}'"
            for spec, names in merged.items()
            if not is_carbon(spec) and not has_default(names)
        ] + others
        self._vendor_module_imports = [
            (spec, emit_names(names))
            for spec, names in merged.items()
            if is_carbon(spec) or has_default(names)
        ]
        # The svelte compiler injects `svelte/internal` and
        # `svelte/internal/disclose-version` imports into every compiled
        # component; they never appear in the sources, so add them explicitly
        if any(spec == "svelte" for spec in merged):
            self.vendor_imports += [
                "export * from 'svelte/internal'",
                "export * from 'svelte/internal/disclose-version'",
            ]
        self._vendor_changed = await self._write_vendor_input()

    async def _expand_carbon_barrels(
        self, merged: dict[str, list[str]]
    ) -> dict[str, list[str]]:
        """Replace carbon barrel imports with per-module subpath imports

        The pages import the carbon components by subpath (the
        optimizeImports preprocess rewrites barrel imports to subpaths), so
        the shared build must provide an entry per subpath module. Map each
        name imported from the barrel to the subpath module that exports it.
        The barrel entry itself stays: the pages' own `$ccs` alias imports are
        not rewritten by optimizeImports and import the barrel directly.
        """
        out: dict[str, list[str]] = {}
        nm = Path(self.workdir / "node_modules")
        for spec, names in merged.items():
            if spec not in ("carbon-components-svelte", "carbon-icons-svelte"):
                out[spec] = names
                continue
            out[spec] = names
            barrel = next(
                (
                    p
                    for p in (
                        nm / spec / "src" / "index.js",
                        nm / spec / "lib" / "index.js",
                    )
                    if p.is_file()
                ),
                None,
            )
            if barrel is None:
                out[spec] = names
                continue
            prefix = str(barrel.relative_to(nm)).rsplit("/", 1)[0]
            byname: dict[str, tuple[str, str]] = {}
            for line in barrel.read_text().splitlines():
                m = re.match(
                    r'export\s*\{([^}]+)\}\s*from\s*["\']([^"\']+)["\']', line
                )
                if not m or not m.group(2).startswith("./"):
                    continue
                sub = f"{prefix}/{m.group(2)[2:]}"
                for part in m.group(1).split(","):
                    part = part.strip()
                    if not part:
                        continue
                    if part.startswith("default as "):
                        byname[part[11:].strip()] = (sub, "default")
                    else:
                        byname[part] = (sub, part)
            for name in names:
                mapped = byname.get(name)
                if mapped:
                    sub, export_name = mapped
                    if export_name not in out.setdefault(sub, []):
                        out[sub].append(export_name)
                else:
                    logger.warning(
                        "Cannot map %s.%s to a subpath module in the shared "
                        "chunk build; pages importing it by subpath may 404",
                        spec,
                        name,
                    )
                    out.setdefault(spec, []).append(name)
        return out

    async def _walk_imports(
        self,
        path: Path,
        visited: set[str],
        statements: list[str],
    ) -> None:
        """Recursively collect node_modules import statements from a file"""
        # Use plain pathlib.Path: xqute's MountedPath loses `_spec` on
        # resolve()/glob()/parent, breaking hashing. The workdir is local.
        path = Path(path)
        key = str(path.resolve())
        if key in visited:
            return
        visited.add(key)
        await self._walk_text(path.read_text(), path.parent, visited, statements)

    async def _walk_text(
        self,
        text: str,
        basedir: Path,
        visited: set[str],
        statements: list[str],
    ) -> None:
        """Collect node_modules import statements from template/report text"""
        src = Path(self.workdir / "src")
        for spec, line in _parse_imports(text):
            target: Path | None = None
            if spec.startswith("."):
                target = self._resolve_rel(basedir, spec)
            elif spec.startswith("$"):
                # alias targets are written for page dirs (src/pages/<proc>/),
                # resolving to the same absolute dirs here
                m = re.match(r"^\$(libs?|components?|layouts?|extlibs)(?:/(.+))?$", spec)
                if m:
                    alias, sub = m.group(1), m.group(2)
                    if alias == "extlibs":
                        if self.extlibs:
                            target = self._resolve_rel(
                                src / "extlibs" / Path(self.extlibs).name,
                                sub or "",
                            )
                    else:
                        base = src / {
                            "lib": "components",
                            "libs": "components",
                            "component": "components",
                            "components": "components",
                            "layout": "layouts",
                            "layouts": "layouts",
                        }[alias]
                        target = self._resolve_rel(base, sub or "")
                elif spec == "$ccs":
                    statements.append(
                        line.replace(f"'{spec}'", "'carbon-components-svelte'")
                    )
                    continue
                else:
                    logger.warning(
                        "Unknown import alias in report: %s (skipped for "
                        "shared chunks)",
                        spec,
                    )
                    continue
            else:
                statements.append(line)
                continue

            if target is None:
                logger.warning(
                    "Cannot resolve import in report: %s from %s (skipped for "
                    "shared chunks)",
                    spec,
                    basedir,
                )
                continue

            await self._walk_imports(target, visited, statements)

    def _resolve_rel(self, dirpath: Path, spec: str) -> Path | None:
        """Resolve a relative import specifier to a local file"""
        p = dirpath.joinpath(spec)
        for cand in (p, p.with_name(p.name + ".js"), p.with_name(p.name + ".svelte")):
            if cand.is_file():
                return cand
        for cand in (p.joinpath("index.js"), p.joinpath("index.svelte")):
            if cand.is_file():
                return cand
        return None

    async def _write_vendor_input(self) -> bool:
        """Write the collected node_modules imports to src/vendor/

        The main entry re-exports the per-package imports; each module the
        pages import by subpath or by `default` gets its own tiny entry file
        in src/vendor/modules/, named by the vendor path the page maps it to
        (a single entry module can re-export `default` only once, so multiple
        default-exporting modules need separate entries).

        Returns True if anything was changed.
        """
        files: dict[str, str] = {
            "index.js": "\n".join(self.vendor_imports) + "\n",
            **{
                f"modules/{self._vendor_key(spec)}.js": (
                    f"export {{ {names} }} from '{spec}'\n"
                )
                for spec, names in self._vendor_module_imports
            },
        }
        changed = False
        for name, text in files.items():
            path = self.workdir / "src" / "vendor" / name
            if await path.a_exists() and await path.a_read_text() == text:
                continue
            await path.parent.a_mkdir(parents=True, exist_ok=True)
            await path.a_write_text(text)
            changed = True
        return changed

    @staticmethod
    def _vendor_key(spec: str) -> str:
        """The vendor path key of a module entry, matching the rollup config"""
        if spec.startswith(("carbon-components-svelte/", "carbon-icons-svelte/")):
            return re.sub(r"\.(svelte|js|mjs)$", "", spec)
        return spec.split("/")[0]

    async def build_vendor_chunks(self, ulogger: UnifiedLogger) -> None:
        """Build the shared vendor chunks for the whole report"""
        if not self._vendor_needed:
            # Single report page: it compiles its own node_modules, so drop
            # any stale shared chunks and keep index.html's static
            # `./pages/index.css` link resolving (to an empty file)
            ulogger.info("Only one report page, skipping shared chunk build.")
            for base in (self.workdir / "public" / "pages", self.outdir / "pages"):
                for rel in ("vendor", "_carbon", "_pkg"):
                    d = base / rel
                    if await d.a_exists():
                        await d.a_rmtree()
                css = base / "index.css"
                if not await css.a_exists():
                    await css.parent.a_mkdir(parents=True, exist_ok=True)
                    await css.a_write_text("")
            return
        if not self._vendor_changed and await (
            self.outdir / "pages" / "vendor"
        ).a_is_dir():
            ulogger.info("Shared chunks cached, skipping building.")
            return
        # The build output keeps stale files between runs (renamed/removed
        # module entries); drop the whole shared-chunk area first
        for base in (self.workdir / "public" / "pages", self.outdir / "pages"):
            for rel in ("vendor", "_carbon", "_pkg"):
                d = base / rel
                if await d.a_exists():
                    await d.a_rmtree()
        await self._npm_run_build(
            cwd=self.workdir,
            proc="_vendor",
            ulogger=ulogger,
            force_build=True,
            cached=False,
        )

    async def _update_proc_meta(self, proc: Proc, npages: int) -> None:
        """Update the number of pages for a process"""

        runinfo_sess_file = proc.workdir / "0" / "job.runinfo.session"
        runinfo_time_file = proc.workdir / "0" / "job.runinfo.time"
        runinfo_dev_file = proc.workdir / "0" / "job.runinfo.device"

        runinfo_sess = (
            await runinfo_sess_file.a_read_text()
            if await runinfo_sess_file.a_exists()
            else (
                "pipen-runinfo plugin not enabled or language not supported "
                "for saving session information."
            )
        )
        runinfo_time = (
            textwrap.dedent(await runinfo_time_file.a_read_text())
            if await runinfo_time_file.a_exists()
            else "pipen-runinfo plugin not enabled."
        )
        runinfo_dev = (
            await runinfo_dev_file.a_read_text()
            if await runinfo_dev_file.a_exists()
            else "pipen-runinfo plugin not enabled."
        )
        to_update = {
            "npages": npages,
            "desc": proc.desc,
            "report_toc": proc.plugin_opts.get("report_toc", True),
            "runinfo": {
                "session": runinfo_sess,
                "time": runinfo_time,
                "device": runinfo_dev,
            },
        }

        pg = proc.__meta__["procgroup"]
        if self.no_collapse_pgs is True or (
            pg and pg.name in self.no_collapse_pgs
        ):  # pragma: no cover
            pg = None

        for entry in self.pipeline_data["entries"]:
            if pg and entry["name"] == pg.name:
                for p in entry["procs"]:
                    if p["name"] == proc.name:
                        p.update(to_update)
                        break
                break
            elif entry["name"] == proc.name:
                entry.update(to_update)
                break

    async def _render_file(
        self,
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

        eng = engine(source, **engine_opts)
        # A better way to handle missing includes/imports
        # if the included file is in the cloud path, download it first
        missed_files = set()
        while True:
            try:
                return eng.render(render_data)
            except FileNotFoundError as e:
                missed_file = str(e).split(": '")[1][:-1]
                if missed_file in missed_files:  # pragma: no cover
                    raise e

                missed_files.add(missed_file)
                cloud_file = get_cloudpath(missed_file, self.cachedir_for_cloud)
                if cloud_file is not None:
                    ppath = PanPath(cloud_file)
                    lpath = PanPath(missed_file)
                    await a_copy_all(ppath, lpath, self.cachedir_for_cloud)
                else:
                    raise e

    async def render_proc_report(self, proc: Proc):
        """Render the report template for a process

        Args:
            proc: The process
            status: The status of the process
        """
        rendering_data = self._rendering_data(proc)

        # Render the report
        # in case it's a Path object
        report = str(proc.plugin_opts["report"])
        report_toc = proc.plugin_opts.get("report_toc", True)
        report_paging = proc.plugin_opts.get("report_paging", False)
        report_relpath_tags = proc.plugin_opts.get("report_relpath_tags", None) or {}
        if report.startswith("file://"):
            report_tpl = PanPath(report[7:])
            if not report_tpl.is_absolute():
                base = get_base(
                    proc.__class__,
                    Proc,
                    report,
                    lambda klass: (
                        None
                        if klass.plugin_opts is None
                        else str(klass.plugin_opts.get("report", None))
                    ),
                )
                report_tpl = PanPath(inspect.getfile(base)).parent / report_tpl
            report = await report_tpl.a_read_text()

        template_opts = self._template_opts(proc.template_opts)

        try:
            rendered = await self._render_file(
                proc.template,
                template_opts,  # type: ignore[arg-type]
                report,
                rendering_data,
            )
        except Exception as exc:  # pragma: no cover
            raise TemplateRenderingError(
                f"[{proc.name}] Failed to render report file."
            ) from exc

        # How the pipeline/proc is run
        # If mounted_outdir is not None, it means the pipeline is run remotely
        # The spec paths are paths that mounted inside the remote environment
        # They may not be working on this local system
        # `_export_dir`/`workdir` are SpecPaths for remote schedulers
        # (with `mounted` set), plain paths otherwise (pipen >= 1.2)
        mounted_outdir = getattr(proc._export_dir, "mounted", None)
        mounted_workdir = getattr(proc.workdir, "mounted", None)
        run_meta = {
            "outdir": self.outdir,
            "workdir": self.workdir,
            "mounted_outdir": (
                mounted_outdir
                if mounted_outdir is not None and mounted_outdir.is_mounted()
                else None
            ),
            "mounted_workdir": (
                mounted_workdir
                if mounted_workdir is not None and mounted_workdir.is_mounted()
                else None
            ),
        }

        # preprocess the rendered report and get the toc
        rendered_parts, toc = await preprocess(
            rendered,
            run_meta,
            report_toc,
            report_paging,
            report_relpath_tags,
            cachedir_for_cloud=self.cachedir_for_cloud,
            logfn=lambda *args, **kwargs: proc.log(*args, **kwargs, logger=logger),
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
        await self._update_proc_meta(proc, npages)

        for i, rendered_part in enumerate(rendered_parts):
            await self._render_page(
                rendered=rendered_part,
                name=proc.name,
                page=i,
                toc=toc,
            )

        return npages

    async def _render_page(
        self,
        rendered: str,
        name: str,
        page: int,
        toc: List[Mapping[str, Any]] | None,
    ) -> Path:
        """Render a page of the report"""
        tpl_dir = self.nmdir.joinpath("src", "pages", "proc")
        if page == 0:
            dest_dir = self.workdir.joinpath("src", "pages", name)
        else:
            dest_dir = self.workdir.joinpath("src", "pages", f"{name}-{page}")

        run_copy_partial = functools.partial(
            run_copy,
            str(tpl_dir),
            dest_dir,
            overwrite=True,
            quiet=True,
            data={"name": name, "page": page},
            skip_if_exists=["proc.svelte"],
        )
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, run_copy_partial)
        rendered_report = dest_dir / "proc.svelte"

        await dest_dir.joinpath("toc.json").a_write_text(json.dumps(toc, indent=2))

        if (
            not await rendered_report.a_exists()
            or await rendered_report.a_read_text() != rendered
        ):
            await rendered_report.a_write_text(rendered)

        return rendered_report

    async def build(
        self,
        proc: Proc | str,
        nobuild: bool,
        force_build: bool,
        cached: bool = False,
    ) -> None:
        """Build report for a process

        Args:
            proc: The process
            nobuild: Don't build the report
            cached: Whether the process is cached
        """
        ulogger = UnifiedLogger(logger, proc)

        if proc == "_index":
            if nobuild:  # pragma: no cover
                ulogger.debug("`report_nobuild` is True, skipping building home page.")
            else:
                await self._npm_run_build(
                    cwd=self.workdir,
                    proc="_index",
                    ulogger=ulogger,
                    force_build=force_build,
                    cached=cached,
                )

            return

        npages = await self.render_proc_report(proc)

        datafile = self.workdir / "src" / "data.json"
        await datafile.a_write_text(json.dumps(self.pipeline_data, indent=2))

        if nobuild or self.nobuild:  # pragma: no cover
            ulogger.debug("`report_nobuild` is True, skipping building report.")
            return

        procgroup = get_marked(proc, "procgroup")
        await self._npm_run_build(
            cwd=self.workdir,
            proc=proc.name,
            ulogger=ulogger,
            force_build=force_build,
            cached=cached,
            npages=npages,
            procgroup=procgroup.name if procgroup else None,
        )

    async def sync_reports(self, logfn: Callable | None = None) -> None:
        """Sync the reports to the cloud output directory if needed"""

        if hasattr(self.outdir, "spec") and isinstance(self.outdir.spec, CloudPath):
            if logfn:
                logfn("info", "Syncing reports to cloud ...", logger=logger)
            else:
                logger.info("Syncing reports to cloud ...")
                logger.info(f" {self.outdir}")
                logger.info(f" → {self.outdir.spec}")

            await self.outdir.a_copytree(self.outdir.spec)
