<script>
    import { InlineLoading } from "carbon-components-svelte";

    export let src;
    export let title = 'about:blank';
    export let frameborder = 0;
    export let width = '100%';
    // default to a random id,
    // export let key = `pipen-report-iframe-component-${Math.random().toString(36).substring(7)}`;

    let loaded = false;
</script>

<div class="pipen-report-iframe-container" style="width: {width}">
    {#if !loaded}
    <div class="pipen-report-iframe-indicator">
        <InlineLoading description="Loading content ..." />
    </div>
    {/if}
    <iframe
        {title}
        {width}
        {src}
        frameborder={frameborder}
        on:load={() => loaded = true}
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
        width: 100%;
        height: 40%;
        font-size: 1.2rem;
    }

    .pipen-report-iframe-indicator :global(.bx--inline-loading) {
        justify-content: center;
        height: 100%;
    }
</style>
