"""Provide filters to transform the data"""

from typing import Optional, List, Union, Mapping, Callable, Any

import csv
import json
import warnings

FORMATTER_TYPE = Optional[Union[str, Callable, List[Union[str, Callable]]]]

def datatable(
        datafile,
        rows: Optional[int] = None,
        cols: Optional[Union[int, str, List[int], List[str]]] = None,
        fmtcols: Mapping[str, FORMATTER_TYPE] = None,
        rownames: bool = False,
        **kwargs
) -> str:
    """A filter to turn a sep-delimited file into json data for data table

    Args:
        datafile: The path to the file
        rows: Number of rows to truncate to
        cols: Number of columns to truncate to
        fmtcols: The format of the columns, using `{}.format()` syntax
            A dict to specify the format of the columns
        rownames: Whether the table has rownames, meaning
            `ncol(header) = ncol(data) - 1`
        **kwargs: Arguments passed to `csv.DictReader()`

    Warns:
        When there are > 100 rows or > 20 columns in the final data

    Returns:
        A json string
    """
    encoding = kwargs.pop('encoding', 'utf-8')
    if isinstance(cols, int):
        cols = list(range(cols))
    if isinstance(cols, str):
        cols = [cols]

    if rownames:
        with open(datafile, newline='', encoding=encoding) as fdata:
            reader = csv.DictReader(fdata, **kwargs)
            fieldnames = reader.fieldnames
            fieldnames.insert(0, '')
    else:
        fieldnames = None
    kwargs['fieldnames'] = fieldnames

    data = []
    data_append = data.append
    rowidx = 0
    with open(datafile, newline='', encoding=encoding) as fdata:
        reader = csv.DictReader(fdata, **kwargs)
        if fieldnames:
            # skip the fieldnames in file
            next(reader)
        if cols is not None:
            # convert to fieldname
            cols = [
                reader.fieldnames[col] if isinstance(col, int) else col
                for col in cols
            ]

            for col in cols:
                if col not in reader.fieldnames:
                    raise ValueError(f'{col} is not a valid fieldname')

        fmtcols = fmtcols or {}
        fmtcols2 = {}
        for key, fmt in fmtcols.items():
            if isinstance(key, int):
                key = reader.fieldnames[key]
            if key not in reader.fieldnames:
                raise ValueError(f'{key} is not a valid fieldname')
            fmtcols2[key] = fmt

        for row in reader:
            if rows and rowidx >= rows:
                break

            to_append = {
                key: _format(val, fmtcols2.get(key, None))
                for key, val in row.items()
                if cols is None or key in cols
            }
            data_append(to_append)
            rowidx += 1

        if len(row) > 20:
            warnings.warn(
                "There are more than 20 columns in the table, "
                "which may cause display issues. "
                "Consider using `| datatable: cols=...` to limit"
            )
        if rowidx > 100:
            warnings.warn(
                "There are more than 100 rows in the table, "
                "which may cause display issues. "
                "Consider using `| datatable: cols=...` to limit"
            )

        return '{%s}' % json.dumps(data)

def _format(val: Any, fmts: FORMATTER_TYPE) -> str:
    if not fmts:
        return val
    if not isinstance(fmts, (tuple, list)):
        fmts = [fmts]

    out = val
    try:
        for fmt in fmts:
            if callable(fmt):
                out = fmt(out)
            else:
                out = fmt.format(out)
    except (TypeError, ValueError):
        ...
    return out
