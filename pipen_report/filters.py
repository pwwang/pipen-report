import csv
import json

def datatable(datafile, **kwargs):
    encoding = kwargs.pop('encoding', 'utf-8')
    with open(datafile, newline='', encoding=encoding) as fdata:
        reader = csv.DictReader(fdata, **kwargs)
        data = list(reader)
        return '{%s}' % json.dumps(data)
