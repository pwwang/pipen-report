<script>
    import { DataTable, Image } from "$components";
</script>

<h1>Sample information</h1>
<DataTable
    src={{job.out.samplefile | quote}}
    data={ {{job.out.samplefile | datatable: index_col=0}} }
/>

<h1>Statistics</h1>
<h2>Number of samples per group</h2>
<Image src={{job.outdir | joinpaths: "nsamples_per_group.png" | quote}} />

<h2>Number of samples per lane</h2>
<Image src={{job.outdir | joinpaths: "nsamples_per_lane.png" | quote}} />
