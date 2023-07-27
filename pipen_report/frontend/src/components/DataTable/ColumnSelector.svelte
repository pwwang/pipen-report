<script>
    import { Checkbox } from "carbon-components-svelte";
    import ColumnDelete from "carbon-icons-svelte/lib/ColumnDelete.svelte";
    // import Checkbox from "carbon-icons-svelte/lib/Checkbox.svelte";
    // import CheckboxChecked from "carbon-icons-svelte/lib/CheckboxChecked.svelte";
    import OverflowMenu from "./OverflowMenu.svelte";

    export let allColumns;
</script>

<OverflowMenu class="pipen-report-overflowmenu" persistentClickItems size="sm" icon={ColumnDelete} iconDescription="Select visible columns ...">
    {#each allColumns as column}
    <li class="pipen-report-column-selector-item">
        <Checkbox bind:checked={column.selected} on:change={() => {allColumns = allColumns}} labelText={column.value} />
    </li>
    {/each}
</OverflowMenu>

<style>
    :global(.pipen-report-overflowmenu.bx--overflow-menu) {
        height: 2rem;
        width: 3rem;
    }
    :global(.pipen-report-overflowmenu.bx--overflow-menu:not(.bx--overflow-menu--open)) {
        background-color: var(--cds-interactive-01);
    }
    :global(.pipen-report-overflowmenu.bx--overflow-menu:not(.bx--overflow-menu--open):hover) {
        background-color: var(--cds-hover-primary);
    }
    :global(.pipen-report-overflowmenu.bx--overflow-menu:not(.bx--overflow-menu--open):focus) {
        outline: none;
    }
    :global(.pipen-report-overflowmenu.bx--overflow-menu:not(.bx--overflow-menu--open) > svg) {
        fill: white;
    }
    .pipen-report-column-selector-item {
        display: flex;
        align-items: center;
        padding-bottom: 0.2rem;
        width: 100%;
        padding-left: 0.5rem;
    }
    .pipen-report-column-selector-item:hover {
        background-color: var(--cds-hover-ui);
    }
    .pipen-report-column-selector-item:first-child {
        padding-top: 0.4rem;
    }
    .pipen-report-column-selector-item:last-child {
        padding-bottom: 0.4rem;
    }
    :global(.pipen-report-column-selector-item .bx--checkbox-label) {
        width: 100%;
    }
    :global(.pipen-report-column-selector-item .bx--checkbox-label .bx--checkbox-label-text) {
        width: 100%;
        text-align: left;
    }
</style>
