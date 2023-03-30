<script>
    import IndexLayout from "../../layouts/Index.svelte";
    import ProcCard from "../../layouts/ProcCard.svelte";

    export let procs;
    export let pipeline;
    export let versions;

</script>

<IndexLayout logo={pipeline.name} logotext={pipeline.desc} {versions}>
    <div class="bx--grid proc-list {procs.length < 10 ? "col-1" : "col-2"}">
        {#each procs as proc}
        <div>
            <ProcCard name={proc["name"]} slug={proc["slug"]} desc={proc["desc"]} />
        </div>
        {/each}
    </div>
</IndexLayout>

<style>
    .proc-list {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        grid-gap: 0.1rem 1.6rem;
    }

    .proc-list.col-1 {
        grid-template-columns: repeat(1, 1fr);
    }

    .proc-list > div {
        min-height: 6.2rem;
    }
</style>