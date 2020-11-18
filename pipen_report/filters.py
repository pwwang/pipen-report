import csv
import json

def datatable(datafile, **kwargs):
    encoding = kwargs.pop('encoding', 'utf-8')
    rows = kwargs.pop('rows', None)
    cols = kwargs.pop('cols', None)
    with open(datafile, newline='', encoding=encoding) as fdata:
        reader = csv.DictReader(fdata, **kwargs)
        data = []
        rowidx = 0;
        if cols and isinstance(cols, int):
            cols = list(range(cols))
        if cols and isinstance(cols[0], int):
            cols = [reader.fieldnames[col] for col in cols]
        if cols:
            for col in cols:
                if col not in reader.fieldnames:
                    raise ValueError(f'{col} is not a valid fieldname')
        for row in reader:
            if rows and rowidx >= rows:
                break
            data.append({key: row[key] for key in cols} if cols else row)
            rowidx += 1

        return '{%s}' % json.dumps(data)
