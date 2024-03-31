<script>
    import { onMount } from "svelte";
    import { Dropdown } from "carbon-components-svelte";

    export let name;
    export let desc;
    export let procs;

    const pgId = `__${name}`;

    const items = [
        {id: pgId, text: `${name} ...`, desc},
        ...procs.map(proc => ({id: proc.name, text: proc.name, desc: proc.desc}))
    ];

    let direction = "bottom";
    let ref;

    onMount(() => {
        const rect = ref.getBoundingClientRect();
        const bottom_space = window.innerHeight - rect.bottom - rect.height - 10;
        const top_space = rect.top - rect.height - 10;

        if (bottom_space < 0 && top_space > 0) {
            direction = "top";
        }
    });

</script>

<Dropdown
    bind:ref
    {direction}
    size="xl"
    hideLabel
    {items}
    selectedId={pgId}
    class="procgroup"
    style='--desc: "{desc}";'
    on:select={e => {
        if (e.detail.selectedItem.id !== pgId) {
            window.location.href = `?proc=${e.detail.selectedItem.id}`;
        }
    }}
    let:item
    >
    <h2>{item.text}</h2>
    {item.desc || ""}
</Dropdown>

<style>
    :global(.bx--list-box__menu) {
        border-radius: 0.6rem;
        border: 1px solid var(--cds-border-subtle-selected);
    }
</style>
