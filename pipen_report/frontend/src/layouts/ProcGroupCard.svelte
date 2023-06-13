<script>
    import { Dropdown } from "carbon-components-svelte";

    export let name;
    export let desc;
    export let procs;

    const pgId = `__${name}`;

    const items = [
        {id: pgId, text: name, desc},
        ...procs.map(proc => ({id: proc.name, text: proc.name, desc: proc.desc}))
    ];
</script>

<Dropdown
    size="xl"
    hideLabel
    {items}
    selectedId={pgId}
    style='--desc: "{desc}";'
    on:select={e => {
        if (e.detail.selectedItem.id !== pgId) {
            window.location.href = `procs/${e.detail.selectedItem.id}/index.html`;
        }
    }}
    let:item
    >
    <h2>{item.text}</h2>
    {item.desc || ""}
</Dropdown>
