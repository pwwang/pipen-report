<script>
    import { ClickableTile } from "carbon-components-svelte";

    export let name;
    export let desc;
</script>

<ClickableTile href="?proc={name}">
    <h2>{name}</h2>
    {desc || ""}
</ClickableTile>
