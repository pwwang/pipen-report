Configurations should be set under `plugin_opts`.

Just like configurations for `pipen`, there are two levels of configuration items: process-level and pipeline-level.

Process-level configurations should set at process definition. They can, however, be initialized at pipeline creation or in a configuration file, then those will apply to ALL processes if they are not set at process definition.

Pipeline-level configurations are not set in configuration files or pipeline creation. Set values at process definition won't affect it.

## `report`

Process-level.

Default: `None`

The report template. If `None`, no report will be generated for this process.
If the template is a file, use a `file://` prefix: `file:///path/to/template`

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

## `report_logging`

Pipeline-level

Default: `"info"`

The logging level of the `pipen-report` logger. It won't affect the pipen's main logger.

## `report_forks`

Pipeline-level

Default: `None`

Number of cores used to build the reports. Since building reports for each processes are independent after the pipeline is done (all outputs are already generated), so that they can be parallelized.

`None` to use `pipline.config.forks`, the same as the number of cores used to run jobs in parallel.

## `report_force_export`

Pipeline-level

Default: `True`

Force the process to export output when report template is given
