# Configurations

Configurations should be set under `plugin_opts`.

Just like configurations for `pipen`, there are two levels of configuration items: process-level and pipeline-level.

Process-level configurations should set at process definition. They can, however, be initialized at pipeline creation or in a configuration file, then those will apply to ALL processes if they are not set at process definition.

Pipeline-level configurations are not set in configuration files or pipeline creation. Set values at process definition won't affect it.

## `report`

Process-level.

Default: `None`

The report template. If `None`, no report will be generated for this process.
If the template is a file, use a `file://` prefix: `file:///path/to/template`

## `report_order`

Process-level.

Default: `0`

The order of the process to show in the index page and app menu

## `report_toc`

Process-level.

Default: `True`

Whether add TOC (left-side navigation) to the process report

## `report_npm`

Pipeline-level.

Default: `"npm"`

The path to `npm`, in case you don't have it installed in `$PAT`

## `report_nmdir`

Pipeline-level.

Default: `"~/.pipen-report"`

Where to save the `node_modules` directory (frontend dependencies), or where to run `npm install`.
`pipen-report` will first try to run `npm install` at `frontend` of the package directory. However, if you don't have the write privileges to the directory (i.e. The package is installed by admin), we will try to run `npm install` in the given directory (`package.json` will be copied there).

Another way is that you install this package in `user` mode: `pip install --user -U pipen-report`

The frontend dependencies are install once, and will be shared across all pipelines.

## `report_nobuild`

Pipeline-level.

Default: `False`

Don't build the reports, but just setup the frontend environment. You can build the reports by yourself manually at `<pipeline-workdir>/<pipeline-name>/.report-workdir`

## `report_loglevel`

Pipeline-level

Default: `"info"`

The logging level of the `pipen-report` logger. It won't affect the pipen's main logger.

## `report_force_export`

Pipeline-level

Default: `True`

Force the process to export output when report template is given

## `report_no_collapse_pgs`

Pipeline-level

Default: `False` (collapse all procgroups)

Don't collapse procgroups in the report. This is useful when you want to see the processes of the procgroup in the index page. Could be either a procgroup name, a list of procgroup names or `True` (don't collapse any procgroups)

## `report_paging`

Process-level

Default: `False`

Break the process report into pages. They are split by `h1` tags, which has to be
top-level tags. For example:

```svelte
<script>
    // ...
</script>

<h1>Section1</h1>
content1

<h1>Section2</h1>
content2

<h1>Section3</h1>
content3
```

When `report_paging = 2`, then the report will be split into:


```svelte
<script>
    // ...
</script>

<h1>Section1</h1>
content1

<h1>Section2</h1>
content2
```

and

```svelte
<script>
    // ...
</script>

<h1>Section3</h1>
content3
```

Note that the TOC will still show all items and when clicking one of them, the right page will be shown.
