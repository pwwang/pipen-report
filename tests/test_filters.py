from copy import deepcopy
import json
import pytest

from pathlib import Path
from pipen_report.filters import (
    TAB,
    datatable,
    render_component,
    _render_accordion,
    _render_descr,
    _render_error,
    _render_list,
    _render_table,
    _render_image,
    _render_table_image,
    _render_tab,
    render_ui,
    _ui_flat,
    _ui_table_of_images,
    _ui_tabs,
    _ui_accordion,
    _ui_dropdown_switcher,
    _tag,
    render_job,
    register_component,
    register_ui,
)


datafile = Path(__file__).parent / "data" / "data.csv"
imgpath = Path(__file__).parent.parent / "example" / "placeholder.png"


def test_datatable():
    out = datatable(datafile)
    assert out == (
        '[{"h_1":"a","h2":1,"h3":1.1235,"id":0},'
        '{"h_1":"b","h2":2,"h3":2.2,"id":1},'
        '{"h_1":"c","h2":3,"h3":3.3,"id":2},'
        '{"h_1":"d","h2":4,"h3":4.4,"id":3},'
        '{"h_1":"e","h2":5,"h3":5.5,"id":4},'
        '{"h_1":"f","h2":6,"h3":6.6,"id":5},'
        '{"h_1":"g","h2":7,"h3":7.7,"id":6},'
        '{"h_1":"h","h2":8,"h3":8.8,"id":7},'
        '{"h_1":"i","h2":9,"h3":9.9,"id":8},'
        '{"h_1":"j","h2":10,"h3":10.1,"id":9}]'
    )

    out = datatable(datafile, ncols=2, nrows=2)
    assert out == ('[{"h_1":"a","h2":1,"id":0},' '{"h_1":"b","h2":2,"id":1}]')

    out = datatable(datafile, excluded="h3")
    assert out == (
        '[{"h_1":"a","h2":1,"id":0},'
        '{"h_1":"b","h2":2,"id":1},'
        '{"h_1":"c","h2":3,"id":2},'
        '{"h_1":"d","h2":4,"id":3},'
        '{"h_1":"e","h2":5,"id":4},'
        '{"h_1":"f","h2":6,"id":5},'
        '{"h_1":"g","h2":7,"id":6},'
        '{"h_1":"h","h2":8,"id":7},'
        '{"h_1":"i","h2":9,"id":8},'
        '{"h_1":"j","h2":10,"id":9}]'
    )


@pytest.mark.parametrize(
    "tag, level, attrs, expected",
    [
        (
            "div",
            0,
            {"slot": "content", "class_": "my-class", "id": "my-id"},
            '<div class="my-class" id="my-id">content</div>',
        ),
        (
            "div",
            0,
            {"class_": "my-class", "id": "my-id"},
            '<div class="my-class" id="my-id" />',
        ),
        (
            "div",
            0,
            {"class_": "my-class", "id": "my-id", "disabled": True},
            '<div class="my-class" id="my-id" disabled />',
        ),
        (
            "div",
            0,
            {"class_": "my-class", "id": "my-id", "disabled": False},
            '<div class="my-class" id="my-id" />',
        ),
        (
            "div",
            0,
            {"class_": "my-class", "id": "my-id", "disabled": None},
            '<div class="my-class" id="my-id" />',
        ),
        (
            "div",
            0,
            {"class_": "my-class", "id": "my-id", "data": '{"key": "value"}'},
            '<div class="my-class" id="my-id" data="{\\"key\\": \\"value\\"}" />',
        ),
        (
            "div",
            0,
            {"class_": "my-class", "id": "my-id", "data": {"key": "value"}},
            '<div class="my-class" id="my-id" data={ {"key": "value"} } />',
        ),
        (
            "div",
            0,
            {"slot_": "content", "class_": "my-class", "id": "my-id"},
            '<div slot="content" class="my-class" id="my-id" />',
        ),
        (
            "div",
            0,
            {"kind_": "type", "class_": "my-class", "id": "my-id"},
            '<div kind="type" class="my-class" id="my-id" />',
        ),
        (
            "div",
            1,
            {
                "slot": "content1\ncontent2",
                "class_": "my-class",
                "id": "my-id",
            },
            (
                f'{TAB}<div class="my-class" id="my-id">\n'
                f'{TAB}content1\n'
                f'{TAB}content2\n'
                f'{TAB}</div>'
            ),
        ),
        (
            "div",
            0,
            {
                "slot": "content1",
                # long attribute
                "id": "my-id-" * 11,
            },
            (
                '<div\n'
                f'{TAB}id="my-id'
                '-my-id-my-id-my-id-my-id-my-id-my-id-my-id-my-id-my-id-my-id-">\n'
                f'content1\n'
                '</div>'
            ),
        ),
    ],
    ids=[
        "div with content",
        "div with no content",
        "div with disabled",
        "div with disabled False",
        "div with disabled None",
        "div with data str",
        "div with data dict",
        "div with slot",
        "div with kind",
        "div with multiline content",
        "div with long attribute",
    ],
)
def test_tag(tag, level, attrs, expected):
    result = _tag(tag, level, **attrs)
    assert result == expected


@pytest.mark.parametrize(
    "cont, job, level, expected",
    [
        (
            {
                "title": "Title1",
                "contents": ["Contents1"],
                "ui": "flat",
            },
            {"job_info": "Job1"},
            0,
            f'<AccordionItem title="Title1">\n{TAB}<p>Contents1</p>\n</AccordionItem>',
        ),
        (
            {
                "title": "Title2",
                "contents": [
                    {
                        "kind": "tag",
                        "tag": "div",
                        "slot": "abc",
                        "class_": "my-class",
                    }
                ],
                "ui": "flat",
            },
            {"job_info": "Job2"},
            1,
            (
                f'{TAB}<AccordionItem title="Title2">\n'
                f'{TAB * 2}<div class="my-class">abc</div>\n'
                f'{TAB}</AccordionItem>'
            ),
        ),
    ],
    ids=[
        "Test case 1: level 0",
        "Test case 2: level 1",
    ],
)
def test_render_accordion(cont, job, level, expected):
    result = _render_accordion(cont, job, level)
    assert result == expected


@pytest.mark.parametrize(
    "cont, job, level, expected",
    [
        (
            {
                "title": "Title1",
                "contents": ["Contents1"],
                "ui": "flat",
            },
            {"job_info": "Job1"},
            0,
            (
                '<Tab label="Title1" />',
                f"<TabContent>\n{TAB}<p>Contents1</p>\n</TabContent>",
            ),
        ),
        (
            {
                "title": "Title2",
                "contents": [
                    {
                        "kind": "tag",
                        "tag": "div",
                        "slot": "abc",
                        "class_": "my-class",
                    }
                ],
                "ui": "flat",
            },
            {"job_info": "Job2"},
            1,
            (
                f'{TAB}<Tab label="Title2" />',
                f'{TAB}<TabContent>\n'
                f'{TAB * 2}<div class="my-class">abc</div>\n'
                f'{TAB}</TabContent>',
            ),
        ),
    ],
    ids=[
        "Test case 1: level 0",
        "Test case 2: level 1",
    ],
)
def test_render_tab(cont, job, level, expected):
    result = _render_tab(cont, job, level)
    assert result == expected


@pytest.mark.parametrize(
    "cont, job, level, expected",
    [
        (
            {
                "content": "Content1",
            },
            {"index": 0},
            0,
            '<Descr>Content1</Descr>',
        ),
        (
            {
                "content": "Content2",
                "once": True,
            },
            {"index": 1},
            0,
            '',
        ),
        (
            {
                "content": "Content3",
                "once": False,
                "title": "Title3",
            },
            {"index": 2},
            1,
            f'{TAB}<Descr title="Title3">Content3</Descr>',
        ),
    ],
    ids=[
        "Test case 1: level 0",
        "Test case 2: level 0",
        "Test case 3: level 1",
    ],
)
def test_render_descr(cont, job, level, expected):
    result = _render_descr(cont, job, level)
    assert result == expected


@pytest.mark.parametrize(
    "cont, job, level, expected",
    [
        (
            {
                "content": "Content1",
            },
            {},
            0,
            (
                '<InlineNotification subtitle="Content1" hideCloseButton lowContrast '
                'kind="warning" />'
            ),
        ),
        (
            {
                "content": "Content2",
                "hideCloseButton": False,
            },
            {},
            0,
            '<InlineNotification subtitle="Content2" lowContrast kind="warning" />',
        ),
        (
            {
                "content": "Content3",
                "hideCloseButton": True,
                "kind_": "info",
            },
            {},
            1,
            (
                f'{TAB}<InlineNotification hideCloseButton kind="info" '
                'subtitle="Content3" lowContrast />'
            ),
        ),
    ],
    ids=[
        "Test case 1: level 0",
        "Test case 2: level 0",
        "Test case 3: level 1",
    ],
)
def test_render_error(cont, job, level, expected):
    result = _render_error(cont, job, level)
    assert result == expected


@pytest.mark.parametrize(
    "cont, job, level, expected",
    [
        (
            {
                "ordered": True,
                "items": ["Item1", "Item2"],
            },
            {},
            0,
            (
                '<OrderedList>\n'
                f'{TAB}<ListItem>Item1</ListItem>\n'
                f'{TAB}<ListItem>Item2</ListItem>\n'
                '</OrderedList>'
            ),
        ),
        (
            {
                "ordered": False,
                "items": ["Item1", "Item2"],
            },
            {},
            0,
            (
                '<UnorderedList>\n'
                f'{TAB}<ListItem>Item1</ListItem>\n'
                f'{TAB}<ListItem>Item2</ListItem>\n'
                '</UnorderedList>'
            ),
        ),
        (
            {
                "ordered": True,
                "items": ["Item1", "Item2"],
                "title": "Title1",
            },
            {},
            1,
            (
                f'{TAB}<OrderedList title="Title1">\n'
                f'{TAB * 2}<ListItem>Item1</ListItem>\n'
                f'{TAB * 2}<ListItem>Item2</ListItem>\n'
                f'{TAB}</OrderedList>'
            ),
        ),
    ],
    ids=[
        "Test case 1: level 0",
        "Test case 2: level 0",
        "Test case 3: level 1",
    ],
)
def test_render_list(cont, job, level, expected):
    result = _render_list(cont, job, level)
    assert result == expected


@pytest.mark.parametrize(
    "cont, job, level, expected",
    [
        (
            {
                "data": {"file": str(datafile)},
                "src": False,
            },
            {},
            0,
            (
                '<DataTable\n'
                + TAB
                + (
                    'data={ [{"h_1": "a", "h2": 1, "h3": 1.1235, "id": 0}, '
                    '{"h_1": "b", "h2": 2, "h3": 2.2, "id": 1}, '
                    '{"h_1": "c", "h2": 3, "h3": 3.3, "id": 2}, '
                    '{"h_1": "d", "h2": 4, "h3": 4.4, "id": 3}, '
                    '{"h_1": "e", "h2": 5, "h3": 5.5, "id": 4}, '
                    '{"h_1": "f", "h2": 6, "h3": 6.6, "id": 5}, '
                    '{"h_1": "g", "h2": 7, "h3": 7.7, "id": 6}, '
                    '{"h_1": "h", "h2": 8, "h3": 8.8, "id": 7}, '
                    '{"h_1": "i", "h2": 9, "h3": 9.9, "id": 8}, '
                    '{"h_1": "j", "h2": 10, "h3": 10.1, "id": 9}] } />'
                )
            ),
        ),
        (
            {
                "data": {"file": str(datafile)},
                "src": True,
            },
            {},
            0,
            (
                '<DataTable\n'
                + TAB
                + f'src="{datafile}"\n'
                + TAB
                + (
                    'data={ [{"h_1": "a", "h2": 1, "h3": 1.1235, "id": 0}, '
                    '{"h_1": "b", "h2": 2, "h3": 2.2, "id": 1}, '
                    '{"h_1": "c", "h2": 3, "h3": 3.3, "id": 2}, '
                    '{"h_1": "d", "h2": 4, "h3": 4.4, "id": 3}, '
                    '{"h_1": "e", "h2": 5, "h3": 5.5, "id": 4}, '
                    '{"h_1": "f", "h2": 6, "h3": 6.6, "id": 5}, '
                    '{"h_1": "g", "h2": 7, "h3": 7.7, "id": 6}, '
                    '{"h_1": "h", "h2": 8, "h3": 8.8, "id": 7}, '
                    '{"h_1": "i", "h2": 9, "h3": 9.9, "id": 8}, '
                    '{"h_1": "j", "h2": 10, "h3": 10.1, "id": 9}] } />'
                )
            ),
        ),
        (
            {
                "data": {"file": str(datafile), "nrows": 2},
                "src": False,
                "pageSize": 2,
            },
            {},
            1,
            (
                f'{TAB}<DataTable\n'
                + TAB * 2
                + 'pageSize={ 2 }\n'
                + TAB * 2
                + (
                    'data={ [{"h_1": "a", "h2": 1, "h3": 1.1235, "id": 0}, '
                    '{"h_1": "b", "h2": 2, "h3": 2.2, "id": 1}] } />'
                )
            ),
        ),
    ],
    ids=[
        "Test case 1: src False",
        "Test case 2: src True",
        "Test case 3: level 1",
    ],
)
def test_render_table(cont, job, level, expected):
    result = _render_table(cont, job, level)
    assert result == expected


@pytest.mark.parametrize(
    "cont, job, level, expected",
    [
        (
            {
                "src": str(imgpath),
            },
            {},
            0,
            (
                f'<Image\n{TAB}src="%(imgpath)s"\n'
                f'{TAB}width={{ 526 }}\n{TAB}height={{ 360 }} />'
            ) % {"imgpath": imgpath},
        ),
        (
            {
                "src": str(imgpath),
                "width": 100,
                "height": 100,
            },
            {},
            0,
            (
                f'<Image\n{TAB}src="%(imgpath)s"\n{TAB}width={{ 100 }}\n'
                f'{TAB}height={{ 100 }} />'
            ) % {"imgpath": imgpath},
        ),
        (
            {
                "src": str(imgpath),
                "width": 100,
                "height": 100,
                "title": "Title1",
            },
            {},
            1,
            (
                f'{TAB}<Image\n{TAB * 2}src="%(imgpath)s"\n{TAB * 2}width={{ 100 }}\n'
                f'{TAB * 2}height={{ 100 }}\n{TAB * 2}title="Title1" />'
            ) % {"imgpath": imgpath},
        ),
    ],
    ids=[
        "Test case 1: level 0",
        "Test case 2: level 0",
        "Test case 3: level 1",
    ],
)
def test_render_image(cont, job, level, expected, request):
    result = _render_image(cont, job, level)
    assert result == expected


@pytest.mark.parametrize(
    "cont, job, level, expected",
    [
        (
            {
                "name": "Name1",
                "descr": "Desc1",
                "src": str(imgpath),
            },
            {},
            0,
            (
                '<div>\n'
                f'{TAB}<Descr title="Name1" class="pipen-report-table-image-descr"'
                '>Desc1</Descr>\n'
                f'{TAB}<Image\n'
                f'{TAB * 2}src="%(imgpath)s"\n'
                f'{TAB * 2}class="pipen-report-table-image"\n'
                f'{TAB * 2}width={{ 526 }}\n'
                f'{TAB * 2}height={{ 360 }} />\n'
                '</div>'
            ) % {"imgpath": imgpath},
        ),
        (
            {
                "name": "Name2",
                "descr": "Desc2",
                "src": str(imgpath),
                "width": 100,
                "height": 100,
            },
            {},
            0,
            (
                '<div>\n'
                f'{TAB}<Descr title="Name2" class="pipen-report-table-image-descr"'
                '>Desc2</Descr>\n'
                f'{TAB}<Image\n'
                f'{TAB * 2}src="%(imgpath)s"\n'
                f'{TAB * 2}width={{ 100 }}\n'
                f'{TAB * 2}height={{ 100 }}\n'
                f'{TAB * 2}class="pipen-report-table-image" />\n'
                '</div>'
            ) % {"imgpath": imgpath},
        ),
        (
            {
                "name": "Name3",
                "descr": "Desc3",
                "src": str(imgpath),
                "width": 100,
                "height": 100,
                "alt": "Title3",
            },
            {},
            1,
            (
                f'{TAB}<div>\n'
                f'{TAB * 2}<Descr title="Name3" class="pipen-report-table-image-descr"'
                '>Desc3</Descr>\n'
                f'{TAB * 2}<Image\n'
                f'{TAB * 3}src="%(imgpath)s"\n'
                f'{TAB * 3}width={{ 100 }}\n'
                f'{TAB * 3}height={{ 100 }}\n'
                f'{TAB * 3}alt="Title3"\n'
                f'{TAB * 3}class="pipen-report-table-image" />\n'
                f'{TAB}</div>'
            ) % {"imgpath": imgpath},
        ),
    ],
    ids=[
        "Test case 1: level 0",
        "Test case 2: level 0",
        "Test case 3: level 1",
    ],
)
def test_render_table_image(cont, job, level, expected):
    result = _render_table_image(cont, job, level)
    assert result == expected


def test_ui_flat():
    contents = [
        {
            "kind": "tag",
            "tag": "div",
            "slot": "abc",
        },
        {
            "kind": "descr",
            "content": "Content1",
        },
    ]
    result = _ui_flat(contents, {}, 0)
    assert result == (
        '<div>abc</div>\n'
        '<Descr>Content1</Descr>'
    )


def test_ui_dropdown_switcher():
    contents = [
        {
            "kind": "tag",
            "tag": "div",
            "slot": "abc",
            "ds_name": "Item 1",
        },
        {
            "ds_name": "Item 2",
        },
    ]
    result = _ui_dropdown_switcher(contents, {}, 0)
    assert result == (
        '<Dropdown\n'
        f'{TAB}selectedId="0"\n'
        f'{TAB}items={{ [{{"id": "0", "text": "Item 1"}}, {{"id": "1", "text": "Item 2"}}] }}\n'
        f'{TAB}on:select="{{ ({{detail}}) => {{'
        '    const conents = document.getElementsByClassName('
        '      \'pipen-report-ds-content-0\''
        '    );'
        '    for (const content of conents) {'
        '       content.style.display = \'none\';'
        '    }'
        '    document.getElementById('
        '      \'pipen-report-ds-content-0-\' + detail.selectedId'
        '    ).style.display = \'block\';} }" />\n'
        '<div id="pipen-report-ds-content-0-0" class="pipen-report-ds-content-0" style="">\n'
        '  <div>abc</div>\n'
        '</div>\n'
        '<div id="pipen-report-ds-content-0-1" class="pipen-report-ds-content-0" style="display: none;" />'
    )


def test_ui_table_of_images():
    contents = [
        {
            "kind": "table_image",
            "name": "Name1",
            "descr": "Desc1",
            "src": str(imgpath),
        },
        {
            "name": "Name2",
            "descr": "Desc2",
            "src": str(imgpath),
        },
        "Content3",
    ]
    contents2 = deepcopy(contents)
    result = _ui_table_of_images(contents, {}, 0)
    assert result == (
        '<div class="pipen-report-table-of-images" '
        'style="grid-template-columns: repeat(2, auto); ">\n'
        f'{TAB}<div>\n'
        f'{TAB * 2}<Descr title="Name1" class="pipen-report-table-image-descr"'
        '>Desc1</Descr>\n'
        f'{TAB * 2}<Image\n'
        f'{TAB * 3}src="%(imgpath)s"\n'
        f'{TAB * 3}class="pipen-report-table-image"\n'
        f'{TAB * 3}width={{ 526 }}\n'
        f'{TAB * 3}height={{ 360 }} />\n'
        f'{TAB}</div>\n'
        f'{TAB}<div>\n'
        f'{TAB * 2}<Descr title="Name2" class="pipen-report-table-image-descr"'
        '>Desc2</Descr>\n'
        f'{TAB * 2}<Image\n'
        f'{TAB * 3}src="%(imgpath)s"\n'
        f'{TAB * 3}class="pipen-report-table-image"\n'
        f'{TAB * 3}width={{ 526 }}\n'
        f'{TAB * 3}height={{ 360 }} />\n'
        f'{TAB}</div>\n'
        f'{TAB}<div>Content3</div>\n'
        '</div>'
    ) % {"imgpath": imgpath}
    result = _ui_table_of_images(contents2, {}, 0, 2)
    assert result == (
        '<div '
        'class="pipen-report-table-of-images" '
        'style="grid-template-columns: repeat(2, auto); ">\n'
        f'{TAB}<div>\n'
        f'{TAB * 2}<Descr title="Name1" class="pipen-report-table-image-descr"'
        '>Desc1</Descr>\n'
        f'{TAB * 2}<Image\n'
        f'{TAB * 3}src="%(imgpath)s"\n'
        f'{TAB * 3}class="pipen-report-table-image"\n'
        f'{TAB * 3}width={{ 526 }}\n'
        f'{TAB * 3}height={{ 360 }} />\n'
        f'{TAB}</div>\n'
        f'{TAB}<div>\n'
        f'{TAB * 2}<Descr title="Name2" class="pipen-report-table-image-descr"'
        '>Desc2</Descr>\n'
        f'{TAB * 2}<Image\n'
        f'{TAB * 3}src="%(imgpath)s"\n'
        f'{TAB * 3}class="pipen-report-table-image"\n'
        f'{TAB * 3}width={{ 526 }}\n'
        f'{TAB * 3}height={{ 360 }} />\n'
        f'{TAB}</div>\n'
        f'{TAB}<div>Content3</div>\n'
        '</div>'
    ) % {"imgpath": imgpath}

    # wrong kind
    contents = [
        {
            "kind": "xx",
            "name": "Name1",
            "descr": "Desc1",
            "src": str(imgpath),
        },
    ]
    with pytest.raises(ValueError):
        _ui_table_of_images(contents, {}, 0)


def test_ui_tabs():
    contents = [
        {
            "kind": "tab",
            "title": "Title1",
            "contents": [
                {
                    "kind": "tag",
                    "tag": "div",
                    "slot": "abc",
                },
                {
                    "kind": "descr",
                    "content": "Content1",
                },
            ],
        },
        {
            "kind": "tab",
            "title": "Title2",
            "contents": [
                {
                    "kind": "tag",
                    "tag": "div",
                    "slot": "abc",
                },
                {
                    "kind": "descr",
                    "content": "Content2",
                },
            ],
        },
    ]
    result = _ui_tabs(contents, {}, 0)
    assert result == (
        '<Tabs>\n'
        f'{TAB}<Tab label="Title1" />\n'
        f'{TAB}<Tab label="Title2" />\n'
        f'{TAB}<svelte:fragment slot="content">\n'
        f'{TAB * 2}<TabContent>\n'
        f'{TAB * 3}<div>abc</div>\n'
        f'{TAB * 3}<Descr>Content1</Descr>\n'
        f'{TAB * 2}</TabContent>\n'
        f'{TAB * 2}<TabContent>\n'
        f'{TAB * 3}<div>abc</div>\n'
        f'{TAB * 3}<Descr>Content2</Descr>\n'
        f'{TAB * 2}</TabContent>\n'
        f'{TAB}</svelte:fragment>\n'
        '</Tabs>'
    )

    # wrong kind
    contents = [
        {
            "kind": "xx",
            "title": "Title1",
            "contents": [
                {
                    "kind": "tag",
                    "tag": "div",
                    "slot": "abc",
                },
                {
                    "kind": "descr",
                    "content": "Content1",
                },
            ],
        },
    ]
    with pytest.raises(ValueError):
        _ui_tabs(contents, {}, 0)


def test_ui_accordion():
    contents = [
        {
            "kind": "accordion",
            "title": "Title1",
            "contents": [
                {
                    "kind": "tag",
                    "tag": "div",
                    "slot": "abc",
                },
                {
                    "kind": "descr",
                    "content": "Content1",
                },
            ],
        },
        {
            "kind": "accordion",
            "title": "Title2",
            "contents": [
                {
                    "kind": "tag",
                    "tag": "div",
                    "slot": "abc",
                },
                {
                    "kind": "descr",
                    "content": "Content2",
                },
            ],
        },
    ]
    result = _ui_accordion(contents, {}, 0)
    assert result == (
        '<Accordion align="start">\n'
        f'{TAB}<AccordionItem title="Title1" open>\n'
        f'{TAB * 2}<div>abc</div>\n'
        f'{TAB * 2}<Descr>Content1</Descr>\n'
        f'{TAB}</AccordionItem>\n'
        f'{TAB}<AccordionItem title="Title2">\n'
        f'{TAB * 2}<div>abc</div>\n'
        f'{TAB * 2}<Descr>Content2</Descr>\n'
        f'{TAB}</AccordionItem>\n'
        '</Accordion>'
    )

    # wrong kind
    contents = [
        {
            "kind": "xx",
            "title": "Title1",
            "contents": [
                {
                    "kind": "tag",
                    "tag": "div",
                    "slot": "abc",
                },
                {
                    "kind": "descr",
                    "content": "Content1",
                },
            ],
        },
    ]
    with pytest.raises(ValueError):
        _ui_accordion(contents, {}, 0)


@pytest.mark.parametrize(
    "cont, func",
    [
        ({"kind": "accordion", "title": "Title", "contents": []}, _render_accordion),
        ({"kind": "tab", "contents": []}, _render_tab),
        ({"kind": "descr"}, _render_descr),
        ({"kind": "error"}, _render_error),
        ({"kind": "list"}, _render_list),
        ({"kind": "table", "data": {"file": str(datafile)}}, _render_table),
        ({"kind": "image", "src": str(imgpath)}, _render_image),
        ({"kind": "image", "src": "xxx"}, _render_image),
        ({"kind": "table_image", "src": str(imgpath)}, _render_table_image),
    ],
    ids=[
        "Test case 2: accordion",
        "Test case 3: tab",
        "Test case 4: descr",
        "Test case 5: error",
        "Test case 6: list",
        "Test case 7: table",
        "Test case 8: image",
        "Test case 8.1: table_image (src nonexisitng)",
        "Test case 9: table_image",
    ],
)
def test_render_component(cont, func):
    result = render_component(cont, {}, 0)
    del cont["kind"]
    assert result == func(cont, {}, 0)


def test_render_unknown_kind():
    with pytest.raises(ValueError):
        render_component({"kind": "unknown"}, {}, 0)


def test_render_table_no_file():
    with pytest.raises(ValueError):
        render_component({"kind": "table", "data": {}}, {}, 0)


def test_render_ui():
    contents = [
        {
            "kind": "descr",
            "content": "Content3",
        },
    ]
    contents2 = deepcopy(contents)
    result = render_ui(contents, "flat", {})
    assert result == _ui_flat(contents2, {}, 0)

    contents = [
        {
            "kind": "table_image",
            "name": "Name1",
            "descr": "Desc1",
            "src": str(imgpath),
        },
    ]
    contents2 = deepcopy(contents)
    result = render_ui(contents, "table_of_images", {})
    assert result == _ui_table_of_images(contents2, {}, 0)

    contents = [
        {
            "kind": "tab",
            "title": "Title1",
            "contents": [
                {
                    "kind": "tag",
                    "tag": "div",
                    "slot": "abc",
                },
                {
                    "kind": "descr",
                    "content": "Content1",
                },
            ],
        },
    ]
    contents2 = deepcopy(contents)
    result = render_ui(contents, "tabs", {})
    assert result == _ui_tabs(contents2, {}, 0)

    contents = [
        {
            "kind": "accordion",
            "title": "Title1",
            "contents": [
                {
                    "kind": "tag",
                    "tag": "div",
                    "slot": "abc",
                },
                {
                    "kind": "descr",
                    "content": "Content1",
                },
            ],
        },
    ]
    contents2 = deepcopy(contents)
    result = render_ui(contents, "accordion", {})
    assert result == _ui_accordion(contents2, {}, 0)

    # wrong ui
    with pytest.raises(ValueError):
        render_ui(contents, "unknown", {})


def test_report_job(tmp_path):
    job = {"index": 0, "outdir": tmp_path}
    tocfile = tmp_path / "report.json"
    toc = {
        "Heading1": {
            "Heading2": {
                "title": {
                    "flat": [
                        {
                            "kind": "descr",
                            "content": "Content1",
                        },
                    ],
                }
            }
        }
    }
    tocfile.write_text(json.dumps(toc))
    result = render_job(job)
    assert result == (
        '<!-- Generated by pipen_report.filters.report -->\n'
        '<h1>Heading1</h1>\n'
        '<h2>Heading2</h2>\n'
        '<h3>title</h3>\n'
        '<Descr>Content1</Descr>\n'
        '<!-- End of Generated by pipen_report.filters.report -->'
    )


def test_register():
    @register_component("my-component")
    def my_component(cont, job, level):
        return "my-component"

    assert render_component({"kind": "my-component"}, {}, 0) == "my-component"

    @register_ui("my-ui")
    def my_ui(contents, job, level):
        return "my-ui"

    assert render_ui([], "my-ui", {}) == "my-ui"
