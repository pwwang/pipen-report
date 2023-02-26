"""Provides some filters"""
import re
from os import PathLike
from typing import Any, Iterable, Union
import pandas


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
    df = df.rename(lambda x: re.sub(r"[^\w]+", "_", x), axis='columns')
    # add id for sorting purposes
    if "id" not in df:
        df["id"] = range(df.shape[0])

    return df.to_json(orient="records", double_precision=double_precision)


FILTERS = {}
FILTERS["datatable"] = datatable
