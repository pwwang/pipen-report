<script>
    import ImageInner from "./ImageInner.svelte";

    export let frameProps = { class: "pipen-report-image-frame" };
    export let width = 200;
    export let height = 100;
</script>

{#if !!frameProps}
    <div {...frameProps}>
        <ImageInner {...$$restProps}>
            <svelte:fragment slot="loading">
                <div
                    class="pipen-report-image-loading"
                    style="--preset-width: {width}; --preset-height: {height};"
                >
                    Image loading ...
                </div>
            </svelte:fragment>
            <svelte:fragment slot="error">
                <div
                    class="pipen-report-image-loading error"
                    style="--preset-width: {width}; --preset-height: {height};"
                >
                    Image loading error!
                </div>
            </svelte:fragment>
        </ImageInner>
    </div>
{:else}
    <ImageInner {...$$restProps}>
        <svelte:fragment slot="loading">
            <div
                class="pipen-report-image-loading"
                style="--preset-width: {width}; --preset-height: {height};"
            >
                Image loading ...
            </div>
        </svelte:fragment>
        <svelte:fragment slot="error">
            <div
                class="pipen-report-image-loading error"
                style="--preset-width: {width}; --preset-height: {height};"
            >
                Image loading error!
            </div>
        </svelte:fragment>
    </ImageInner>
{/if}
