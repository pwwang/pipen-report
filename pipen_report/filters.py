"""Provides some filters"""
from os import PathLike
from typing import Any, Iterable, Union
import pandas


def datatable(
    path: PathLike,
    *args: Any,
    ncols: Union[int, Iterable] = None,
    nrows: Union[int, Iterable] = None,
    double_precision: int = 4,
    **kwargs: Any,
) -> str:
    """Read data from a file, using pandas.read_csv() and make it to json so
    js can handle it and render it with <DataTable />

    Args:
        path: the path to the data file
        *args: and
        **kwargs: Arguments pass to pandas.read_csv()
        ncols: and
        nrows: Either number of cols/rows to select or an iterable of indices
            or an iterable of column/index names
        double_precision: The precision for double numbers
            See also panadas.DataFrame.to_json()

    Returns:
        A json format of data
    """
    df = pandas.read_csv(path, *args, **kwargs)

    # use ncols and nrows to filter
    if nrows is None:
        nrows = df.shape[0]
    if ncols is None:
        ncols = df.shape[1]

    if isinstance(nrows, int):
        nrows = range(nrows)
    if isinstance(ncols, int):
        ncols = range(ncols)

    if all(isinstance(row, int) for row in nrows):
        nrows = df.index[nrows]
    if all(isinstance(col, int) for col in ncols):
        ncols = df.columns[ncols]

    df = df.loc[nrows, ncols]
    # add id for sorting purposes
    if "id" not in df:
        df["id"] = range(df.shape[0])
    return df.to_json(orient="records", double_precision=double_precision)


FILTERS = {}
FILTERS["datatable"] = datatable
