## CLI tools

List available CLI tools:

```shell
❯ pipen report

DESCRIPTION:
  CLI utility for pipen-report

USAGE:
  pipen report [OPTIONS] COMMAND [OPTIONS]

OPTIONAL OPTIONS:
  -h, --help                      - Print help information for this command

COMMANDS:
  inject                          - Inject an independent HTML page into a
                                    report
  help                            - Print help of sub-commands
```

### `inject`

Inject an independent HTML page into a report.

The page will be listed as a process tile in the index page.

A `Go-back` button will be injected to the page to go back to the index page.

If a page is exported from jupyter notebook, the input code blocks will be allowed to collapse by `--jupyter`. The default is `False`.
Note that if the HTML file is exported by `nbconvert` and you have input controls, you don't need this function. This is useful when the nodebook is exported by, say, `vscode-jupyter`.

```shell
❯ pipen report inject

DESCRIPTION:
  Inject an independent HTML page into a report

USAGE:
  pipen report inject --reportdir AUTO - PATH [OPTIONS]

OPTIONAL OPTIONS:
  -t, --title <STR>               - The title of the page
                                    Default: <1st H1 of the HTML page>
  -d, --desc <STR>                - The description/subtitle of the page
                                    Default: ''
  --jupyter [BOOL]                - Whether the HTML file is exported from
                                    jupyter notebook. Default: False
                                    If so, allow the input/code block to
                                    collapse.
                                    You don't need this if the HTML is exported
                                    by nbconvert with input controls.
  -h, --help                      - Print help information for this command

REQUIRED OPTIONS:
  -r, --reportdir <AUTO>          - The directory of the reports. Typically,
                                    /path/to/REPORTS
  POSITIONAL <PATH>               - The path to the HTML file to inject
```