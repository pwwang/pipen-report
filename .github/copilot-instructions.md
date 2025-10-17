# Copilot Instructions for pipen-report

## Project Overview

`pipen-report` is a report generation plugin for [pipen](https://github.com/pwwang/pipen), a pipeline framework. It generates interactive HTML reports from pipeline processes using a Svelte-based frontend compiled with Rollup.

## Architecture

### Core Components

1. **Plugin System** (`report_plugin.py`): Implements pipen's plugin hooks (`on_init`, `on_start`, `on_proc_done`, `on_complete`) to integrate report generation into the pipeline lifecycle
2. **ReportManager** (`report_manager.py`): Central orchestrator handling template rendering, frontend building, and cloud/local path synchronization
3. **Frontend** (`pipen_report/frontend/`): Svelte components built with Rollup, using Carbon Design System components
4. **Template Processing** (`preprocess.py`): Converts Svelte templates to reports, handles path resolution, paging, and TOC generation

### Key Data Flows

- **Pipeline → Reports**: Plugin hooks collect process data → ReportManager renders templates → Frontend builds static assets → Synced to output directory
- **Cloud Support**: Handles Google Cloud Storage, S3, Azure via `yunpath`/`cloudpathlib` with local caching in temporary directories
- **Path Resolution**: Templates reference job outputs → Preprocessor converts to relative URLs → Frontend loads resources correctly

## Critical Workflows

### Development Setup

```bash
# Install with dev dependencies
pip install -e '.[dev]'

# Configure frontend environment (required before running)
pipen report config --npm npm --nmdir ~/.pipen-report

# Install/update frontend dependencies
pipen report update
```

### Testing

```bash
# Run all tests with coverage (uses pytest-xdist for parallel execution)
pytest -vv -n auto --cov=pipen_report --cov-report term-missing

# Run specific test
pytest tests/test_example.py::test_example

# Example pipeline (generates reports in example/output/REPORTS)
python example/pipeline.py
```

### Frontend Development

- **Location**: `pipen_report/frontend/` contains the Svelte app
- **Build**: Managed by `ReportManager.build()`, uses `rollup.config.js.jinja` template
- **Components**: Located in `frontend/src/components/`, aliased as `$lib` or `$components` in templates
- **Node Requirements**: Node 18-20 (specified in `package.json` engines)

## Project-Specific Conventions

### Template Syntax

Reports use **Jinja2/Liquid with Svelte**:

```svelte
<script>
  import { Image, DataTable } from '$lib';
</script>

<!-- Jinja2 variables rendered server-side -->
<Image src="{{ job.out.image }}" />

<!-- Use filters for data processing -->
<DataTable data={ {{ job.out.table | datatable: sep="\t" }} } />
```

### Configuration System

- **Two levels**: Pipeline-level (affects all processes) vs Process-level (per-process override)
- **Storage**: `.pipen-report.toml` (local) or `~/.pipen-report.toml` (global)
- **Runtime**: Set via `plugin_opts` dict in pipen config

### Custom Filters

Register template filters in `filters.py` as dict entries:

```python
FILTERS = {
    'datatable': datatable,  # Converts CSV/TSV to JSON for DataTable component
    'markdown': markdown,    # Renders markdown to HTML
}
```

### Cloud Path Handling

- Uses `MountedPath` wrapper to abstract local/cloud paths
- **Critical**: Always check `isinstance(path, SpecCloudPath)` before operations
- **Patching**: `_patch_copier.py` prevents chmod failures on gcsfuse-mounted filesystems

### Report Paging

Process reports can split by H1 headings (`report_paging` option):

- `False`: Single page (default)
- `3`: Split into pages with 3 H1s each
- Implemented in `preprocess.preprocess()` using `H1_TAG` regex

## Integration Points

### Pipen Plugin Registration

Entry point in `pyproject.toml`:
```toml
[tool.poetry.plugins.pipen]
report = "pipen_report.report_plugin:PipenReport"
```

Disable with: `Pipen(..., plugins=['no:report'])`

### External Dependencies

- **copier**: Template copying with custom patching for cloud filesystems
- **Carbon Design**: UI components from `carbon-components-svelte`
- **temml**: Math rendering in reports
- **imagesize**: Automatic image dimension detection

### CLI Commands

Registered as `pipen_cli` plugin:

```bash
pipen report config    # Configure npm, nmdir, extlibs
pipen report update    # Install frontend dependencies
pipen report serve     # Serve generated reports locally
```

## Common Patterns

### Adding Components

1. Create in `frontend/src/components/`
2. Export from `components/index.js`
3. Use in templates via `import { YourComponent } from '$lib'`

### Adding Filters

1. Add function to `filters.py`
2. Add to `FILTERS` dict
3. Use in templates: `{{ value | your_filter: arg1, arg2 }}`

### Handling Job Outputs

Templates receive `job` object with `in` (inputs) and `out` (outputs). Access files:

```svelte
{{ job.out.image }}  <!-- Full path -->
{{ job.out.image | basename }}  <!-- Filename only -->
```

## Testing Considerations

- Tests use `tmp_path` fixtures for isolated output directories
- Example pipeline in `example/pipeline.py` demonstrates all features
- `test_example.py` runs full pipeline, validates generated reports
- Frontend tests not included (Svelte compilation tested via pipeline runs)
