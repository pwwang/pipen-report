<script>
  import {
    DataTable,
    Pagination,
    Toolbar,
    ToolbarContent,
    ToolbarSearch,
    Button,
    Modal,
    OverflowMenu,
    Checkbox
  } from "carbon-components-svelte";
  import ColumnDelete from "carbon-icons-svelte/lib/ColumnDelete.svelte";
  import CloudDownload from "carbon-icons-svelte/lib/CloudDownload.svelte";
  import DocumentDownload from "carbon-icons-svelte/lib/DocumentDownload.svelte";
  // replace this in the future with
  // https://github.com/carbon-design-system/carbon-components-svelte/blob/paginated-datatable/src/PaginatedDataTable/PaginatedDataTable.svelte
  // import PaginatedDataTable from "./PaginatedDataTable.svelte";
  /**
   * Set the size of the data table
   * @type {"compact" | "short" | "medium" | "tall" | "sm" | "small" | "lg" | "large" | "md"}
   */
  export let size = "sm";
  export let src = undefined;

  const sizeMapping = {
    sm: "short",
    small: "short",
    short: "short",
    md: "medium",
    medium: "medium",
    lg: "tall",
    large: "tall",
    tall: "tall",
    compact: "compact",
  };
  const toolBarSizeMapping = {
    short: "sm",
    compact: "sm",
    medium: "default",
    tall: "default",
  };
  size = sizeMapping[size];
  let toolbarSize = toolBarSizeMapping[size];

  /** Set to `true` to use zebra styles */
  export let zebra = true;
  /** Set to `true` for the sortable variant */
  export let sortable = true;
  export let rows = [];
  export let headers = [];
  export let pageSizes = [20, 50, 75, 100];
  export let pageSize = pageSizes[0];

  if (!pageSizes.includes(pageSize)) {
    pageSizes = [pageSize, ...pageSizes];
    pageSizes.sort((a, b) => a - b);
  }

  let allColumns = headers.map(h => ({...h, selected: true}));
  $: headers = allColumns.filter(col => col.selected);

  let page = 1;

  let value = "";
  let modal_open = false;
  let filteredRowIds = [];

  $: rowsWithIds = rows.map((row, i) => ({ ...row, id: row?.id ?? String(i) }));
  $: totalItems = value.length ? filteredRowIds.length : rowsWithIds.length;
  $: exportRows = value.length ? rowsWithIds.filter((r) => filteredRowIds.includes(r.id)) : rowsWithIds;

  const clouldDownload = (event) => {
    event.preventDefault();
    modal_open = true;
  };

  const download = (href, filename) => {
    const alink = document.createElement("a");
    alink.href = href;
    alink.download = filename;
    document.body.appendChild(alink);
    alink.click();
    document.body.removeChild(alink);
  };

  const downloadTable = () => {
    const href =
      "data:application/vnd.ms-excel;charset=utf-8,\ufeff" +
      encodeURIComponent(
        (function () {
          const dataTitle = headers.map((col) => col.value);
          const dataMain = [];
          exportRows.forEach((row) => {
            const vals = headers.map((col) => `"${row[col.key]}"`);
            dataMain.push(vals.join(","));
          });
          return dataTitle.join(",") + "\r\n" + dataMain.join("\r\n");
        })()
      );
    const filename =
      (src && src.length > 0)
        ? src.split("/").pop().split(".")[0] + ".xls"
        : "data-subset.xls";
    download(href, filename);
  };
</script>

<DataTable
  {size}
  {zebra}
  {sortable}
  {page}
  {pageSize}
  rows={rowsWithIds}
  {headers}
  {...$$restProps}
>
  <Toolbar size={toolbarSize}>
    <ToolbarContent>
      <ToolbarSearch persistent bind:value shouldFilterRows bind:filteredRowIds />
      <!-- ccs keeps the menu open for clicks inside the menu, so checking columns does not close it -->
      <OverflowMenu class="pipen-report-overflowmenu" size="sm" icon={ColumnDelete} iconDescription="Select visible columns ...">
        {#each allColumns as column}
          <li class="pipen-report-column-selector-item">
            <Checkbox bind:checked={column.selected} on:change={() => {allColumns = allColumns}} labelText={column.value} />
          </li>
        {/each}
      </OverflowMenu>
      <Button
        kind="ghost"
        iconDescription={`Download current ${exportRows.length} records (may be partial of the entire data)`}
        tooltipPosition="top"
        icon={DocumentDownload}
        on:click={downloadTable}
      />
      {#if !!src}
        <Button
          kind="ghost"
          iconDescription="Right click and save as to download the entire data"
          tooltipPosition="top"
          icon={CloudDownload}
          href={src}
          on:click={clouldDownload}
        />
      {/if}
    </ToolbarContent>
  </Toolbar>
</DataTable>
<Pagination
  bind:pageSize={pageSize}
  bind:page={page}
  pageSizes={pageSizes}
  totalItems={totalItems}
/>

<Modal passiveModal bind:open={modal_open} modalHeading="Downloading entire data" on:open on:close>
  <p>
    You must use "Save as" or "Save link as" from the context menu (by right-clicking the button) to download the entire data.
  </p>
</Modal>

<style>
  :global(.pipen-report-datatable-frame .bx--table-toolbar .bx--btn--icon-only--top .bx--assistive-text) {
    left: -100%;
  }
  :global(.pipen-report-overflowmenu.bx--overflow-menu) {
    height: 2rem;
    width: 3rem;
  }
  /* the toolbar sits inside the block shell, so the controls are quiet until hovered
     instead of three saturated blocks competing with the table */
  :global(.pipen-report-overflowmenu.bx--overflow-menu:hover) {
    background-color: var(--cds-hover-ui);
  }
  :global(.pipen-report-overflowmenu.bx--overflow-menu > svg) {
    fill: currentColor;
  }

  /* one size for every control in the toolbar row: carbon's icon-only button is 3rem
     square, which overflows the 2rem toolbar and drops the two download buttons below
     the column selector */
  :global(.bx--toolbar-content .bx--btn) {
    width: 2rem;
    min-width: 2rem;
    height: 2rem;
    min-height: 2rem;
    padding: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--cds-text-01);
  }
  :global(.bx--toolbar-content .bx--btn:hover) {
    background-color: var(--cds-hover-ui);
  }
  /* the overflow menu's own colour is a fixed #000 in carbon v10, so the icon stayed
     black in every theme */
  :global(.pipen-report-overflowmenu.bx--overflow-menu) {
    width: 2rem;
    min-width: 2rem;
    padding: 0;
    color: var(--cds-text-01);
  }
  .pipen-report-column-selector-item {
    display: flex;
    align-items: center;
    padding-bottom: 0.2rem;
    width: 100%;
    padding-left: 0.5rem;
  }
  .pipen-report-column-selector-item:hover {
    background-color: var(--cds-hover-ui);
  }
  .pipen-report-column-selector-item:first-child {
    padding-top: 0.4rem;
  }
  .pipen-report-column-selector-item:last-child {
    padding-bottom: 0.4rem;
  }
  :global(.pipen-report-column-selector-item .bx--checkbox-label) {
    width: 100%;
  }
  :global(.pipen-report-column-selector-item .bx--checkbox-label .bx--checkbox-label-text) {
    width: 100%;
    text-align: left;
  }
</style>