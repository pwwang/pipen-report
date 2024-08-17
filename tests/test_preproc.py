import pytest  # noqa

from pathlib import Path
from PIL import Image
from pipen_report.preprocess import (
    TAG_RE,
    _preprocess_slash_h,
    _path_to_url,
    _preprocess_relpath_tag,
    _preprocess_markdown,
    _preprocess_section,
    preprocess,
)
from . import run_pipeline


@pytest.mark.parametrize(
    "source, index, page, kind, text, expected",
    [
        (
            "<h1>Title 1</h1>",
            1,
            1,
            "h1",
            None,
            (
                '<h1>Title 1</h1><a id="prt-h1-1-title-1" class="pipen-report-toc-anchor"> </a>',
                {"slug": "prt-h1-1-title-1", "text": "Title 1", "children": [], "page": 1},
            ),
        ),
        (
            "<h2>Title 2</h2>",
            1,
            1,
            "h2",
            None,
            (
                '<h2>Title 2</h2><a id="prt-h2-1-title-2" class="pipen-report-toc-anchor"> </a>',
                {"slug": "prt-h2-1-title-2", "text": "Title 2", "children": [], "page": 1},
            ),
        ),
    ],
)
def test_preprocess_slash_h(source, index, page, kind, text, expected):
    assert _preprocess_slash_h(source, index, page, kind, text) == expected


@pytest.mark.parametrize(
    "path, absolute, relative_to, expected",
    [
        ("file0.txt", True, True, "../file0.txt"),
        ("proc1/file1.txt", True, False, "data/file1.*.txt"),
        ("some/other/file2.txt", True, True, "../some/other/file2.txt"),
        ("some/other/file3.txt", True, False, "data/file3.*.txt"),
        ("a/b/file4.txt", False, True, "a/b/file4.txt"),
        ("a/b/file5.txt", False, False, "a/b/file5.txt"),
        ("http://a/b.txt", False, True, "http://a/b.txt"),
        ("http://a/b.txt", False, False, "http://a/b.txt"),
        ("", False, True, ""),
        ("", False, False, ""),
    ],
)
def test_path_to_url(path, absolute, relative_to, expected, tmp_path):
    basedir = tmp_path / "the" / "basedir"
    datadir = basedir / "data"
    datadir.mkdir(parents=True, exist_ok=True)
    nonrelpath = tmp_path / "nonrelpath"
    nonrelpath.mkdir(parents=True, exist_ok=True)

    if absolute:
        if relative_to:  # relative to basedir.parent
            path = tmp_path / "the" / path
        else:
            path = nonrelpath / path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(path.name)

    output = _path_to_url(path, basedir)

    if absolute and not relative_to:
        expected = Path(list(basedir.glob(expected))[0]).relative_to(basedir).as_posix()

    assert output == expected

    if absolute and not relative_to:
        assert basedir.joinpath(expected).read_text() == path.name


@pytest.mark.parametrize(
    "tagstr, expected",
    [
        # no related attribute to handle
        ('<a title="abc" />', '<a title="abc" />'),
        ('<Link title="abc" href="https://example.com/" />', '<Link title="abc" href="https://example.com/" />'),
        ('<Download title="abc" href="{tmp_path}/the/file.txt">', '<Download title="abc" href="../file.txt">'),
        ('<Image src="{tmp_path}/the/file.png" download="{tmp_path}/the/file.png" width="100" />',
         '<Image src="../file.png" download="../file.png" width="100" />'),
        ('<Image src="{tmp_path}/the/file.png" download={{["{tmp_path}/the/file.png"]}} />',
         '<Image src="../file.png" download={ [{"src": "../file.png"}] } />'),
        ('<Image src="{tmp_path}/the/file.png" download={{ {{"src": "{tmp_path}/the/file.png", "tip": "A tip"}} }} />',
         '<Image src="../file.png" download={ [{"src": "../file.png", "tip": "A tip"}] } />'),
    ],
)
def test_preprocess_relpath_tag(tagstr, expected, tmp_path):
    basedir = tmp_path / "the" / "basedir"
    basedir.mkdir(parents=True, exist_ok=True)
    tagstr = tagstr.format(basedir=basedir, tmp_path=tmp_path)
    matching = TAG_RE.match(tagstr)
    assert _preprocess_relpath_tag(matching, basedir) == expected


def test_preprocess_relpath_tag_imagesize(tmp_path):
    basedir = tmp_path / "the" / "basedir"
    basedir.mkdir(parents=True, exist_ok=True)
    imgfile = tmp_path / "the" / "file.png"
    # make a fake 100x50 image
    Image.new("RGB", (100, 50)).save(imgfile)
    tagstr = f'<Image src="{imgfile}" />'
    matching = TAG_RE.match(tagstr)
    expected = '<Image src="../file.png" width={100} height={50} />'
    assert _preprocess_relpath_tag(matching, basedir) == expected


def test_prepocess_markdown():
    expected = '<h4>Header 4</h4>'
    source = "<Markdown>#### Header 4</Markdown>"
    assert _preprocess_markdown(source) == expected


def test_preprocess_section(tmp_path):
    source = "<h2>Subsection 1</h2><div>Content1</div><h2>Subsection 2</h2><div>Content2</div>"
    expected = (
        '<h2>Subsection 1</h2><a id="prt-h2-1-subsection-1" class="pipen-report-toc-anchor"> </a>'
        '<div>Content1</div><h2>Subsection 2</h2><a id="prt-h2-2-subsection-2" class="pipen-report-toc-anchor"> </a>'
        '<div>Content2</div>',
        [
            {"slug": "prt-h2-1-subsection-1", "text": "Subsection 1", "children": [], "page": 1},
            {"slug": "prt-h2-2-subsection-2", "text": "Subsection 2", "children": [], "page": 1},
        ],
    )
    assert _preprocess_section(source, 1, 1, tmp_path) == expected


def test_preprocess1(tmp_path):
    source = (
        "<h1>Section 1</h1>"
        "<h2>Subsection 1</h2><div>Content1</div><h2>Subsection 2</h2><div>Content2</div>"
        "<h1>Section 2</h1>"
        "<h2>Subsection 1</h2><div>Content1</div><h2>Subsection 2</h2><div>Content2</div>"
    )
    expected = (
        [
            '<h1>Section 1</h1><a id="prt-h1-0-section-1" class="pipen-report-toc-anchor"> </a>'
            '<h2>Subsection 1</h2><a id="prt-h2-0-subsection-1" class="pipen-report-toc-anchor"> </a>'
            '<div>Content1</div><h2>Subsection 2</h2><a id="prt-h2-1-subsection-2" class="pipen-report-toc-anchor"> </a>'
            '<div>Content2</div>',
            '<h1>Section 2</h1><a id="prt-h1-1-section-2" class="pipen-report-toc-anchor"> </a>'
            '<h2>Subsection 1</h2><a id="prt-h2-2-subsection-1" class="pipen-report-toc-anchor"> </a>'
            '<div>Content1</div><h2>Subsection 2</h2><a id="prt-h2-3-subsection-2" class="pipen-report-toc-anchor"> </a>'
            '<div>Content2</div>',
        ],
        [
            {
                "slug": "prt-h1-0-section-1",
                "text": "Section 1",
                "children": [
                    {"slug": "prt-h2-0-subsection-1", "text": "Subsection 1", "children": [], "page": 0},
                    {"slug": "prt-h2-1-subsection-2", "text": "Subsection 2", "children": [], "page": 0},
                ],
                "page": 0,
            },
            {
                "slug": "prt-h1-1-section-2",
                "text": "Section 2",
                "children": [
                    {"slug": "prt-h2-2-subsection-1", "text": "Subsection 1", "children": [], "page": 1},
                    {"slug": "prt-h2-3-subsection-2", "text": "Subsection 2", "children": [], "page": 1},
                ],
                "page": 1,
            },
        ],
    )
    assert preprocess(source, tmp_path, True, 1) == expected


def test_preprocess2(tmp_path):
    basedir = tmp_path / "the" / "basedir"
    basedir.mkdir(parents=True, exist_ok=True)
    imgfile = tmp_path / "the" / "PG1/placeholder.png"
    imgfile.parent.mkdir(parents=True, exist_ok=True)
    # make a fake 100x50 image
    Image.new("RGB", (100, 50)).save(imgfile)

    source = (
        """<script>
            import { Image, Descr } from '$lib';
        </script>
        <h1>Image</h1>
        <Descr>This is a description about the section.</Descr>
        <Image src="%s" download={ {"src": "%s", "tip": "Download the high resolution format"} } />"""
    ) % (imgfile, imgfile)
    expected = (
        [
            """<script>
            import { Image, Descr } from '$lib';
        </script>
        <h1>Image</h1><a id="prt-h1-0-image" class="pipen-report-toc-anchor"> </a>
        <Descr>This is a description about the section.</Descr>
        <Image src="../PG1/placeholder.png" download={ [{"src": "../PG1/placeholder.png", "tip": "Download the high resolution format"}] } width={100} height={50} />"""
        ],
        [
            {
                "slug": "prt-h1-0-image",
                "text": "Image",
                "children": [],
                "page": 0,
            }
        ],
    )
    assert preprocess(source, basedir, True, 1) == expected


# @pytest.mark.forked
def test_regular(tmp_path):
    run_pipeline("regular", _dir=tmp_path)
    report = tmp_path / "outdir" / "REPORTS" / "pages" / "_index.js"
    assert report.exists()


@pytest.mark.forked
def test_markdown(tmp_path):
    run_pipeline("markdown_", _dir=tmp_path)
    report = tmp_path.joinpath(
        "workdir",
        "Markdown-process",
        ".report-workdir",
        "src",
        "pages",
        "Process2",
        "proc.svelte",
    )
    assert "<h1>Process</h1>" in report.read_text()


@pytest.mark.forked
def test_extlibs(tmp_path):
    run_pipeline("extlibs", _dir=tmp_path)
    report = tmp_path / "outdir" / "REPORTS" / "pages" / "Index.js"
    text = report.read_text()
    assert "Hello world" in text
    assert "A link" in text
    assert "../Index/12.txt" in text
