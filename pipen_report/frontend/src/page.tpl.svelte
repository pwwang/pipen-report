<script>
    import ProcLayout from "../layouts/Proc.svelte"
    import ProcReport from "../procs/{{proc_slug}}.svelte"
    {% if report_toc %}
    import ProcReportToc from "../procs/{{proc_slug}}.toc.svelte"
    {% endif %}

    const proc_name = "{{proc.name}}";
    const proc_desc = "{{proc.desc}}";
    const pipeline_name = "{{proc.pipeline.name}}";
    const versions = `{{versions}}`;
    const procs = {{procs}};
    const report_toc = {{str(report_toc).lower()}};

</script>

<ProcLayout logo={proc_name} logotext={proc_desc} {versions} {procs} {pipeline_name} {report_toc}>
    {% if report_toc %}
    <ProcReportToc slot="toc" />
    {% endif %}
    <ProcReport />
</ProcLayout>
