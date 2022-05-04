import pytest

from pathlib import Path
from pipen_report.filters import datatable


@pytest.fixture
def datafile():
    return Path(__file__).parent / "data" / "data.csv"


def test_datatable(datafile):
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
    assert out == (
        '[{"h_1":"a","h2":1,"id":0},'
        '{"h_1":"b","h2":2,"id":1}]'
    )

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
