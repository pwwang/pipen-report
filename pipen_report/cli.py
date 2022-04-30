"""Provide a command line interface for the pipen_report plugin"""
import re
from pathlib import Path
import shutil
from typing import Any, Mapping

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

    matched = re.search(r"<h1.*?>(.+?)</h1>", content, re.IGNORECASE)
    if not matched:
        return page.stem

    return re.sub(r"<[^<]+?>", "", matched.group(1))


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
            default="<1st H1 of the HTML page>",
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
        return pms

    def exec_command(self, args: Mapping[str, Any]) -> None:
        """Execute the run command"""
        if args["__command__"] == "inject":
            self._inject(args.inject)

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
        if not matched:
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
