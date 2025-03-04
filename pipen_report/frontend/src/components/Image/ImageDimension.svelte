<script>
    import { TooltipDefinition } from "carbon-components-svelte";

    /** The source of the image
     * @type {string}
     */
    export let src = "";

    /** The tooltip to show when hovering the icon
     * @type {string}
     */
    export let tip = "";

    // calculate width and height of the image
    let width = 0;
    let height = 0;
    let image = new Image();
    image.src = src;
    image.onload = () => {
        width = image.width;
        height = image.height;
    };
</script>

<TooltipDefinition
    tooltipText={tip}
    class="pipen-report-image-dimension"
    align="start"
    direction="bottom"
>
    {width}x{height}
</TooltipDefinition>

<style>
    :global(.pipen-report-image-dimension button) {
        font-size: 0.65rem !important;
        transform: scaleX(.6);
        font-weight: 500 !important;
        border-bottom: none !important;
    }
</style>
