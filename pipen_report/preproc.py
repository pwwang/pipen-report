"""Provides preprocess"""
import re
from pathlib import Path
import shutil
from typing import Any, Mapping, Match, Tuple
import hashlib

from pipen.utils import ignore_firstline_dedent
from slugify import slugify
from xqute.utils import asyncify

RELPATH_TAGS = {
    "a": "href",
    "img": "src",
    "Link": "href",
    "Image": "src",
    "ImageLoader": "src",
    "DataTable": "src",
    "PaginationDataTable": "src",
    "Download": "href",
}
TAG_RE = re.compile(r"<(?P<tagname>/?[\w_]+)(?P<tagattrs>.*?)/?>", re.DOTALL)
TAG_ATTR_RE = re.compile(
    r"\s+(?P<attrname>[\w_-]+)=\"(?P<attrval>[^\"]*)\"(?=\s|$)"
)


def _preprocess_slash_h(
    text: str,
    last_pos: int,
    match: Match,
) -> Tuple[str, Mapping[str, Any]]:
    """Preprocess </h1> or </h2>"""
    h_text = text[last_pos : match.start()].strip()
    slug = f"pipen-report-toc-{slugify(h_text)}"
    return f'<a id="{slug}"> </a>', {
        "slug": slug,
        "text": h_text,
        "children": [],
    }


async def _preprocess_relpath_tag(
    text: str,
    match: Match,
    tagname: str,
    basedir: Path,
) -> str:
    """Preprocess tags with paths to be redirected"""

    pos = 0
    # add '<DataTable '
    out = [text[match.start() : match.regs[2][0]]]
    tagattrs = match.group("tagattrs")
    # matches ' href="abc"'
    for mat in TAG_ATTR_RE.finditer(tagattrs):
        attrname = mat.group("attrname")

        if attrname != RELPATH_TAGS[tagname]:
            out.append(tagattrs[pos : mat.end()])
            pos = mat.end()
            continue

        pathval = Path(mat.group("attrval"))
        try:
            relpath = pathval.relative_to(basedir.parent)
        except ValueError:
            # If we can't get the relative path, that means those files
            # are not exported, we need to copy the file to a directory
            # where the html file can access
            suffix = hashlib.md5(str(pathval).encode()).hexdigest()[:8]
            relpath = Path("./data") / f"{pathval.name}.{suffix}"

            await asyncify(shutil.copyfile)(pathval, basedir / relpath)
        else:
            # results are at uplevel dir
            relpath = Path("..") / relpath

        out.append(f' {attrname}="{relpath}"')
        pos = mat.end()

    out.append(tagattrs[pos:])
    # add ' />'
    out.append(text[match.regs[2][1] : match.end()])
    return "".join(out)


async def preprocess(
    text: str,
    basedir: Path,
) -> Tuple[str, Mapping[str, Any]]:
    """Preprocess the rendered report and return the toc dict

    This is faster than using a xml/html parsing library.

    Args:
        text: The rendered report

    Returns:
        The preprocessed text and the toc dict
    """
    out = []
    out_append = out.append
    last_pos = 0
    toc = []
    for match in TAG_RE.finditer(text):
        tagname = match.group("tagname")
        if tagname in ("h1", "h2"):
            out_append(text[last_pos : match.end()])
            last_pos = match.end()
        # h1
        elif tagname == "/h1":
            out_elem, toc_elem = _preprocess_slash_h(text, last_pos, match)
            toc.append(toc_elem)
            out_append(out_elem)
            out_append(text[last_pos : match.end()])
            last_pos = match.end()
        # h2
        elif tagname == "/h2":
            if not toc:
                toc.append(
                    {
                        "slug": "pipen-report",
                        "text": "Report",
                        "children": [],
                    }
                )
            out_elem, toc_elem = _preprocess_slash_h(text, last_pos, match)
            toc[-1]["children"].append(toc_elem)
            out_append(out_elem)
            out_append(text[last_pos : match.end()])
            last_pos = match.end()
        # make path relative
        elif tagname in RELPATH_TAGS:
            out_elem = await _preprocess_relpath_tag(
                text,
                match,
                tagname,
                basedir,
            )
            out_append(out_elem)
            last_pos = match.end()

    out_append(text[last_pos:])
    return ignore_firstline_dedent("".join(out)), toc
