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
