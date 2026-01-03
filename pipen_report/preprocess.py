"""Provides preprocess"""

from __future__ import annotations

import math
import json
import hashlib
import re
from pathlib import Path
from contextlib import suppress
from panpath import PanPath, CloudPath
from typing import Any, List, Mapping, Sequence, Tuple, Union, Callable

from slugify import slugify

from .utils import get_fspath, get_imagesize, a_re_sub, a_copy_all, cache_fun

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


async def _path_to_url(
    path: str,
    run_meta: Mapping[str, Any],
    tag: str,
    cachedir_for_cloud: str,
    logfn: Callable,
) -> Tuple[str, str | Path | CloudPath]:
    """Convert a path to a url to be used in the html

    If the path is a relative path to basedir.parent, it will be converted
    to a relative path to basedir. Otherwise, it will be copied to a directory
    where the html file can access.

    Args:
        path: The path to be converted, usually from the attribute value of a tag
        run_meta: The run meta paths
        tag: The tag name

    Returns:
        The url and the content-accessible path.
    """
    # HTTP/HTTPS URLs should be returned as-is
    if (
        path.startswith(("http://", "https://"))
        or path.startswith("data:")
        or path.startswith("mailto:")
        or path.startswith("ftp://")
        or not path
    ):
        return path, path

    # Where REPORTS sit locally
    # Can be a MountedLocalPath with spec being a cloud path
    basedir = run_meta["outdir"]
    # How the basedir (outdir) was specified, could be cloud path
    basedir_spec = getattr(basedir, "spec", basedir)
    # apath may be changed so we need orig_path to keep the original one
    orig_path = apath = PanPath(path)

    if isinstance(orig_path, CloudPath):
        # Make it local, the report is built locally
        apath = PanPath(get_fspath(apath, cachedir_for_cloud))
    elif run_meta["mounted_outdir"] and apath.is_relative_to(
        run_meta["mounted_outdir"]
    ):
        # Use spec, which should be a cloud path
        apath = basedir_spec.parent.joinpath(
            apath.relative_to(run_meta["mounted_outdir"])
        )
        apath = getattr(apath, "mounted", apath)
    elif run_meta["mounted_workdir"] and apath.is_relative_to(
        run_meta["mounted_workdir"]
    ):
        # Use workdir, which should be a cloud path
        apath = run_meta["workdir"].spec.parent.joinpath(
            apath.relative_to(run_meta["mounted_workdir"])
        )
        apath = getattr(apath, "mounted", apath)

    if Path(apath).is_relative_to(basedir.parent):
        url = f"../{Path(apath).relative_to(basedir.parent)}"
        return url, apath

    url = str(orig_path)

    # otherwise, let's check if it is relative to the workdir.parent
    # if so, that means it is a result from non-export processes
    if Path(apath).is_relative_to(run_meta["workdir"].parent):
        warning_msg = (
            f"Resource '{orig_path}' from non-exported location detected for {tag}, "
            "copying it to REPORTS/data ..."
        )
        url = Path(apath).relative_to(run_meta["workdir"].parent).resolve()
    else:
        # otherwise if
        # - it is a cloud path, we just copy it to data/
        # - it is an absolute local path, we also copy it to data/
        # - it is a relative local path, keep as is
        if not isinstance(apath, CloudPath) and not apath.is_absolute():
            return url, apath  # keep as is

        path_msg = f"'{url}' ({apath}) " if url != str(apath) else f"{url} "
        warning_msg = (
            f"External resource {path_msg} detected for {tag}, "
            "copying it to REPORTS/data ..."
        )

    logfn("warning", warning_msg)
    suffix = hashlib.sha256(str(apath).encode()).hexdigest()[:8]
    url = f"data/{apath.stem}.{suffix}{apath.suffix}"

    dest_path = basedir_spec.joinpath(url)
    await a_copy_all(apath, dest_path, cachedir_for_cloud)

    return url, apath


async def _preprocess_relpath_tag(
    matching: re.Match,
    run_meta: Mapping[str, Any],
    relpath_tags: Mapping[str, str | Sequence[str]] | None,
    cachedir_for_cloud: str,
    logfn: Callable,
) -> Tuple[str, List[Tuple[PanPath, PanPath]]]:
    """Preprocess tags with paths to be redirected"""
    pathval = None
    tag = matching.group("tag")
    attrs = matching.group("attrs")
    has_height = False
    has_width = False
    if tag == "Image":
        has_height = "height=" in attrs
        has_width = "width=" in attrs
    rp_tags = RELPATH_TAGS.copy()
    rp_tags.update(relpath_tags or {})

    async def repl_attrs(mattrs):
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
                    u = await _path_to_url(
                        av, run_meta, tag, cachedir_for_cloud, logfn
                    )
                    av2[i] = {"src": u[0]}
                elif isinstance(av, dict):
                    u = await _path_to_url(
                        av["src"], run_meta, tag, cachedir_for_cloud, logfn
                    )
                    av["src"] = u[0]
            return f" {attrname}={{ {json.dumps(av2)} }}"

        pathval = attrval
        urlval, path = await _path_to_url(
            attrval, run_meta, tag, cachedir_for_cloud, logfn
        )

        if tag == "Image" and attrname == "src" and not has_height and pathval:
            out = f' {attrname}="{urlval}"'

            with suppress(Exception):
                width, height = await get_imagesize(path, cachedir_for_cloud)
                if height > 0:
                    out = f"{out} height={{{height}}}"
                if width > 0 and not has_width:
                    out = f"{out} width={{{width}}}"

                return out

        return f' {attrname}="{urlval}"'

    attrs = await a_re_sub(TAG_ATTR_RE, repl_attrs, matching.group("attrs"))
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
        return (
            f"{tag}data:text/plain;base64,{b64encode(latex.encode()).decode()}</Math>"
        )

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


async def _preprocess_section(
    section: str,
    h2_index: int,
    page: int,
    run_meta: Mapping[str, Any],
    relpath_tags: Mapping[str, str | Sequence[str]] | None,
    cachedir_for_cloud: str,
    logfn: Callable,
) -> Tuple[str, List[Mapping[str, Any]]]:
    """Preprocesss a section of the document (between h1 tags)

    Args:
        section: The source code of the section
        h2_index: The start h2 index
        page: which page are we on?
        run_meta: The run meta paths
        relpath_tags: Tags with properties that need to convert to relative paths
            i.e. {"Image": "src"}
        logfn: The logging function

    Returns:
        The preprocessed section and the toc items
    """
    section = _preprocess_math(section)
    section = _preprocess_markdown(section)

    async def repl_relpath_tags(matching):
        new_section = await _preprocess_relpath_tag(
            matching,
            run_meta,
            relpath_tags,
            cachedir_for_cloud,
            logfn,
        )
        return new_section

    # handle relpath tags
    section = await a_re_sub(TAG_RE, repl_relpath_tags, section)

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
async def preprocess(
    text: str,
    run_meta: Mapping[str, Any],
    toc_switch: bool,
    paging: Union[bool, int],
    relpath_tags: Mapping[str, str | Sequence[str]] | None,
    cachedir_for_cloud: str,
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
        run_meta: The run meta paths
        toc_switch: Whether render a TOC?
        paging: Number of h1's in a page
            False to disable
        relpath_tags: Tags with properties that need to convert to relative paths
            i.e. {"Image": "src"}
        cachedir_for_cloud: The base temporary directory when workdir is on cloud
        logfn: The logging function

    Returns:
        The preprocessed text and the toc dict
    """
    # split the text h1 tags
    splits = re.split(H1_TAG, text)
    # splits[0] is header
    len_sections = (len(splits) - 1) // 2
    if len_sections == 0:
        # no h1's
        section, _ = await _preprocess_section(
            splits[0],
            h2_index=0,
            page=0,
            run_meta=run_meta,
            relpath_tags=relpath_tags,
            cachedir_for_cloud=cachedir_for_cloud,
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
            section, toc_items = await _preprocess_section(
                splt,
                h2_index=h2_index,
                page=page,
                run_meta=run_meta,
                relpath_tags=relpath_tags,
                cachedir_for_cloud=cachedir_for_cloud,
                logfn=logfn,
            )
            h2_index += len(toc_items)
            pages[page].append(section)
            if toc_switch:
                toc[-1]["children"].extend(toc_items)

    return ["".join(page) for page in pages], toc
