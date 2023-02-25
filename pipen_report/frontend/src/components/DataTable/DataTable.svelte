<script>
    import DataTableInner from "./DataTableInner.svelte";

    export let frameProps = { class: "pipen-report-datatable-frame" };
    // data is something generated from pandas.DataFrame.to_json(orient="records")
    // [{"Sepal_Length":5.1,"Sepal_Width":3.5},{"Sepal_Length":4.9,"Sepal_Width":3.0}]
    export let data = {};
    // convert this to headers and rows
    export let headers = [];
    export let rows = [];

    if (headers.length + rows.length > 0 && data.length > 0) {
        throw "Can only specify `data` or `headers`/`rows` for `DataTable`!";
    }

    if (data.length > 0) {
        // use the header names itself as keys
        // slugify them?
        rows = data;
        headers = Object.keys(rows[0])
            .filter((key) => key !== "id")
            .map((key) => ({ key: key, value: key }));
    }
</script>

{#if !!!frameProps}
    <DataTableInner {headers} {rows} {...$$restProps} />
{:else}
    <div {...frameProps}>
        <DataTableInner {headers} {rows} {...$$restProps} />
    </div>
{/if}
