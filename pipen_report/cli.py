"""Provide a command line interface for the pipen_report plugin"""
import re
import stat
import shutil
from pathlib import Path
from typing import Any, Mapping

import cmdy
import json5
from pyparam import Params, POSITIONAL
from pipen.cli import CLIPlugin

try:
    from functools import cached_property
except ImportError:  # pragma: no cover
    from cached_property import cached_property


def _parse_title(title: str, page: Path) -> str:
    """Parse title from a page"""
    if title and not title.startswith("<") and not title.endswith(">"):
        return title

    with page.open() as f:
        content = f.read()

    matched = re.search(r"<title>(.+?)</title>", content, re.IGNORECASE)
    if not matched:
        return page.stem

    return matched.group(1)


class PipenCliReport(CLIPlugin):
    """CLI utility for pipen-report"""
    from .versions import __version__

    name = "report"

    @cached_property
    def params(self) -> Params:
        """Add run command"""
        pms = Params(
            desc=self.__class__.__doc__,
        )
        pms._prog = f"{pms._prog} {self.name}"

        inject_cmd = pms.add_command(
            "inject",
            desc="Inject an independent HTML page into a report",
        )
        inject_cmd.add_param(
            "t,title",
            desc="The title of the page",
            default="<text of title tag>",
        )
        inject_cmd.add_param(
            "d,desc",
            desc="The description/subtitle of the page",
            default=""
        )
        inject_cmd.add_param(
            "r,reportdir",
            desc="The directory of the reports. Typically, `/path/to/REPORTS`",
            required=True,
        )
        inject_cmd.add_param(
            "jupyter",
            desc=(
                "Whether the HTML file is exported from jupyter notebook. ",
                "If so, allow the input/code block to collapse. ",
                "You don't need this if the HTML is exported by nbconvert "
                "with input controls.",
            ),
            default=False,
        )
        inject_cmd.add_param(
            POSITIONAL,
            desc="The path to the HTML file to inject",
            type='path',
            required=True,
        )

        update_cmd = pms.add_command(
            "up,update",
            desc="Update the frontend dependencies",
            help_on_void=False,
        )
        update_cmd.add_param(
            "npm",
            desc=[
                "Path to npm. Should be the same one as",
                "`config.plugin_opts.report_npm`",
            ],
            default="npm",
        )
        update_cmd.add_param(
            "nmdir",
            desc=[
                "Where is the frontend dependencies installed?",
                "If the package directory is writable, this option will "
                "be ignored. The frontend dependencies should have been "
                "installed in the package directory. If not, the frontend "
                "dependencies were installed in "
                "`config.plugin_opts.report_nmdir`. Then this option should "
                "be the same as the configuration.",
            ],
            default="~/.pipen-report",
        )
        return pms

    def exec_command(self, args: Mapping[str, Any]) -> None:
        """Execute the run command"""
        if args["__command__"] == "inject":
            self._inject(args.inject)
        if args["__command__"] in ("up", "update"):
            self._update(args.up)

    def _inject(self, args: Mapping[str, Any]) -> None:
        """Execute the inject command"""
        page = args[POSITIONAL]
        title = args["title"]
        desc = args["desc"]
        reportdir = Path(args["reportdir"])

        print("- Copying the html file over ...")
        injected_page = reportdir / page.name
        if injected_page.exists():
            injected_page = reportdir / f"{page.stem}_1{page.suffix}"
        shutil.copy2(page, injected_page)

        print("- Parsing title from the HTML page if not specified ...")
        title = _parse_title(title, injected_page)
        print(f"  Title: {title}")

        print("- Injecting", injected_page.name, "into index.html/js ...")
        indexjs = reportdir / "build" / "index.js"
        with indexjs.open() as f:
            content = f.read()
        matched = re.search(r"\[\{name:\".+?\"\}\]", content)
        if not matched:  # pragma: no cover
            raise ValueError(
                "Unable to find the process tile blocks in index.js. "
                "This tool might be out of date. "
                "Please contact the plugin author."
            )
        tileblock = json5.loads(matched.group(0))
        print(f"  Read {len(tileblock)} process blocks")
        tileblock.append(
            {"name": title, "slug": injected_page.stem, "desc": desc}
        )
        print(f"  Write {len(tileblock)} process blocks")
        with indexjs.open("w") as f:
            f.write(content.replace(matched.group(0), json5.dumps(tileblock)))
        print("  Injected successfully!")

        print("- Adding a 'Go-back' button to the injected page ...")
        with injected_page.open() as f:
            content = f.read()

        js_source = (
            '<script type="text/javascript">\n'
            f'   const is_jupyter = {str(args["jupyter"]).lower()};\n'
            '</script>\n'
            '<script type="text/javascript" src="./assets/inject.js">'
            '</script>\n'
        )
        content = content.replace('</head>', js_source + '</head>')
        with injected_page.open("w") as f:
            f.write(content)

        print("- Done!")

    def _update(self, args: Mapping[str, Any]) -> None:
        """Execute the update command"""
        pkgdir = Path(__file__).parent / "frontend"
        if not (pkgdir.stat().st_mode & stat.S_IWUSR):  # pragma: no cover
            nmdir = args["nmdir"]
            shutil.copy2(pkgdir.joinpath("package.json"), nmdir)
            shutil.copy2(pkgdir.joinpath("package-lock.json"), nmdir)
        else:
            nmdir = pkgdir

        print("WORKING DIRECTORY:", nmdir)
        print("")
        print("Running: npm update ...")
        for line in cmdy.run("update", _cwd=nmdir, _exe=args["npm"]).iter():
            print(line, end="")
