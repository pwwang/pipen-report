<script>
    import ImageInner from "./ImageInner.svelte";

    export let frameProps = { class: "pipen-report-image-frame" };
</script>

{#if !!frameProps}
    <div {...frameProps}>
        <ImageInner {...$$restProps} />
    </div>
{:else}
    <ImageInner {...$$restProps} />
{/if}
