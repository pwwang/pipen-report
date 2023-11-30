# CLI tools

List available CLI tools:

```shell
❯ pipen report --help
Usage: pipen report [-h] {config,update,serve} ...

CLI utility for pipen-report

Optional Arguments:
  -h, --help            show help message and exit

Subcommands:
    config              Configure pipen-report
    update              Install/Update the frontend dependencies
    serve               Serve the report
```

## config

Configure pipen-report. Note that these values can still be overwritten by the pipeline configurations at runtime.

```shell
❯ pipen report config --help
Usage: pipen report config [-h] [--local] [--list] [--extlibs EXTLIBS] [--npm NPM]
                                           [--nmdir NMDIR] [--nobuild]

Optional Arguments:
  -h, --help         show help message and exit
  --local, -l        Save the configuration locally (./.pipen-report.toml)? Otherwise, the
                     configuration will be saved globally in the user's home directory (~/.pipen-
                     report.toml). The local configuration has higher priority than the global
                     configuration. [default: False]
  --list             List the configuration [default: False]
  --extlibs EXTLIBS  External components to be used in the report
  --npm NPM          The path to npm [default: npm]
  --nmdir NMDIR      Where should the frontend dependencies installed?
                     By default, the frontend dependencies will be installed in frontend/ of the
                     python package directory. However, this directory may not be writable. In this
                     case, the frontend dependencies will be installed in the directory specified.
                     [default: /home/pwwang/github/pipen-report/pipen_report/frontend]
  --nobuild          Don't build the final report. If True only preprare the environment Say if you
                     want to do the building manually [default: False]
```

## update

Install/Update the frontend dependencies:

```shell
❯ pipen report update --help
Usage: pipen report update [-h]

Optional Arguments:
  -h, --help  show help message and exit
```

## serve

Serve the report:

```shell
❯ pipen report serve --help
Usage: pipen report serve [-h] [--port PORT] [--host HOST] --reportdir REPORTDIR

Required Arguments:
  --reportdir REPORTDIR, -r REPORTDIR
                        The directory of the reports, where the REPORTS/ directory is

Optional Arguments:
  -h, --help            show help message and exit
  --port PORT, -p PORT  The port to serve the report [default: 8525]
  --host HOST           The host to serve the report [default: 127.0.0.1]
```
