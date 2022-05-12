## 0.4.0

- ⬆️ Upgrade frontend deps
- ⬆️ Upgrade pipen to v0.3.0

## 0.3.1

- 📌 Pin dep and doc dep verions
- ✨ Allow injected jupyter html to collapse code
- 📝 Add docs for CLI tools
- 💥 Default title to the title tag instead of h1 for cli inject
- 🐛 Use on_init hook to init config
- ⬆️ Upgrade frontend deps, so no longer need to patch svelte for large report
- ✅ Add tests
- 🐛 Fix renaming report from process with name index


## 0.3.0

- 🐛 Fix preprocessing with tag attribute value is empty
- ✨ Implement a cli plugin for pipen to inject external html page to the report
- 📌 Pin doc dep verions

## 0.2.3

- Allow datatable filter to exclude columns

## 0.2.2

- 🐛 Fix no toc generated when no H1 in report but report_toc is True
- 🐛 Fix report without H1 not getting preprocessed


## 0.2.1

- 🔊 Warn when there are > sections in report but paging is disabled
- 🚑 Fix when there is no H1's in the report
- 🩹 De-highlight the H1's in TOC when there are H2's in there
- 📝 Update example report
- 📝 Add post install/update necessities in README.md


## 0.2.0

- ♻️ Front: Use the builtin pagination table from ccs (carbon-design-system/carbon-components-svelte#702)
- ✨ Implement backend report paging
- 💥 Change config item `report_logging` to `report_loglevel`
- ✨ Implement frontend for report paging

## 0.1.1

- 🐛 Add postinstall to patch svelte compiler

## 0.1.0

- ⬆️ Update frontend deps
- 🐛 Make a patch to svelte compiler to fix "Max Stack Size Exceeded for huge HTML" (sveltejs/svelte#4694)

## 0.0.15

- 🐛 Fix min ncols wrongly using number of rows of df in datatable filter

## 0.0.14

- Replace all irregular characters in df column names in datatable filter

## 0.0.13

- Preprocess `embed` tag

## 0.0.12

- 🐛 Fix #3 (same name toc link not working) and fix offset of toc links
- 🐛 Don't cache non-export processes (Fix #2);
- 🐛 Fix `report_force_export` not forcing process to export (#1)
- 🐛 Fix issues when dot in column names at frontend for `DataTable`
- ⬆️ Upgrade frontend dependencies


## 0.0.11

- ✨ Add process-level config `report_toc` to disable toc for a single process report


## 0.0.10

- 🐛 Fix larger nrows/ncols not working for datatable filter
- 🐛 Fix multiple column alignment in index page

## 0.0.9

- 🐛 Allow relative script path to be inherited

## 0.0.8

- 🩹 Expand the TOC by default

## 0.0.7

- 🐛 Fix non-tags in pre-processing
- ⬆️ Upgrade frontend deps
- 🩹 Fix background of theme selector

## 0.0.6

- 🩹 Don't initilize if pipeline init fails
- ⬆️ Upgrade pipen to 0.2+ in deps

## 0.0.5

- 🐛 Fix all procs other than those with report template to be included in the reports
- ✨ Add `report_order` to define process order in report


## 0.0.4

- 🐛 Add fontend/src/pages directory to the repo


## 0.0.3

- ✨ Set export to True if report template is provided for a process

## 0.0.2

- Refactor previous version with the frontend builtin.
