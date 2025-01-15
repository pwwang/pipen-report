"""Filters for pipen-report

This module contains the filters for pipen-report. The filters are used
in the report template to render the report.
"""
from __future__ import annotations

import re
import html
import json
import textwrap
import warnings
import imagesize
from contextlib import suppress
from typing import Any, Iterable, Union, List, Mapping
from os import PathLike
from pathlib import Path
from markdown import markdown as markdown_parse

TAB = "  "


def datatable(
    path: PathLike,
    *args: Any,
    ncols: Union[int, Iterable] = None,
    nrows: Union[int, Iterable] = None,
    double_precision: int = 4,
    excluded: set = None,
    **kwargs: Any,
) -> str:
    """Read data from a file, using pandas.read_csv() and make it to json so
    js can handle it and render it with <DataTable />

    Args:
        path (PathLike): The path to the data file.
        *args (Any): Additional positional arguments to pass to pandas.read_csv().
        ncols (Union[int, Iterable], optional): Either the number of columns to
            select or an iterable of column indices or names. Defaults to None.
        nrows (Union[int, Iterable], optional): Either the number of rows to select
            or an iterable of row indices. Defaults to None.
        double_precision (int, optional): The precision for double numbers.
            See also pandas.DataFrame.to_json(). Defaults to 4.
        excluded (set, optional): A set of column names to exclude from the resulting
            DataFrame. Defaults to None.
        **kwargs (Any): Additional keyword arguments to pass to pandas.read_csv().

    Returns:
        str: A JSON format of the data.

    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        import pandas

    kwargs.setdefault("sep", "\t")
    df = pandas.read_csv(path, *args, **kwargs)
    if not isinstance(df.index, pandas.RangeIndex):
        df = df.reset_index(names=["ROWNAMES"])

    if excluded:
        kept_cols = [col for col in df.columns if col not in excluded]
        df = df.loc[:, kept_cols]

    # use ncols and nrows to filter
    if nrows is None:
        nrows = df.shape[0]
    if ncols is None:
        ncols = df.shape[1]

    if isinstance(nrows, int):
        nrows = min(nrows, df.shape[0])
        nrows = range(nrows)  # type: ignore
    if isinstance(ncols, int):
        ncols = min(ncols, df.shape[1])
        ncols = range(ncols)  # type: ignore

    if all(isinstance(row, int) for row in nrows):
        nrows = df.index[nrows]
    if all(isinstance(col, int) for col in ncols):
        ncols = df.columns[ncols]

    df = df.loc[nrows, ncols]
    # "." in column names causing problem at frontend
    df = df.rename(lambda x: re.sub(r"[^\w]+", "_", x), axis="columns")
    # add id for sorting purposes
    if "id" not in df:
        df["id"] = range(df.shape[0])

    return df.to_json(orient="records", double_precision=double_precision)


def render_component(
    component: str | Mapping[str, Any],
    job: Mapping[str, Any] = None,
    level: int = 0,
) -> str:
    """
    Render the content based on its kind.

    Args:
        component (Any): The content to be rendered.
        job (Mapping[str, Any]): The job information.
        level (int): The level of the content.

    Returns:
        str: The rendered content.

    Raises:
        ValueError: If the kind of component in toc is unknown.
    """
    job = job or {}
    if not isinstance(component, dict):
        return _tag("p", slot=html.escape(str(component)), _level=level)

    cont = component.copy()
    kind = cont.pop("kind")
    if kind not in render_component.renderers:
        raise ValueError(
            f"Unknown kind of component: {kind}. "
            f"Allowed components: {list(render_component.renderers)}"
        )

    return render_component.renderers[kind](cont, job=job, level=level)


render_component.renderers = {}


def register_component(kind: str, *aliases: str):
    """Register a component renderer

    Args:
        kind (str): The kind of component to register.
        *aliases (str): The aliases of the kind.

    Returns:
        Callable: The decorator to register the component renderer.
    """
    kinds = [kind, *aliases]

    def decorator(func):
        for knd in kinds:
            render_component.renderers[knd] = func
        return func

    return decorator


@register_component("accordion")
def _render_accordion(
    cont: Mapping[str, Any],
    job: Mapping[str, Any],
    level: int,
) -> str:
    """
    Render an accordion item based on the given content, job, and level.

    Args:
        cont (Mapping[str, Any]): The content of the accordion item.
        job (Mapping[str, Any]): The job information.
        level (int): The level of the accordion item.

    Returns:
        str: The rendered accordion item.
    """
    cont = cont.copy()
    ui = cont.pop("ui", "flat")
    contents = cont.pop("contents", [])
    return _tag(
        "AccordionItem",
        _level=level,
        slot=render_ui(contents, ui, job=job, level=1),
        **cont,
    )


@register_component("descr")
def _render_descr(
    cont: Mapping[str, Any],
    job: Mapping[str, Any],
    level: int,
) -> str:
    """
    Render the description based on the given content, job, and level.

    Args:
        cont (Mapping[str, Any]): The content mapping.
        job (Mapping[str, Any]): The job mapping.
        level (int): The level of the description.

    Returns:
        str: The rendered description.
    """
    cont = cont.copy()
    if cont.get("once", False) and job["index"] != 0:
        return ""

    slot = str(cont.pop("content", cont.pop("descr", "")) or "")
    markdown = cont.pop("markdown", False)
    if markdown:
        slot = markdown_parse(slot)
    title = cont.pop("title", cont.pop("name", None))
    return _tag("Descr", slot=slot, _level=level, title=title, **cont)


@register_component("error")
def _render_error(
    cont: Mapping[str, Any],
    job: Mapping[str, Any],
    level: int,
) -> str:
    """
    Render an error message as an inline notification.

    Args:
        cont (Mapping[str, Any]): The content of the error message.
        job (Mapping[str, Any]): The job information.
        level (int): The level of the error message.

    Returns:
        str: The rendered error message as a string.
    """
    cont["subtitle"] = str(cont.pop("content", ""))
    cont.setdefault("hideCloseButton", True)
    cont.setdefault("lowContrast", True)
    cont.setdefault("kind_", "warning")
    return _tag("InlineNotification", **cont, _level=level)


@register_component("list")
def _render_list(
    cont: Mapping[str, Any],
    job: Mapping[str, Any],
    level: int,
) -> str:
    """
    Render a list.

    Args:
        cont (Mapping[str, Any]): The container containing the list properties.
        job (Mapping[str, Any]): The job containing the list items.
        level (int): The level of the list.

    Returns:
        str: The rendered list as a string.
    """
    ordered = cont.pop("ordered", False)
    items = cont.pop("items", [])
    tag = "OrderedList" if ordered else "UnorderedList"
    list_items = [_tag("ListItem", slot=item, _level=1) for item in items]
    return _tag(tag, slot="\n".join(list_items), **cont, _level=level)


@register_component("table", "datatable")
def _render_table(
    cont: Mapping[str, Any],
    job: Mapping[str, Any],
    level: int,
) -> str:
    """
    Render a table.

    Args:
        cont (Mapping[str, Any]): The container for the table attributes.
            Keys will be passed to `<DataTable ... />` component.
            `data` is special key to hold arguments passed to `datatable` filter.
            `data.file` or `data.path` is used to hold the path to the data file.
            The rest of the keys in `data` are passed to `datatable` filter.
            `src` can be True so that `data.path` or `data.file` is used as the `src`.
        job (Mapping[str, Any]): The container for the job attributes.
        level (int): The level of the table.

    Returns:
        str: The rendered table as a string.
    """
    attrs = cont.copy()
    data = attrs.pop("data", {}).copy()
    src = attrs.get("src", True)
    path = data.pop("path", data.pop("file", src))

    if isinstance(path, bool):
        raise ValueError("No data.path or data.file is specified")

    if src is True:
        attrs["src"] = path

    attrs["data"] = json.loads(datatable(path, **data))
    return _tag("DataTable", **attrs, _level=level)


@register_component("img", "image")
def _render_image(
    cont: Mapping[str, Any],
    job: Mapping[str, Any],
    level: int,
) -> str:
    """Render an image

    Args:
        cont (Mapping[str, Any]): The container containing the image attributes.
        job (Mapping[str, Any]): The job containing the image data.
        level (int): The level of the image in the hierarchy.

    Returns:
        str: The rendered image as a string.
    """
    attrs = cont.copy()
    src = attrs["src"]
    width = attrs.get("width", None)
    height = attrs.get("height", None)
    if not width or not height:
        with suppress(FileNotFoundError):
            width, height = imagesize.get(src)
            if width > 0 and height > 0:
                attrs["width"] = width
                attrs["height"] = height

    return _tag("Image", **attrs, _level=level)


@register_component("table_img", "table_image")
def _render_table_image(
    cont: Mapping[str, Any],
    job: Mapping[str, Any],
    level: int,
) -> str:
    """
    Render a table image with optional name and description.

    Args:
        cont (Mapping[str, Any]): The container containing the image details.
        job (Mapping[str, Any]): The job details.
        level (int): The level of the table image.

    Returns:
        str: The rendered table image HTML.

    """
    cont = cont.copy()
    name = cont.pop("name", cont.pop("title", cont.pop("caption", None)))
    descr = cont.pop("descr", None)
    markdown = cont.pop("markdown", False)
    cont.setdefault("class", "pipen-report-table-image")

    return _tag(
        "div",
        slot="\n".join(
            [
                _render_descr(
                    {
                        "content": descr,
                        "title": name,
                        "class": "pipen-report-table-image-descr",
                        "markdown": markdown,
                    },
                    job=job,
                    level=1,
                )
                if name or descr
                else "",
                _render_image(cont, job=job, level=1),
            ]
        ),
        _level=level,
    )


@register_component("tab")
def _render_tab(
    cont: Mapping[str, Any],
    job: Mapping[str, Any],
    level: int,
) -> str:
    """
    Render a tab.

    Args:
        cont (Mapping[str, Any]): The container containing the tab information.
        job (Mapping[str, Any]): The job information.
        level (int): The level of the tab.

    Returns:
        str: The rendered tab.

    """
    ui = cont.get("ui", "flat")
    return (
        _tag(
            "Tab",
            label=cont.get("name", cont.get("title", cont.get("label"))),
            _level=level,
        ),
        _tag(
            "TabContent",
            slot=render_ui(cont["contents"], ui, job=job, level=1),
            _level=level,
        ),
    )


@register_component("tag")
def _render_tag(
    cont: Mapping[str, Any],
    job: Mapping[str, Any],
    level: int,
) -> str:
    """
    Render a tag.

    Args:
        cont (Mapping[str, Any]): The container containing the tag information.
        job (Mapping[str, Any]): The job information.
        level (int): The level of the tag.

    Returns:
        str: The rendered tag.

    """
    tag = cont.pop("tag")
    return _tag(tag, **cont, _level=level)


def render_ui(
    contents: List[Mapping[str, Any]],
    ui: str,
    job: Mapping[str, Any] = None,
    level: int = 0,
) -> str:
    """Render a ui

    Args:
        contents (List[Mapping[str, Any]]): The contents to render in the UI.
        ui (str): The type of UI to render.
            Allowed values are "flat", "table_of_images", "accordion", and "tabs".
        job (Mapping[str, Any], optional): The job information. Defaults to None.
        level (int, optional): The level of the UI. Defaults to 0.

    Returns:
        str: The rendered UI as a string.

    Raises:
        ValueError: If the provided UI type is not one of the allowed values.
    """
    job = job or {}
    ui_parts = ui.split(":")

    if ui_parts[0] not in render_ui.renderers:
        raise ValueError(
            f"Unknown ui: {ui_parts[0]}. Allowed: {list(render_ui.renderers)}"
        )

    renderer = render_ui.renderers[ui_parts[0]]
    return renderer(contents, job, level, *ui_parts[1:])


render_ui.renderers = {}


def register_ui(kind: str, *aliases: str):
    """Register a UI renderer

    Args:
        kind (str): The kind of UI to register.
        *aliases (str): The aliases of the kind.

    Returns:
        Callable: The decorator to register the UI renderer.
    """
    kinds = [kind, *aliases]

    def decorator(func):
        for knd in kinds:
            render_ui.renderers[knd] = func
        return func

    return decorator


@register_ui("flat")
def _ui_flat(
    contents: List[Mapping[str, Any]],
    job: Mapping[str, Any],
    level: int,
) -> str:
    """Render a flat ui

    Args:
        contents (List[Mapping[str, Any]]): The contents to render.
        job (Mapping[str, Any]): The job information.
        level (int): The level of the UI.

    Returns:
        str: The rendered UI as a string.
    """
    return "\n".join(render_component(cont, job, level) for cont in contents)


@register_ui("dropdown_switcher")
def _ui_dropdown_switcher(
    contents: List[Mapping[str, Any]],
    job: Mapping[str, Any],
    level: int,
    ui_arg: str = None,
) -> str:
    """
    Render a dropdown switcher UI.

    Args:
        contents (List[Mapping[str, Any]]): The contents to be rendered.
        job (Mapping[str, Any]): The job information.
        level (int): The level of the dropdown switcher.

    Returns:
        str: The rendered dropdown switcher HTML.

    Raises:
        ValueError: If the 'kind' attribute of any content is not 'tab'.
    """
    ds_id = _ui_dropdown_switcher.counter
    _ui_dropdown_switcher.counter += 1
    selected_id = ui_arg or "0"
    components = []
    items = []

    for i, cont in enumerate(contents):
        name = cont.pop("ds_name")
        items.append({"id": str(i), "text": name})
        if "kind" not in cont:
            components.append(
                _tag(
                    "div",
                    id=f"pipen-report-ds-content-{ds_id}-{i}",
                    _level=level,
                    class_=f"pipen-report-ds-content-{ds_id}",
                    style="display: none;" if i != int(selected_id) else "",
                )
            )
        else:
            components.append(
                _tag(
                    "div",
                    id=f"pipen-report-ds-content-{ds_id}-{i}",
                    _level=level,
                    class_=f"pipen-report-ds-content-{ds_id}",
                    slot=render_component(cont, job=job, level=1),
                    style="display: none;" if i != int(selected_id) else "",
                )
            )

    dropdown = _tag(
        "Dropdown",
        selectedId=selected_id,
        items=items,
        _level=level,
        **{
            "on:select": (
                "{ ({detail}) => {"
                "    const conents = document.getElementsByClassName("
                f"      'pipen-report-ds-content-{ds_id}'"
                "    );"
                "    for (const content of conents) {"
                "       content.style.display = 'none';"
                "    }"
                "    document.getElementById("
                f"      'pipen-report-ds-content-{ds_id}-' + detail.selectedId"
                "    ).style.display = 'block';"
                "} }"
            )
        }
    )

    return "\n".join([dropdown, *components])


_ui_dropdown_switcher.counter = 0


@register_ui("table_of_images")
def _ui_table_of_images(
    contents: List[Mapping[str, Any]],
    job: Mapping[str, Any],
    level: int,
    ui_arg: str = None,
) -> str:
    """
    Render a table of images UI.

    Args:
        ui (str): The UI configuration for the table of images.
        contents (List[Mapping[str, Any]]): The list of image contents to be rendered.
        job (Mapping[str, Any]): The job information.
        level (int): The level of the table of images.

    Returns:
        str: The rendered table of images HTML.

    Raises:
        ValueError: If the 'kind' attribute of any image content is not 'table_img' or
        'table_image'.
    """
    ncol = int(ui_arg or "2")

    grid_col = "auto" if len(contents) >= ncol else f"{100. / ncol}%"
    img_src = []
    for cont in contents:
        if isinstance(cont, str):
            cont = {"kind": "tag", "tag": "div", "slot": cont}

        cont.setdefault("kind", "table_image")
        img_src.append(render_component(cont, job=job, level=1))

    return _tag(
        "div",
        slot="\n".join(img_src),
        class_="pipen-report-table-of-images",
        style=f"grid-template-columns: repeat({ncol}, {grid_col}); ",
        _level=level,
    )


@register_ui("tabs")
def _ui_tabs(
    contents: List[Mapping[str, Any]],
    job: Mapping[str, Any],
    level: int,
) -> str:
    """
    Render a tabs UI.

    Args:
        contents (List[Mapping[str, Any]]): List of tab contents.
        job (Mapping[str, Any]): Job information.
        level (int): Level of the UI.

    Returns:
        str: Rendered tabs UI.
    """
    tabs = []
    for cont in contents:
        if cont.get("kind", "tab") != "tab":
            raise ValueError("Only kind = tab allowed in UI tabs")

        cont["kind"] = "tab"
        tabs.append(render_component(cont, job=job, level=1))

    tab_slot = [tab[0] for tab in tabs]
    tab_slot.append(
        _tag(
            "svelte:fragment",
            slot_="content",
            slot="\n".join([tab[1] for tab in tabs]),
            _level=1,
        )
    )
    return _tag("Tabs", slot="\n".join(tab_slot), _level=level)


@register_ui("accordion")
def _ui_accordion(
    contents: List[Mapping[str, Any]],
    job: Mapping[str, Any],
    level: int,
    ui_arg: str = None,
) -> str:
    """
    Render an accordion ui.

    Args:
        contents (List[Mapping[str, Any]]): The contents of the accordion.
        job (Mapping[str, Any]): The job information.
        level (int): The level of the accordion.

    Returns:
        str: The rendered accordion UI.
    """
    accords = []
    ui_arg = ui_arg or "start"
    has_open = any(cont.get("open", False) for cont in contents)
    for i, cont in enumerate(contents):
        if cont.get("kind", "accordion") != "accordion":
            raise ValueError("Only kind = accordion allow in ui accordion")

        cont["kind"] = "accordion"
        if not has_open and i == 0:
            cont["open"] = True
        accords.append(render_component(cont, job=job, level=1))

    return _tag("Accordion", align=ui_arg, slot="\n".join(accords), _level=level)


def _tag(tag: str, _level: int = 0, **attrs: Any) -> str:
    """
    Generate a html tag for report

    Args:
        tag (str): The HTML tag name.
        _level (int, optional): The indentation level. Defaults to 0.
        **attrs: Additional attributes for the HTML tag.

    Returns:
        str: The generated HTML tag.

    """
    slot = attrs.pop("slot", None)

    tag_attrs = []
    for k, v in attrs.items():
        if v is False or v is None:
            continue

        if k == "class_":
            k = "class"
        elif k == "slot_":
            k = "slot"
        elif k == "kind_":
            k = "kind"

        if isinstance(v, str):
            tag_attrs.append(f"{k}={json.dumps(v)}")
        elif v is True:
            tag_attrs.append(k)
        else:
            tag_attrs.append(f"{k}={{ {json.dumps(v)} }}")

    if not tag_attrs:
        tag_attrs = ""
    elif all(len(tag_attr) <= 60 for tag_attr in tag_attrs):
        tag_attrs = " " + " ".join(tag_attrs)
    else:
        tag_attrs = "\n" + textwrap.indent("\n".join(tag_attrs), TAB)

    out = (
        f"<{tag}{tag_attrs}>{slot}</{tag}>"
        if (
            slot
            and "\n" not in slot
            and len(slot) <= 60
            and not slot.startswith(TAB)
            and "\n" not in tag_attrs
        )
        else f"<{tag}{tag_attrs}>\n{slot}\n</{tag}>"
        if slot
        else f"<{tag}{tag_attrs} />"
    )
    return textwrap.indent(out, TAB * _level)


def render_job(
    job: Mapping[str, Any],
    report_file: str = "report.json",
    h: int = 1,
) -> str:
    """Generate a report template from a report json file

    Args:
        job: The job data that can be used to render the template
        report_file: Absolute path to a report file or relative to `job.outdir`
        h: The starting level of the headers

    Returns:
        The generated report
    """
    # h1 => list(
    #   h2 => list(
    #       title1 => list(ui1 => list(content11, content12)),
    #       title2 => list(ui2 => list(content21, content22))
    #   )
    # )
    if not Path(report_file).is_absolute():
        report_file = Path(job["outdir"]) / report_file

    toc_obj = json.loads(Path(report_file).read_text())
    out = ["<!-- Generated by pipen_report.filters.report -->"]
    out_append = out.append
    for h1, section in toc_obj.items():
        h1 = h1.split("#", 1)[0].strip()
        out_append(_tag(f"h{h}", slot=h1))

        for h2, subsection in section.items():
            h2 = h2.split("#", 1)[0].strip()
            if h2:
                out_append(_tag(f"h{h + 1}", slot=h2))

            for title, content in subsection.items():
                title = title.split("#", 1)[0].strip()
                if title:
                    out_append(_tag(f"h{h + 2}", slot=title))

                for ui, conts in content.items():
                    ui = ui.split("#", 1)[0].strip()
                    out_append(render_ui(conts, ui, job=job))

    out_append("<!-- End of Generated by pipen_report.filters.report -->")
    return "\n".join(out)


FILTERS = {}
FILTERS["datatable"] = datatable
FILTERS["render_component"] = render_component
FILTERS["render_ui"] = render_ui
FILTERS["render_job"] = render_job
