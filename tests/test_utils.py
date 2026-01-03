from diot import Diot
from panpath import PanPath
from pipen import Proc
from pipen.defaults import CONFIG
from pipen_report.utils import _stringify, get_cloudpath, get_fspath, a_copy_all


def test__stringify(tmp_path):
    # Test case 1: List
    obj = [1, 2, 3]
    expected = "[1, 2, 3]"
    assert _stringify(obj) == expected

    # Test case 2: Tuple
    obj = (4, 5, 6)
    expected = "(4, 5, 6)"
    assert _stringify(obj) == expected

    # Test case 3: Dictionary
    obj = {"a": 1, "b": 2, "c": 3}
    expected = "{a: 1, b: 2, c: 3}"
    assert _stringify(obj) == expected

    # Test case 4: Callable
    def func():
        pass

    obj = func
    expected = "<callable func>"
    assert _stringify(obj) == expected

    # Test case 5: Proc
    class AProc(Proc):
        template = "liquid"
        input = "a:var"

    obj = AProc(
        pipeline=Diot(
            workdir=tmp_path,
            config=CONFIG,
        )
    )
    expected = "<Proc:AProc>"
    assert _stringify(obj) == expected

    # Test case 6: Other object
    obj = 123
    expected = "123"
    assert _stringify(obj) == expected


def test_get_cloudpath():
    assert get_cloudpath(PanPath("/path/to/file.txt"), "/cache/dir") is None
    assert (
        str(
            get_cloudpath(
                PanPath("/path/to/cache/gs/bucket/file.txt"), "/path/to/cache"
            )
        )
        == "gs://bucket/file.txt"
    )


def test_get_fspath():
    assert (
        str(get_fspath(PanPath("gs://bucket/file.txt"), "/path/to/cache"))
        == "/path/to/cache/gs/bucket/file.txt"
    )


async def test_a_copy_all(tmp_path):
    tmp_path = PanPath(tmp_path)
    src_file = tmp_path / "src_file.txt"
    await src_file.a_write_text("Hello, World!")

    dst_file = tmp_path / "dst_file.txt"
    await a_copy_all(src_file, dst_file)
    assert await dst_file.a_read_text() == "Hello, World!"

    src_dir = tmp_path / "src_dir"
    await src_dir.a_mkdir()
    await (src_dir / "file1.txt").a_write_text("File 1")
    await (src_dir / "file2.txt").a_write_text("File 2")

    dst_dir = tmp_path / "dst_dir"
    await a_copy_all(src_dir, dst_dir)
    assert await (dst_dir / "file1.txt").a_read_text() == "File 1"
    assert await (dst_dir / "file2.txt").a_read_text() == "File 2"
