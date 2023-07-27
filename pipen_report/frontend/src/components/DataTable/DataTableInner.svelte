<script>
  import {
    DataTable,
    Pagination,
    Toolbar,
    ToolbarContent,
    ToolbarSearch,
    Button,
    Modal
  } from "carbon-components-svelte";
  import ColumnSelector from "./ColumnSelector.svelte";
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

  let allColumns = headers.map(h => ({...h, selected: true}));
  $: headers = allColumns.filter(col => col.selected);

  let page = 1;
  let pageSize = pageSizes[0];

  let value = "";
  let modal_open = false;
  let filteredRows = rows;
  $: if (value.length > 0) {
    filteredRows = rows.filter(
      (row) =>
        Object.values(row).filter(
          (x) => !!x && x.toString().includes(value)
        ).length > 0
    );
  } else {
    filteredRows = rows;
  }

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
          filteredRows.forEach((row) => {
            const vals = headers.map((col) => `"${row[col.key]}"`);
            dataMain.push(vals.join(","));
          });
          return dataTitle.join(",") + "\r\n" + dataMain.join("\r\n");
        })()
      );
    const filename =
      src.length > 0
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
  rows={filteredRows}
  {headers}
  {...$$restProps}
>
  <Toolbar size={toolbarSize}>
    <ToolbarContent>
      <ToolbarSearch persistent bind:value />
      <ColumnSelector bind:allColumns />
      <Button
        iconDescription={`Download current ${filteredRows.length} records (may be partial of the entire data)`}
        tooltipPosition="top"
        icon={DocumentDownload}
        on:click={downloadTable}
      />
      {#if !!src}
        <Button
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
  totalItems={filteredRows.length}
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
</style>