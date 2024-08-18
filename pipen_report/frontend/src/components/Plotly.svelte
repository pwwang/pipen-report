<script>
    import Iframe from './Iframe.svelte';

    /** The properties of the image frame
     * @type {Object}
     */
    export let frameProps = { class: "pipen-report-plotly-frame" };

    /**
     * The source URL of the iframe
     * @type {string}
     */
    export let src;

    /**
     * The title of the iframe
     * @type {string}
     */
    export let title = 'about:blank';

    /**
     * The width of the iframe
     * @type {number}
     */
    export let width = 800;

    /**
     * The height of the iframe
     * @type {number}
     */
    export let height = 600;

    /**
     * The HTML element of the iframe
     * @type {HTMLIFrameElement}
     */
    let ref;

    if (!!!frameProps) {
        frameProps = {"style:position": "relative"};
    }

</script>

<div {...frameProps}>
    <Iframe
        {src}
        {title}
        {width}
        {height}
        containerClass="pipen-report-plotly-container"
        bind:ref
        resize="both"
        style="aspect-ratio: {width} / {height}"
        on:load={
            // trigger resize event to make the plot fill up the frame
            () => setTimeout(() => {
                ref.setAttribute('width', width - 1);
                ref.setAttribute('height', height - 1);
            }, 100)
        }
        />
</div>

<style>
    :global(.pipen-report-plotly-container) {
        background-color: transparent !important;
    }
    :global(.pipen-report-plotly-container iframe) {
        max-width: 55%;
    }
</style>
