<script>
    import ProcLayout from "../layouts/Proc.svelte"
    import { PageNavButton } from "../components/PageNavButton"

    {% if page == 0 %}
    import ProcReport from "../procs/{{proc_slug}}.svelte"
    {% else %}
    import ProcReport from "../procs/{{proc_slug}}-part{{page}}.svelte"
    {% endif %}

    {% if report_toc %}
    {% if page == 0 %}
    import ProcReportToc from "../procs/{{proc_slug}}.toc.svelte"
    {% else %}
    import ProcReportToc from "../procs/{{proc_slug}}-part{{page}}.toc.svelte"
    {% endif %}
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

    {% if page > 0 %}
    <PageNavButton dir="up" />
    {% endif %}

    <ProcReport />

    {% if page < total_pages - 1 %}
    <PageNavButton dir="down" />
    {% endif %}

</ProcLayout>
