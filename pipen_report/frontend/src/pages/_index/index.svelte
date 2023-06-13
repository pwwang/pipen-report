<script>
    import IndexLayout from "../../layouts/Index.svelte";
    import ProcCard from "../../layouts/ProcCard.svelte";
    import ProcGroupCard from "../../layouts/ProcGroupCard.svelte";

    export let entries;
    export let pipeline;
    export let versions;

</script>

<IndexLayout logo={pipeline.name} logotext={pipeline.desc} {versions}>
    <div class="bx--grid proc-list {entries.length < 10 ? "col-1" : "col-2"}">
        {#each entries as entry}
        <div>
            {#if entry.procs}
                <ProcGroupCard name={entry.name} desc={entry.desc} procs={entry.procs} />
            {:else}
                <ProcCard name={entry.name} desc={entry.desc} />
            {/if}
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

    .proc-list :global(.bx--list-box__menu-item),
    .proc-list :global(.bx--list-box__menu-item__option) {
        height: auto;
    }

    .proc-list :global(.bx--dropdown__wrapper) {
        height: 100%;
    }

    .proc-list :global(.bx--dropdown) {
        height: 100%;
        max-height: none;
        border-bottom: none;
    }
    .proc-list :global(.bx--dropdown span.bx--list-box__label) {
        margin: 0.5rem 0 0.2rem 0;
        font-size: var(--cds-productive-heading-05-font-size, 2rem);
        font-weight: var(--cds-productive-heading-05-font-weight, 400);
        line-height: var(--cds-productive-heading-05-line-height, 1.25);
        letter-spacing: var(--cds-productive-heading-05-letter-spacing, 0);
    }
    .proc-list :global(.bx--dropdown span.bx--list-box__label::after) {
        content: var(--desc);
        display: block;
        color: var(--cds-text-01, #161616);
        text-decoration: none;
        font-size: var(--cds-body-short-01-font-size, 0.875rem);
        font-weight: var(--cds-body-short-01-font-weight, 400);
        line-height: var(--cds-body-short-01-line-height, 1.28572);
        letter-spacing: var(--cds-body-short-01-letter-spacing, 0.16px);
    }
    .proc-list :global(.bx--list-box--expanded .bx--list-box__menu) {
        max-height: none !important;
    }
    .proc-list :global(.bx--list-box__menu-item[id^="__"]) {
        display: none;
    }
</style>