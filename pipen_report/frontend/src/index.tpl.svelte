<script>
    import {
        Grid,
        Row,
        Column
    } from "carbon-components-svelte";
    import IndexLayout from "../layouts/Index.svelte";
    import ProcCard from "../layouts/ProcCard.svelte";

    const procs = {{procs}};
    const pipeline = {{pipeline}};
    const versions = `{{versions}}`;

</script>

<IndexLayout logo={pipeline.name} logotext={pipeline.desc} {versions}>
    <Grid>
    {#if procs.length < 10}
        {#each procs as proc}
        <Row>
            <Column>
                <ProcCard name={proc["name"]} slug={proc["slug"]} desc={proc["desc"]} />
            </Column>
        </Row>
        {/each}
    {:else}
        {#each Array(procs.length).keys().filter(n => n % 2 == 0) as i}
        <Row>
            <Column>
                <ProcCard name={procs[i]["name"]} slug={procs[i]["slug"]} desc={procs[i]["desc"]} />
            </Column>
            <Column>
                {#if i + 1 < procs.length}
                <ProcCard name={procs[i+1]["name"]} slug={procs[i+1]["slug"]} desc={procs[i+1]["desc"]} />
                {/if}
            </Column>
        </Row>
        {/each}
    {/if}
    </Grid>
</IndexLayout>
