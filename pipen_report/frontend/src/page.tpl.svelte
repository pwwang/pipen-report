<script>
    import ProcLayout from "../layouts/Proc.svelte"
    import ProcReport from "../procs/{{proc_slug}}.svelte"
    import ProcReportToc from "../procs/{{proc_slug}}.toc.svelte"

    const procs = {{procs}};
    const pipeline = {{pipeline}};

</script>

<ProcLayout logo={pipeline.name} logotext={pipeline.desc} {procs}>
    <ProcReportToc slot="toc" />
    <ProcReport />
</ProcLayout>
