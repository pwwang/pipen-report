# pipen-report

Report generation system for [`pipen`][1]

## Installation

```python
pip install -U pipen-report
```

## Usage

```python
from pipen import Proc, Pipen

class Figure(Proc):
    """Generate figures"""
    input_keys = ['a:var']
    input = [1,2,3]
    output = 'outfile:file:{{in.a}}.jpg'
    script = '''\
    wget https://picsum.photos/200/300 -O {{out.outfile}}
    '''
    plugin_opts = 'Figure.svx'

class Table(Figure):
    """Generate tables"""
    output = 'outfile:file:{{in.a}}.txt'
    script = '''\
    #!/usr/bin/env python

    outfile = "{{out.outfile}}"
    with open(outfile, 'w') as fout:
        fout.write("""\\
    id	first_name	last_name	email	gender	ip_address
    1	Lynda	Scirman	lscirman0@businessweek.com	Female	22.123.155.57
    2	Moll	Niset	mniset1@marketwatch.com	Female	6.154.75.63
    3	Jory	Mewitt	jmewitt2@delicious.com	Male	233.225.101.101
    4	Dukie	Onslow	donslow3@washington.edu	Male	238.209.40.250
    5	Carlee	Grasha	cgrasha4@cocolog-nifty.com	Female	22.65.237.2
    6	Leanora	Doughtery	ldoughtery5@ucoz.com	Female	54.41.211.142
    7	Winona	Levison	wlevison6@cornell.edu	Female	15.186.215.132
    8	Orrin	Baldick	obaldick7@miitbeian.gov.cn	Male	221.49.10.188
    9	Ingmar	Papez	ipapez8@dmoz.org	Male	225.88.240.74
    10	Arlena	Compford	acompford9@earthlink.net	Female	49.30.204.242
    11	Domenico	Lorinez	dlorineza@hatena.ne.jp	Male	106.63.35.124
    12	Yul	Bonifas	ybonifasb@nba.com	Male	198.152.245.214
    13	Tony	Antonignetti	tantonignettic@skype.com	Male	61.64.103.108
    14	Bayard	Gilhooley	bgilhooleyd@addtoany.com	Male	124.48.176.234
    15	Hillary	Ashbee	hashbeee@bbc.co.uk	Female	111.91.131.252
    16	Cherye	Spuffard	cspuffardf@amazon.com	Female	206.113.100.79
    17	Dorey	Lorraway	dlorrawayg@t.co	Female	179.210.96.234
    18	Iolande	McKilroe	imckilroeh@ustream.tv	Female	92.62.191.79
    19	Ermina	Woodroofe	ewoodroofei@independent.co.uk	Female	193.75.48.192
    20	Quill	Skoggins	qskogginsj@t.co	Male	157.11.232.242
    """)
    '''
    plugin_opts = 'Table.svx'

Pipen('Test pipeline',
      'Just for pipen-report testing').starts([Figure, Table]).run()
```

`Figure.svx`

```html
# Generated Figures

{% for job in jobs %}

## This is a very long heading for figure {{job.index}}

![Figure{{job.index}}]({{job.out.outfile}})

{% endfor %}

# Another very very veryvery veryvery very long heading at level 1

## Short one

### Third level

## Very very very very very very very long one

## Another short one
```

`Table.svx`

```html
<script>
import { DataTable } from "pipen-smelte";

</script>

# Heading 1

## SubHeading 2
<DataTable
    data="{{ job.out.outfile | @report.datatable: delimiter='\t' }}"
    datafile="{{ job.out.outfile }}"
    />

## SubHeading 3
<DataTable
    data="{{ jobs[1].out.outfile | @report.datatable: delimiter='\t', cols=['id', 'first_name', 'last_name'], rows=10 }}"
    datafile="{{ jobs[1].out.outfile }}"
    />
```

See [here][2] for the reports.

[1]: https://github.com/pwwang/pipen
[2]: https://pwwang.github.io/pipen-report
