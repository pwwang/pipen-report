
## python-end rendering

A report template is first rendered with pipeline/process template engine (`liquid` and `jinja2` supoorted by default), which enables us to use process and job attributes in the template (ie. paths to input/output).

The avaiable data to render the template:

|Data|Meaning|
|-|-|
|`proc`|The process object. You can access its attributes by `proc.xxx`|
|`args`|A shortcut to `proc.args`, the arguments of the process|
|`jobs`|Jobs of the process. We can access `index`, `metadir`, `outdir`, `stdout_file`, `stderr_file`, `in`(alias `in_`) and `out` for each job|
|`job`/`job0`|A shortcut to `jobs[0]`, useful for single-job processes|

## frontend rendering

After python-end rendering, the template is sent to [`svelte`][1] for frontend rendering. Any valid `svelte` file is a valid report template.  You can even use a plain HTML elements in the template.

[1]: https://svelte.dev/
