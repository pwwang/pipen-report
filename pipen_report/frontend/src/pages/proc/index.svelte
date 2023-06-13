<script>
    import ProcLayout from "$layouts/ProcLayout.svelte";
    import PageNavButton from "$components/PageNavButton.svelte";
    import ProcReport from "./proc.svelte";
    import toc from "./toc.json";
    import data from "../../data.json";

    export let name;
    export let page = 0;

    let isSideNavOpen = false;

    let proc;
    for (const entry of data.entries) {
        if (entry.procs) {
            for (const p of entry.procs) {
                if (p.name == name) {
                    proc = p;
                    break;
                }
            }
        } else {
            if (entry.name == name) {
                proc = entry;
                break;
            }
        }
    }
</script>

<ProcLayout
    bind:isSideNavOpen
    logo={name}
    logotext={proc.desc}
    versions={data.versions}
    entries={data.entries}
    pipeline_name={data.pipeline.name}
    report_toc={proc.report_toc}
    runinfo={proc.runinfo}
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
