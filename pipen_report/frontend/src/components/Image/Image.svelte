<script>
    import ImageInner from "./ImageInner.svelte";

    /** The properties of the image frame
     * @type {Object}
     */
    export let frameProps = { class: "pipen-report-image-frame" };

    /** The width of the image
     * @type {number}
     */
    export let width = 300;

    /** The height of the image
     * @type {number}
     */
    export let height = 200;

    /** The source URL of the image
     * @type {string}
     */
    export let src;

    if (!!!frameProps) {
        frameProps = {"style:position": "relative"};
    }

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
