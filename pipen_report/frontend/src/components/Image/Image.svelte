<script>
    import ImageInner from "./ImageInner.svelte";

    export let frameProps = { class: "pipen-report-image-frame" };
    export let width = 300;
    export let height = 200;
    export let src;

    let div_style = `width: ${width}px; height: ${height}px; aspect-ratio: ${width} / ${height}`;
    let div_props = {
        ...$$restProps,
        class: [ $$restProps.class, "pipen-report-image-loading" ].filter(Boolean).join(" "),
        style: $$restProps.style ?
            `${$$restProps.style}; ${div_style}` :
            div_style
    };
    let div_error_props = {
        ...div_props,
        class: [ div_props.class, "error" ].join(" ")
    };
</script>

{#if !!frameProps}
    <div {...frameProps}>
        <ImageInner {src} {...$$restProps}>
            <svelte:fragment slot="loading">
                <div {...div_props}>Image loading ...</div>
            </svelte:fragment>
            <svelte:fragment slot="error">
                <div {...div_error_props}>Image loading error!</div>
            </svelte:fragment>
        </ImageInner>
    </div>
{:else}
    <ImageInner {src} {...$$restProps}>
        <svelte:fragment slot="loading">
            <div {...div_props}>Image loading ...</div>
        </svelte:fragment>
        <svelte:fragment slot="error">
            <div {...div_error_props}>Image loading error!</div>
        </svelte:fragment>
    </ImageInner>
{/if}
