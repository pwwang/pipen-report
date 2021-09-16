<script>
    import ProcLayout from "../layouts/Proc.svelte"
    import ProcReport from "../procs/{{proc_slug}}.svelte"
    import ProcReportToc from "../procs/{{proc_slug}}.toc.svelte"

    const proc_name = "{{proc.name}}";
    const proc_desc = "{{proc.desc}}";
    const pipeline_name = "{{proc.pipeline.name}}";
    const versions = `{{versions}}`;
    const procs = {{procs}};

</script>

<ProcLayout logo={proc_name} logotext={proc_desc} {versions} {procs} {pipeline_name}>
    <ProcReportToc slot="toc" />
    <ProcReport />
</ProcLayout>
