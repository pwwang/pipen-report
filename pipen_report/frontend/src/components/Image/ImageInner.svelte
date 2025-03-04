<script>
    /**
     * @event {any} load
     * @event {any} error
     */

    /**
     * Specify the image source
     */
    export let src = "";

    /**
     * Specify the image alt text
     */
    export let alt = "";

    /**
     * The urls related to this image for download
     * For exmaple, the PDF version of the image
     * It is either an array of objects with `src`, `tip`, and `icon` properties
     * or an array of strings representing the `src` values
     * @type {Array<{ src: string, tip: string, icon: string }> | Array<string> | { src: string, tip: string, icon: string } | string}
     */
    export let download = [];

    /**
     * Specify the aspect ratio for the image wrapper
     * @type {"2x1" | "16x9" | "4x3" | "1x1" | "3x4" | "3x2" | "9x16" | "1x2"}
     */
    export let ratio = undefined;

    /**
     * Set to `true` when `loaded` is `true` and `error` is false
     */
    export let loading = false;

    /**
     * Set to `true` when the image is loaded
     */
    export let loaded = false;

    /**
     * Set to `true` if an error occurs when loading the image
     */
    export let error = false;

    /**
     * Set to `true` to fade in the image on load
     * The duration uses the `fast-02` value following Carbon guidelines on motion
     */
    export let fadeIn = false;

    export let border = true;
    let modal_open = false;
    let showDownloadList = false;

    /**
     * Method invoked to load the image provided a `src` value
     * @type {(url?: string) => void}
     */
    export const loadImage = (url) => {
        if (image != null) image = null;
        loaded = false;
        error = false;
        image = new Image();
        image.src = url || src;
        image.onload = () => (loaded = true);
        image.onerror = () => (error = true);
    };

    import { onMount, createEventDispatcher } from "svelte";
    import { fade } from "svelte/transition";
    import { AspectRatio, Modal } from "carbon-components-svelte";
    import ImageDownloadList from "./ImageDownloadList.svelte";

    const dispatch = createEventDispatcher();

    // "fast-02" duration (ms) from Carbon motion recommended for fading micro-interactions
    const fast02 = 110;

    let image = null;
    let hideTimeout;

    $: loading = !loaded && !error;
    $: if (src && typeof window !== "undefined") loadImage();
    $: if (loaded) dispatch("load");
    $: if (error) dispatch("error");

    onMount(() => {
        return () => (image = null);
    });

    const openModal = () => { modal_open = true; };

    const props = {
        ...$$restProps,
        class: [
            $$restProps.class,
            "pipen-report-image",
            border ? "" : "pipen-report-image-noborder"
        ].filter(Boolean).join(" ")
    };
</script>

{#if ratio === undefined}
    {#if loading}
        <slot name="loading" />
    {/if}
    {#if loaded}
        <!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
        <img
            {...props}
            {src}
            {alt}
            title="Click to zoom in ..."
            on:click={openModal}
            on:mouseenter={() => { showDownloadList = true; }}
            on:mouseleave={() => { hideTimeout = setTimeout(() => {showDownloadList = false;}, 100); }}
            transition:fade={{ duration: fadeIn ? fast02 : 0 }}
        />
        {#if showDownloadList}
            <ImageDownloadList dsrc={src} data={download} on:mouseenter={() => { clearTimeout(hideTimeout); showDownloadList = true; }} />
        {/if}
    {/if}
    {#if error}
        <slot name="error" />
    {/if}
{:else}
    <AspectRatio {ratio}>
        {#if loading}
            <slot name="loading" />
        {/if}
        {#if loaded}
            <!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
            <img
                {...props}
                {src}
                {alt}
                title="Click to zoom in ..."
                on:click={openModal}
                on:mouseenter={() => { showDownloadList = true; }}
                on:mouseleave={() => { hideTimeout = setTimeout(() => {showDownloadList = false;}, 100); }}
                transition:fade={{ duration: fadeIn ? fast02 : 0 }}
            />
            {#if showDownloadList}
                <ImageDownloadList data={download} on:mouseenter={() => { clearTimeout(hideTimeout); showDownloadList = true; }} />
            {/if}
        {/if}
        {#if error}
            <slot name="error" />
        {/if}
    </AspectRatio>
{/if}

<Modal
    bind:open={modal_open} modalHeading={alt}
    primaryButtonText="Open in new window ..."
    secondaryButtonText="Close"
    on:click:button--secondary = { () => { modal_open = false } }
    on:click:button--primary = { () => { modal_open = false; window.open(src); } }
>
    <img
        class="pipen-report-image-lg"
        {src}
        {alt}
        transition:fade={{ duration: fadeIn ? fast02 : 0 }}
    />
</Modal>
