"""Provides preprocess"""

from __future__ import annotations

import math
import json
import hashlib
import re
import imagesize
from contextlib import suppress
from yunpath import AnyPath, CloudPath
from pathlib import Path
from typing import Any, List, Mapping, Sequence, Tuple, Union, Callable

from slugify import slugify

from .utils import cache_fun

RELPATH_TAGS = {
    "a": "href",
    "embed": "src",
    "img": "src",
    "Link": "href",
    "Image": ("src", "download"),
    "ImageLoader": "src",
    "DataTable": "src",
    "iframe": "src",
    "Iframe": "src",
    "Plotly": "src",
    "Download": "href",
}
H1_TAG = re.compile(r"(<h1.*?>.+?</h1>)", re.IGNORECASE | re.DOTALL)
H1_TAG_TEXT = re.compile(r"<h1.*?>(.+?)</h1>", re.IGNORECASE | re.DOTALL)
H2_TAG_TEXT = re.compile(r"<h2.*?>(.+?)</h2>", re.IGNORECASE | re.DOTALL)
TAG_RE = re.compile(r"<(?P<tag>[\w-]+)(?P<attrs>.*?)(?P<end>/?>)", re.DOTALL)

# noqa: E501
# <Image src="{{ job.in.inimg}}"
#   download={ {"src": "{{ job.in.inimg } }", "tip": "Download the high resolution format"} } />  # noqa: E501
# <Image src="{{ job.in.inimg}}"
#   download={ {"src": 1, "tip": "Download the high resolution format"} } />
# <Image src="{{ job.in.inimg}}"
#   download={ {"src": true, "tip": "Download the high resolution format"} } />
TAG_ATTR_RE = re.compile(
    r"""
    \s+(?P<attrname>[\w-]+)=
    (?:
        \"(?P<attrval>[^\"]*)\"
        |
        \{(?P<attrval2>.*?)\}
    )
    (?=\s+[\w-]+=|\s*$)
    """,
    re.VERBOSE | re.DOTALL,
)


def _preprocess_slash_h(
    source: str,
    index: int,
    page: int,
    kind: str,
    text: str | None = None,
) -> Tuple[str, Mapping[str, Any]]:
    """Preprocess headings (h1 or h2 tag) adding anchor links

    Add an anchor link after the tag and produce the toc dict

    For example, if the source is `<h1>Title 1</h1>`, the output will be
    `<h1>Title 1</h1><a id="prt-h1-1-title-1" class="pipen-report-toc-anchor"> </a>`

    Args:
        text: The string repr of the tag (e.g `<h1>Title 1</h1>`)
        index: The index of this kind of heading in the document
        page: Which page are we on?
        kind: h1 or h2
    """
    if text is None:
        matching = re.match(
            H1_TAG_TEXT if kind == "h1" else H2_TAG_TEXT,
            source,
        )
        text = matching.group(1)
    # prt: pipen-report-toc
    slug = f"prt-{kind}-{index}-{slugify(text)}"
    return (
        f'{source}<a id="{slug}" class="pipen-report-toc-anchor"> </a>',
        {"slug": slug, "text": text, "children": [], "page": page},
    )


def _path_to_url(path: str, basedir: Path, tag: str, logfn: Callable) -> str:
    """Convert a path to a url to be used in the html

    If the path is a relative path to basedir.parent, it will be converted
    to a relative path to basedir. Otherwise, it will be copied to a directory
    where the html file can access.

    Args:
        path: The path to be converted
        basedir: The base directory, usually, path/to/REPORTS
        tag: The tag name

    Returns:
        The url
    """
    path_passed = path
    apath = AnyPath(path)
    basedir_spec = getattr(basedir, "spec", basedir)
    try:
        path = apath.relative_to(basedir_spec.parent)
    except ValueError:
        # if it's a relative path, suppose it is pages
        # otherwise, it's a path to the results
        if isinstance(apath, CloudPath) or apath.is_absolute():
            # If we can't get the relative path, that means those files
            # are not exported, we need to copy the file to a directory
            # where the html file can access
            logfn(
                "warning",
                f"An external resource ({path}) detected for {tag}, "
                "copying it to REPORTS/data ...",
            )
            suffix = hashlib.sha256(path.encode()).hexdigest()[:8]
            path = f"data/{apath.stem}.{suffix}{apath.suffix}"

            (basedir / path).write_bytes(apath.read_bytes())

        # It's a relative path to the basedir, just use it
    else:
        # results are at uplevel dir
        path = f"../{path}"

    path_via_base = basedir_spec.joinpath(path)
    if isinstance(apath, CloudPath) and not path_via_base.joinpath(path).exists():
        # The outdir is on cloud, we need to download the file
        logfn("debug", f"Downloading {path_passed} for report building ...")
        path_via_base.parent.mkdir(parents=True, exist_ok=True)
        apath.download_to(path_via_base)

    return str(path)


def _preprocess_relpath_tag(
    matching: re.Match,
    basedir: Path,
    relpath_tags: Mapping[str, str | Sequence[str]] | None,
    logfn: Callable,
) -> str:
    """Preprocess tags with paths to be redirected"""
    pathval = None
    tag = matching.group("tag")
    rp_tags = RELPATH_TAGS.copy()
    rp_tags.update(relpath_tags or {})

    def repl_attrs(mattrs):
        nonlocal pathval
        attrname = mattrs.group("attrname")
        attrval = mattrs.group("attrval")
        attrval2 = mattrs.group("attrval2")

        if not (
            tag in rp_tags
            and (
                isinstance(rp_tags[tag], str)
                and attrname == rp_tags[tag]
                or attrname in rp_tags[tag]
            )
        ):
            return mattrs.group(0)

        if tag == "Image" and attrname == "download" and attrval2:
            av2 = json.loads(attrval2)
            if not isinstance(av2, list):
                av2 = [av2]

            for i, av in enumerate(av2):
                if isinstance(av, str):
                    av2[i] = {"src": _path_to_url(av, basedir, tag, logfn)}
                elif isinstance(av, dict):
                    av["src"] = _path_to_url(av["src"], basedir, tag, logfn)
            return f" {attrname}={{ {json.dumps(av2)} }}"

        pathval = attrval
        urlval = _path_to_url(attrval, basedir, tag, logfn)
        return f' {attrname}="{urlval}"'

    attrs = re.sub(TAG_ATTR_RE, repl_attrs, matching.group("attrs"))
    if pathval and tag == "Image" and ("width=" not in attrs or "height=" not in attrs):
        # Add width and height to Image tag
        with suppress(FileNotFoundError):  # pragma: no cover
            width, height = imagesize.get(pathval)
            if width > 0 and height > 0:
                if "width=" not in attrs:
                    attrs = f"{attrs.rstrip()} width={{{width}}} "
                if "height=" not in attrs:
                    attrs = f"{attrs.rstrip()} height={{{height}}} "

    return f"<{tag}{attrs}{matching.group('end')}"


def _preprocess_math(source: str) -> str:
    """Preprocess the Math tag

    A Math tag with latex content within it, which will be then encoded as base64 string
    with a data url.
    """
    def callback(matching):
        # encode the latex content as base64 string
        from base64 import b64encode

        tag = matching.group(1)
        latex = matching.group(2)
        return f"{tag}data:text/plain;base64,{b64encode(latex.encode()).decode()}</Math>"

    return re.sub(
        r"(<Math[^>]*?>)(.+?)</Math>",
        callback,
        source,
        flags=re.DOTALL,
    )


def _preprocess_markdown(source: str) -> str:
    """Preprocess Markdown tag

    A Markdown tag with markdown content within it, which will be then rendered
    as html.
    """
    from markdown import markdown

    def callback(matching):
        return markdown(matching.group(1))

    return re.sub(
        r"<Markdown>(.+?)</Markdown>",
        callback,
        source,
        flags=re.DOTALL,
    )


def _preprocess_section(
    section: str,
    h2_index: int,
    page: int,
    basedir: Path,
    relpath_tags: Mapping[str, str | Sequence[str]] | None,
    logfn: Callable,
) -> Tuple[str, List[Mapping[str, Any]]]:
    """Preprocesss a section of the document (between h1 tags)

    Args:
        section: The source code of the section
        h2_index: The start h2 index
        page: which page are we on?
        basedir: The base directory to save the relative path resources
    """
    section = _preprocess_math(section)
    section = _preprocess_markdown(section)
    # handle relpath tags
    section = re.sub(
        TAG_RE,
        lambda m: _preprocess_relpath_tag(m, basedir, relpath_tags, logfn),
        section,
    )

    toc = []

    def repl_h2(matching):
        nonlocal h2_index
        h2, toc_item = _preprocess_slash_h(
            matching.group(0),
            h2_index,
            page=page,
            kind="h2",
            text=matching.group(1),
        )
        toc.append(toc_item)
        h2_index += 1
        return h2

    return re.sub(H2_TAG_TEXT, repl_h2, section), toc


@cache_fun
def preprocess(
    text: str,
    basedir: Path,
    toc_switch: bool,
    paging: Union[bool, int],
    relpath_tags: Mapping[str, str | Sequence[str]] | None,
    logfn: Callable,
) -> Tuple[List[str], List[Mapping[str, Any]]]:
    """Preprocess the rendered report and return the toc dict

    This is not only faster than using a xml/html parsing library but also
    more compatible with JSX, as most python xml/html parser cannot handle
    JSX

    We use h1 and h2 tags to form TOCs. h1 and h2 tags have to be at the
    top level, which means you should not wrap them with any container in
    your svelte report template.

    h1 tag should be the first tag in the document after `</script>`. Otherwise
    those non-h1 tags will appear in all pages and the relative paths won't
    be parsed.

    Args:
        text: The rendered report
        basedir: The base directory
        toc_switch: Whether render a TOC?
        paging: Number of h1's in a page
            False to disable

    Returns:
        The preprocessed text and the toc dict
    """
    # split the text h1 tags
    splits = re.split(H1_TAG, text)
    # splits[0] is header
    len_sections = (len(splits) - 1) // 2
    if len_sections == 0:
        # no h1's
        section, _ = _preprocess_section(
            splits[0],
            h2_index=0,
            page=0,
            basedir=basedir,
            relpath_tags=relpath_tags,
            logfn=logfn,
        )
        return [section], []

    if not paging:
        paging = len_sections

    n_pages = math.ceil(len_sections / paging)
    pages = [[splits[0]] for _ in range(n_pages)]
    h2_index = 0
    toc = []
    for i, splt in enumerate(splits[1:]):
        page = i // 2 // paging
        if i % 2 == 0:  # h1
            h1, toc_item = _preprocess_slash_h(splt, index=i // 2, page=page, kind="h1")
            pages[page].append(h1)
            if toc_switch:
                toc.append(toc_item)

        else:
            section, toc_items = _preprocess_section(
                splt,
                h2_index=h2_index,
                page=page,
                basedir=basedir,
                relpath_tags=relpath_tags,
                logfn=logfn,
            )
            h2_index += len(toc_items)
            pages[page].append(section)
            if toc_switch:
                toc[-1]["children"].extend(toc_items)

    return ["".join(page) for page in pages], toc
