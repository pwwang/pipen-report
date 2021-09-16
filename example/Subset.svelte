<script>
    import { DataTable } from "@@";
</script>

<h1>Data table</h1>

<DataTable
    src="{{ job.out.outfile }}"
    data={ {{ job.out.outfile | datatable: nrows=100 }} }
    />
