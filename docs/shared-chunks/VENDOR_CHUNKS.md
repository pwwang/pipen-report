# Shared vendor chunks — frontend build architecture

A handover/design document for the shared-chunk build system in pipen-report.
Read this before touching anything in `report_manager.py` around the vendor
code, `rollup.config.js.jinja`, or the `_vendor` build. It describes what was
built, why it works, the invariants any change must preserve, and the known
limitations that are still open.

## TL;DR

Every report page is built by its own `npm run build -- --configProc=<page>`
call. Before this work, each build compiled the node_modules it uses
(carbon-components-svelte, svelte, icons, page-chat, …) **from scratch, once
per page** — total JS grew linearly with the number of pages.

Now, at pipeline start:

1. Python scans all report templates + the page chrome for node_modules
   imports (the "union" of what every page uses).
2. One build (`--configProc=_vendor`) compiles that union **once** into
   stable shared chunks under `public/pages/vendor/`, `_carbon/`, `_pkg/`.
3. Page builds make every bare node_modules import **external** and map it to
   the shared chunk path (`output.paths`), so they compile only their own
   code and import the shared chunks at runtime.
4. If **only one proc** has a report, there is nothing to share: the `_vendor`
   build is skipped and pages compile their own node_modules as before.

## Why it's possible

Report templates are jinja2/liquid, but their `<script>` sections are
**literal** — template variables appear only in markup (`src="{{ job.out.img }}"`),
never in imports. The rest of node_modules usage is in the page chrome
(layouts, PageNavButton, the two page shells), which are our own static
files. Both are scannable.

The union is a **superset**: every node_modules module any page uses. A
page's entry needs specific exports from `vendor/<lib>.js`; the union build
contains them all, so every page finds its exports. Tree-shaking still
applies — only what's actually imported is compiled.

## High-level flow

```
pipeline start ──► on_start (report_plugin.py)
                      │
                      ├─► collect_vendor_imports(pipen)        [report_manager.py]
                      │     count procs with report; ≤ 1 → skip everything
                      │     walk chrome + templates, follow relative/aliased
                      │       imports into local files (never node_modules)
                      │     merge names per specifier; expand carbon barrels
                      │     → self.vendor_imports / self._vendor_module_imports
                      │     → write src/vendor/index.js + src/vendor/modules/*.js
                      │       (only if content changed → _vendor_changed)
                      │
                      ├─► build_vendor_chunks(ulogger)
                      │     skip if not needed (single page: write empty
                      │       index.css, drop stale chunks)
                      │     skip if unchanged + outdir/pages/vendor exists
                      │     rmtree stale vendor/_carbon/_pkg (workdir+outdir)
                      │     npm run build -- --configProc=_vendor  (cwd=workdir)
                      │       → public/pages/{vendor,_carbon,_pkg,index.css}
                      │
                      ├─► build("_index")   (page build, imports shared chunks)
                      │     ... per-proc page builds the same
                      │
                      └─► sync_reports()  → workdir/public/pages → outdir/REPORTS/pages
```

Everything runs with `cwd = workdir` (e.g.
`/home/.../.pipen/Pipeline/.report-workdir/`); outputs land in
`public/pages/` and are synced to `outdir/REPORTS/pages/`. The `_vendor`
build always runs **before** any page build — that ordering is relied upon.

## File layout contract — why `vendor/`, `_carbon/`, `_pkg/`

After a multi-proc run, `pages/` contains:

```
pages/
├── index.css              # shared carbon css (compiled once by _vendor)
├── <proc>.js              # per-page entries (compile only page-local code)
├── <proc>.css
├── vendor/
│   ├── <pkg>.js                       # facades + code for non-carbon packages
│   ├── index.js                       # (or index-<hash>.js) union entry, unused
│   ├── carbon-components-svelte.js    # facade: barrel re-exports by name
│   └── carbon-components-svelte/src/...  # per-module facades (default export)
├── _carbon/                          # compiled carbon module code, one file
│   └── carbon-components-svelte/src/Accordion/Accordion.js
└── _pkg/
    └── temml.js                      # compiled temml code
```

The split exists because there are two kinds of chunks, and they cannot share
filenames:

- **Entry chunks** (`vendor/…` from `entryFileNames: 'vendor/[name].js'`) are
  the *contract with the pages*: pages import `./vendor/<key>.js` paths, and
  only an entry chunk exports **exactly** the names the page asks for —
  `default` for a subpath module, the named list for a package/barrel. A
  non-entry shared chunk exports the module's *internal variable name*
  (e.g. `Accordion_svelte`), which the page doesn't know about. The
  `src/vendor/modules/*.js` shims (`export { default } from '…'`) exist
  precisely to make rollup emit per-module entry chunks with the right name.
- **Shared chunks** hold the compiled module code. A module's code can only
  live in one chunk, so it must sit in a *different* file than the facade
  that re-exports it.

Why a separate directory for carbon/temml instead of just more `vendor/`
files? **Name collisions.** The `_vendor` build's `manualChunks` gives code
chunks predictable names; the catch-all rule is `vendor/<pkg>`. But:

- temml's module entry key is `temml` → entry file `vendor/temml.js`. If its
  code chunk were also named `vendor/temml.js`, rollup would have to rename
  one of them, breaking the page's import path → code goes to `_pkg/temml`.
- carbon's barrel facade lives at `vendor/carbon-components-svelte.js`
  (pages import the bare package from chrome files, which `optimizeImports`
  does *not* rewrite). The catch-all would name carbon code chunks the same
  → carbon code goes to `_carbon/<module-path>`, one chunk per component, so
  each page downloads only the components it uses.

**Sharing**: `_carbon/…` chunks are compiled once and loaded by every page
that references that component — all pages (including `_index`) import the
same facade, which imports the same code chunk.

## Build modes (rollup.config.js.jinja)

### `commonConfig(cssfile)`

Base config: svelte plugin (`optimizeImports` preprocess, `a11y-*` warnings
silenced), `optimizeCss`, alias (`$components`/`$component`/`$libs`/`$lib` →
`../../components`, `$layouts`/`$layout` → `../../layouts`, `$extlibs` →
`../../extlibs/<name>` when configured, `$ccs` → `carbon-components-svelte`),
`css({output: cssfile})`, node-resolve (browser, dedupe svelte), commonjs,
terser, json.

`onwarn` — important: pipen-report treats **any** `(!)` line in npm build
output as a build failure (`NPMBuildingError`), so everything expected must
be silenced here:

| code | why |
|---|---|
| `EMPTY_BUNDLE` | `_index` has no `svelte/internal` dependency when empty |
| `CIRCULAR_DEPENDENCY` in `node_modules/zod` | by page-chat's zod dep |
| `UNUSED_EXTERNAL_IMPORT` | paged procs split template sections; a page's imports are a superset of what its section uses |
| `INVALID_ANNOTATION` | zod v4 ships `@__PURE__` comments esbuild understands but rollup's parser doesn't; it removes the comment and moves on |

### `_vendor` mode (`--configProc=_vendor`)

- `input`: entries object — `index: 'src/vendor/index.js'` plus one entry per
  file in `src/vendor/modules/`, keyed by its path relative to
  `src/vendor/` (minus `.js`) — the key *is* the vendor path pages import.
- `output`: `format: 'system'`, `entryFileNames: 'vendor/[name].js'`,
  `chunkFileNames: '[name].js'` (stable, no content hash), **`minifyInternalExports: false`** — the page builds import these chunks from *outside* this build, so export names must survive (rollup mangles them by default, consistently only within one build).
- `manualChunks`: carbon subpath → `_carbon/<module-path>` (ext stripped),
  temml → `_pkg/temml`, everything else → `vendor/<pkg>`.
- css output `index.css` — carbon `all.css` + component styles, once for the
  whole report. `index.html` statically links `./pages/index.css`.

### Page builds (every `--configProc=<proc>`, incl. `_index`)

```js
const vendor = fs.existsSync('public/pages/_carbon');
```

The `_carbon` dir is the **vendor-mode marker** (see Invariants). When set:

- `external: (id, importer) => !!importer && vendor && !id.startsWith('.') &&
  !id.startsWith('/') && !id.startsWith('$') && !id.startsWith('\0') &&
  !id.endsWith('.css')` — bare specifiers (node_modules) are externalized
  before resolution, so they keep their raw id.
- `paths: vendorPath` — maps the raw id to the shared chunk:
  carbon subpath → `./vendor/<subpath-no-ext>.js`; else → `./vendor/<pkg>.js`.
- `noopCss` plugin replaces `.css` imports with `export default {}` (the css
  is already in `index.css`; without it every page would recompile it).

Without the marker (single-proc skip mode), none of the above apply — the
page compiles its own node_modules and css exactly as before the change.

## Python side (report_manager.py)

### `collect_vendor_imports(pipen)` — line ~485

1. Counts procs with a report: `(getattr(proc, "plugin_opts") or {}).get("report", False)`.
   `_index` does **not** count. If ≤ 1 → `self._vendor_needed = False`, return.
2. Walks the chrome: `src/layouts/*.svelte`, `components/PageNavButton.svelte`,
   `pages/proc/index.svelte`, `pages/_index/index.svelte`.
3. Walks every proc's report template: `file://` templates are resolved like
   `render_proc_report` does (via `get_base`, which returns the class that
   defined `plugin_opts["report"]`), and relative imports resolve against the
   rendered page dir `src/pages/<proc.name>/`.
4. `_walk_text`/`_walk_imports` (line ~700): for each import —
   - `./x` → `_resolve_rel` (adds `.js`/`.svelte`/`index.*` variants), recurse.
   - `$lib(s)`/`$component(s)`/`$layout(s)` → resolve against
     `src/components` / `src/layouts`, recurse. `$extlibs` → resolve against
     `src/extlibs/<name>` (symlinked into the workdir at setup, before this
     scan). `$ccs` → rewritten to the bare `carbon-components-svelte` import
     and kept. Unknown aliases / unresolvable targets → warn and **skip** (the
     module just stays compiled per page instead of shared).
   - bare specifier → kept as-is, never existence-checked (see Limitations).
5. Merges names per specifier (`_import_names`), keeps side-effect/`export *`
   statements once per module.
6. `_expand_carbon_barrels` (line ~617): maps each name imported from the
   `carbon-components-svelte`/`carbon-icons-svelte` barrel to the subpath
   module that exports it (read from the package's `src/index.js` /
   `lib/index.js` barrel) — the pages import carbon by subpath (the
   `optimizeImports` preprocess rewrites barrels), so the union must provide
   an entry per subpath module. The barrel entry itself is kept too (chrome
   `$ccs` imports are not rewritten). Unmappable names → warn (page may 404).
7. Splits into:
   - `vendor_imports` — non-carbon, no-`default` specifiers → one re-export
     line each in the main `src/vendor/index.js` entry.
   - `_vendor_module_imports` — carbon specifiers and anything with a
     `default` import → their own `src/vendor/modules/<key>.js` shim, named
     by `_vendor_key` (carbon subpath → ext stripped, else package root) —
     the file name is the vendor path the pages import.
   - If `svelte` is used, adds `export * from 'svelte/internal'` and
     `'svelte/internal/disclose-version'` — the svelte compiler injects these
     imports into every compiled component; they never appear in sources.
8. `_vendor_changed = await _write_vendor_input()` — writes only if changed.

### `build_vendor_chunks(ulogger)` — line ~809

1. `not _vendor_needed` → log "Only one report page, skipping shared chunk
   build.", rmtree stale `vendor`/`_carbon`/`_pkg` from workdir
   `public/pages` and outdir `pages`, ensure an **empty** `index.css` exists
   in both (index.html statically links it; a 404 would be worse than an
   empty file), return.
2. Cached-skip: `not _vendor_changed` **and** `outdir/pages/vendor` is a dir →
   "Shared chunks cached, skipping building." (pages never write vendor
   chunks, so no other invalidation is possible).
3. rmtree the whole shared-chunk area in workdir + outdir (build output keeps
   stale files between runs), then
   `_npm_run_build(cwd=self.workdir, proc="_vendor", ulogger, force_build=True,
   cached=False)` — the regular npm plumbing: log streaming, `(!)` detection
   → `NPMBuildingError`.

### Wiring

`report_plugin.py` `on_start`: create manager → `check_npm_and_setup_dirs` →
`init_pipeline_data` → if `entries` non-empty (not `--nobuild`):
`collect_vendor_imports(pipen)` → `build_vendor_chunks(UnifiedLogger(logger,
"_vendor"))` → `build("_index")` → `sync_reports()`.

## Single-proc skip mode

"When only one proc has a report, skip `_vendor`." Rationale: one page has
nothing to share; compiling its own node_modules avoids a second npm build
and keeps the page self-contained.

- Python: `_vendor_needed` = count of procs with report > 1 (the `_index`
  page does not count). If false, the union scan is skipped entirely.
- JS: page builds detect vendor mode via `fs.existsSync('public/pages/_carbon')`
  — **not** `public/pages/vendor`, which is a trap: page builds' own
  pre-existing `manualChunks` (`outputConfig`) emit hashed
  `vendor/<lib>-<hash>.js` chunks, so that dir exists in skip mode too. The
  first page build creates it, and a later page build would misdetect vendor
  mode and emit `paths`-mapped imports pointing at chunks that don't exist.
  `_carbon/` is written **only** by the `_vendor` build; page builds never
  create it.
- Skip mode also writes the empty `index.css` (both workdir and outdir) so
  the static `<link href='./pages/index.css'>` in index.html keeps working.

## Invariants — any change must preserve these

1. **Pages import `./vendor/<key>.js` and that exact file must exist** as an
   entry chunk of the `_vendor` build. `output.paths` (page side) and
   `entryFileNames` keys / `_vendor_key` (union side) must stay in sync.
2. **Entry chunk names must never collide with shared chunk names.** Code
   that would land on a facade path goes to `_carbon/` or `_pkg/` instead.
   If you move carbon/temml chunking, update both `manualChunks` and the
   `_carbon` marker.
3. **`minifyInternalExports: false` in the `_vendor` build** — pages import
   these chunks from outside the build.
4. **The `_vendor` build runs before every page build, in the same workdir.**
   Both the `_carbon` marker and the cache-skip logic rely on this.
5. **`src/vendor/` is written by Python before the `_vendor` build** and
   contains only re-exports of bare node_modules specifiers — relative
   imports are walked in Python, never compiled by the union build.
6. **`index.css` must always exist** in outdir `pages/` (real content in
   vendor mode, empty file in skip mode).
7. **Any `(!)` warning in npm output fails the build** — new expected rollup
   warnings must be added to `onwarn`, with a comment.
8. Chrome files are the scan's root set — adding a new chrome file that
   imports node_modules requires adding it to `start_files` in
   `collect_vendor_imports`.

## Verification

- Full suite: `python -m pytest tests/` — expect **98 passed**. Note: the
  uncommitted `package-lock.json` churn bumps carbon-preprocess-svelte to
  a version needing **Node 22** (`fs.globSync`); run tests on Node 22.
  Also: `.env` at the repo root holds GCS credentials that break some
  imports — move it aside before running pytest and restore it after.
- `dev/check-chunks.mjs <pages-dir> <entry.js>` — static check of a built
  report: every `System.register` dep exists, setter `[i]` is aligned with
  dep `[i]`, every name a setter requests is exported by the target chunk.
  String-aware (template literals, `${}`), register-param-aware (the export
  fn name is read from the source). Run against every `pages/*.js`.
- `dev/run-pages.mjs <pages-dir> <entry.js>` — execute a page end-to-end in
  a mini-SystemJS loader with DOM stubs (EventTarget, MutationObserver,
  ResizeObserver, localStorage, nonzero layout metrics, …). The export fn
  must return its value (rollup assigns `const k = _export(…)`), and the
  script ends with `process.exit(0)` (pages keep the event loop alive).
- Manual: serve the report (`pipen report serve -r <outdir>`), open both a
  multi-proc and a single-proc report in a browser; no console errors, no
  404s on `./vendor/*.js` / `./pages/index.css`.

Single-proc check: run `tests/pipelines/single.py <work> <out>` — expect the
log line "Only one report page, skipping shared chunk build.", no `_vendor`
npm run, empty `pages/index.css`, and each page self-contained (its hashed
`vendor/*-<hash>.js` chunks belong to that page only).

## Known limitations / open work

1. **Extlibs with vendored node_modules break the union build.**
   `extlibs/<name>/node_modules/<pkg>`: the scanner appends bare specifiers
   unconditionally, but the union file `src/vendor/index.js` resolves
   packages from `src/vendor/` upward, not inside the extlib → rollup
   "Could not resolve" → `(!)` → `NPMBuildingError` → whole report build
   aborts. (Skip mode is fine — no union.) *Proposed fix*: in
   `collect_vendor_imports`, only collect a bare specifier whose package
   root exists in the workdir's main `node_modules`; warn + skip otherwise.
2. **Dynamic `import('pkg')` silently 404s in vendor mode.** `_parse_imports`
   only matches static `import/export … from`. The page build's blanket
   `external` predicate still externalizes the bare id → mapped to
   `./vendor/<pkg>.js` which doesn't exist → SystemJS load failure for the
   whole page. *Proposed fix*: externalize a bare id only if its mapped
   chunk file exists (reuse `vendorPath` with `fs.existsSync` against
   `public/pages/`), falling back to per-page compilation. This fix also
   makes uncollected ids from (1) fall back correctly.
3. Extlibs' own code is always compiled per page (relative/`$extlibs`
   imports) — by design, unchanged from before this work.
4. Browser cache relies on stable chunk names — after rebuilding with
   changed templates, a hard refresh may be needed (same as page entries
   before this change).
5. `test_report_paging` is flaky on pipen 1.2.1 (`ProcMeta` runtime classes
   make `get_base` resolve `file://` templates against site-packages) —
   pre-existing, unrelated to this work.
6. `package-lock.json` churn (carbon-preprocess-svelte 0.11.38, Node 22) —
   pre-existing, keep out of feature commits.

## File map

| Where | What |
|---|---|
| `report_manager.py:485` | `collect_vendor_imports` — union scan + skip-vendor decision |
| `report_manager.py:46` | `_parse_imports` — import extraction (static only) |
| `report_manager.py:700` | `_walk_text`/`_walk_imports` — recursive alias/relative walk |
| `report_manager.py:617` | `_expand_carbon_barrels` — barrel → subpath mapping |
| `report_manager.py:772` | `_write_vendor_input` — `src/vendor/` union input |
| `report_manager.py:802` | `_vendor_key` — entry key = vendor path |
| `report_manager.py:809` | `build_vendor_chunks` — skip/cache logic + `_vendor` npm run |
| `report_plugin.py:93` | `on_start` — orchestration |
| `frontend/rollup.config.js.jinja` | `_vendor` mode, page-build external/paths/noopCss, `_carbon` marker |
| `frontend/public/index.html` | static `<link href='./pages/index.css'>` |
| `dev/check-chunks.mjs`, `dev/run-pages.mjs` | verification scripts (see Verification) |
