<script>

    import ProcLayout from "$layouts/Proc.svelte"
    import PageNavButton from "$components/PageNavButton.svelte"
    import ProcToc from "$layouts/ProcToc.svelte"
    import ProcReport from "./proc.svelte"
    import toc from "./toc.json"
    import data from "../../data.json"

    export let name;
    export let page = 0;

    const proc = data.procs.filter(p => p.name == name)[0];
</script>

<ProcLayout
    logo={name}
    logotext={proc.desc}
    versions={data.versions}
    procs={data.procs}
    pipeline_name={data.pipeline.name}
    report_toc={proc.report_toc}>
    {#if proc.report_toc}
        <ProcToc slot="toc" {toc} {page}  />
    {/if}

    {#if page > 0}
    <PageNavButton dir="up" />
    {/if}

    <ProcReport />

    {#if page < proc.npages - 1 }
    <PageNavButton dir="down" />
    {/if}
</ProcLayout>
