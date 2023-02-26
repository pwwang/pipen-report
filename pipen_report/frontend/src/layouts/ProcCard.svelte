<script>
    import { ClickableTile } from "carbon-components-svelte";

    export let slug;
    export let name;
    export let desc;
</script>

<ClickableTile href="procs/{slug}/">
    <h2>{name}</h2>
    {desc}
</ClickableTile>
