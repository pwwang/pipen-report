<script>
    import { createEventDispatcher } from "svelte";
    import { InlineLoading } from "carbon-components-svelte";

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
     * The frameborder of the iframe
     * @type {number}
     */
    export let frameborder = 0;

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
    export let ref;

    /**
     * The resize style of the iframe
     * @type {string}
     */
    export let resize = "none";

    /**
     * The classes passed to the container
     * @type {string}
     */
    export let containerClass = "";

    let loaded = false;
    const dispatch = createEventDispatcher();
</script>

<div class="pipen-report-iframe-container {containerClass}">
    {#if !loaded}
    <div class="pipen-report-iframe-indicator" style:width='{width}px' style:height='{height}px'>
        <InlineLoading description="Loading content ..." />
    </div>
    {/if}
    <iframe
        bind:this={ref}
        {title}
        {width}
        {height}
        {src}
        frameborder={frameborder}
        style:resize={resize}
        on:load={() => {loaded = true; dispatch('load');}}
        {...$$restProps}
        />
</div>

<style>
    .pipen-report-iframe-container {
        position: relative;
        background-color: #efefef;
    }

    .pipen-report-iframe-indicator {
        position: absolute;
        top: 0;
        left: 0;
        font-size: 1.2rem;
    }

    .pipen-report-iframe-indicator :global(.bx--inline-loading) {
        justify-content: center;
        height: 100%;
    }
</style>
