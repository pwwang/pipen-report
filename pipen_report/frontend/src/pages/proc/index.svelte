<script>
    import ProcLayout from "$layouts/ProcLayout.svelte";
    import PageNavButton from "$components/PageNavButton.svelte";
    import ProcReport from "./proc.svelte";
    import toc from "./toc.json";
    import data from "../../data.json";

    export let name;
    export let page = 0;

    let isSideNavOpen = false;

    const proc = data.procs.filter(p => p.name == name)[0];
</script>

<ProcLayout
    bind:isSideNavOpen
    logo={name}
    logotext={proc.desc}
    versions={data.versions}
    procs={data.procs}
    pipeline_name={data.pipeline.name}
    report_toc={proc.report_toc}
    {toc}
    {page}
    >

    {#if page > 0}
    <PageNavButton dir="up" />
    {/if}

    <ProcReport />

    {#if page < proc.npages - 1 }
    <PageNavButton dir="down" />
    {/if}
</ProcLayout>
