<script>
    import ImageInner from "./ImageInner.svelte";

    export let frameProps = { class: "pipen-report-image-frame" };
    export let width = 300;
    export let height = 200;
    export let src;

    let div_style = `width: ${width}px; height: ${height}px; aspect-ratio: ${width} / ${height}`;
    let div_props = { ...$$restProps };
    if (div_props.style) {
        div_style = `${div_style}; ${div_props.style}`;
        delete div_props.style;
    }
</script>

{#if !!frameProps}
    <div {...frameProps}>
        <ImageInner {src} {...$$restProps}>
            <svelte:fragment slot="loading">
                <div
                    class="pipen-report-image-loading"
                    style={div_style}
                    {...div_props}
                >
                    Image loading ...
                </div>
            </svelte:fragment>
            <svelte:fragment slot="error">
                <div
                    class="pipen-report-image-loading error"
                    style={div_style}
                    {...div_props}
                >
                    Image loading error!
                </div>
            </svelte:fragment>
        </ImageInner>
    </div>
{:else}
    <ImageInner {src} {...$$restProps}>
        <svelte:fragment slot="loading">
            <div
                class="pipen-report-image-loading"
                style={div_style}
                {...div_props}
            >
                Image loading ...
            </div>
        </svelte:fragment>
        <svelte:fragment slot="error">
            <div
                class="pipen-report-image-loading error"
                style={div_style}
                {...div_props}
            >
                Image loading error!
            </div>
        </svelte:fragment>
    </ImageInner>
{/if}
