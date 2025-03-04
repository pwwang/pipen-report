<script>
    import { createEventDispatcher } from "svelte";
    import ImageDownload from "./ImageDownload.svelte";
    import ImageDimension from "./ImageDimension.svelte";

    /**
     * The urls related to this image for download
     * For example, the PDF version of the image
     * It is either an array of objects with `src`, `tip`, and `icon` properties
     * or an array of strings representing the `src` values
     * @type {Array<{ src: string, tip: string, icon: string }> | Array<string> | {src: string, tip: string, icon: string} | string}
     */
    export let data = [];

    /**
     * The source of the displaying image
     * @type {string}
     */
    export let dsrc = "";

    if (!Array.isArray(data)) {
        data = [data];
    }
    data = [{src: "x", tip: "widthxheight"}, ...data];
    data = data.map((d) => {
        if (typeof d === "string") {
            return { src: d, tip: `Download the ${d.split(".").at(-1)} format.`, icon: "auto" };
        }
        d.tip = d.tip || `Download the ${d.src.split(".").at(-1)} format.`;
        d.icon = d.icon || "auto";
        return d;
    });

    const props = {
        ...$$restProps,
        class: [
            $$restProps.class,
            "pipen-report-image-download-list",
        ].filter(Boolean).join(" ")
    };
    const dispatch = createEventDispatcher();
</script>

{#if data.length > 0}
<div
    {...props}
    on:mouseenter={() => dispatch("mouseenter")}
    role="button"
    tabindex="0">
    {#each data as { src, tip, icon }, i}
        {#if src === "x"}
            <ImageDimension src={dsrc} {tip} />
        {:else}
            <ImageDownload {src} {tip} {icon} />
        {/if}
    {/each}
</div>
{/if}

<style>
    .pipen-report-image-download-list {
        position: absolute;
        z-index: 1000;
        background-color: white;
        border: 1px solid #d6d6d6;
        border-radius: 4px;
        box-shadow: 0 2px 4px 0 rgba(0, 0, 0, 0.1);
        padding: 0.1rem 0.32rem;
        gap: 0.1rem;
        display: flex;
        flex-direction: row;
        left: 2rem;
        top: 2rem;
    }
</style>
