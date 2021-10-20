## Output directory structure

The reports (html files, assets, built js files, etc) will be saved at `<pipeline.outdir>/REPORTS`

You should export the whole output directory (`<pipeline.outdir>`) and refer the index of the report here: `<pipeline.outdir>/REPROTS/index.html`

## Frontend working directory structure

The working directory is located at `<pipeline_workdir>/<pipeline_name>/.report-workdir`

The subdirectoies and files are:

- `node_modules`

    The frontend dependencies, should be a symbolic link to the global `node_modules`

- `package.json`

    The packages defining the dependencies, linked to the one inside the package

- `pipen-report*.log`

    The log files

- `public`

    The public files and built files. Linked to `<pipeline.outdir>/REPORTS`

- `public/data`

    Usually, when the files are exported from the process, they will be saved at `<pipeline.outdir>`, otherwise `<pipeline-workdir>/<pipeline-name>/<proc-name>/<job-index>/output`. For those exported files, we can make relative path ".." to link them, however, for those not exported, there is no way for us to link them. So we make a copy of them in the `public/data` directory, and change the original link to the copied one.

- `rollup.config.*.js`

    The rollup configuration file to compile the reports for each process, include the index page.

- `src`

    The source files used to compile.
