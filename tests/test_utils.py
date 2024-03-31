from diot import Diot
from pipen import Proc
from pipen.defaults import CONFIG
from pipen_report.utils import _stringify


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
