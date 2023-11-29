<script>
    export let title;
</script>

<div class="pipen-report-descr" {...$$restProps}>
    {#if title}
        <div class="pipen-report-descr-title">
            {title}
        </div>
    {/if}
    <slot />
</div>

<style>
    .pipen-report-descr {
        margin: 1rem 0;
        font-size: var(--cds-body-short-01-font-size, 1rem);
        font-weight: var(--cds-body-short-01-font-weight, 400);
        line-height: var(--cds-body-short-01-line-height, 1);
        letter-spacing: var(--cds-body-short-01-letter-spacing, 0);
        border-left: 6px solid var(--cds-background-hover);
        background-color: var(--cds-ui-01);
        padding: 8px 12px;
        color: var(--cds-text-secondary);
    }
    :global(.pipen-report-descr p) {
        font-size: inherit;
        font-weight: inherit;
        line-height: inherit;
        letter-spacing: inherit;
    }
    .pipen-report-descr-title {
        font-size: 110%;
        font-weight: bold;
        margin-bottom: 0.2rem;
    }
</style>
