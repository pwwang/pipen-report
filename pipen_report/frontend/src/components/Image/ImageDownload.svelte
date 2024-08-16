<script>
    import { TooltipIcon } from "carbon-components-svelte";
    import DocumentPdf from "carbon-icons-svelte/lib/DocumentPdf.svelte";
    import DocumentDownload from "carbon-icons-svelte/lib/DocumentDownload.svelte";
    import Image from "carbon-icons-svelte/lib/Image.svelte";
    import Svg from "carbon-icons-svelte/lib/Svg.svelte";
    import Png from "carbon-icons-svelte/lib/Png.svelte";
    import Jpg from "carbon-icons-svelte/lib/Jpg.svelte";
    import Gif from "carbon-icons-svelte/lib/Gif.svelte";
    import Tif from "carbon-icons-svelte/lib/Tif.svelte";
    import VideoPlayer from "carbon-icons-svelte/lib/VideoPlayer.svelte";
    import DatabaseElastic from "carbon-icons-svelte/lib/DatabaseElastic.svelte";
    import ChartLineData from "carbon-icons-svelte/lib/ChartLineData.svelte";
    import DataVolume from "carbon-icons-svelte/lib/DataVolume.svelte";
    import Archive from "carbon-icons-svelte/lib/Archive.svelte";
    import IbmWatsonxCodeAssistantForZRefactor from "carbon-icons-svelte/lib/IbmWatsonxCodeAssistantForZRefactor.svelte";

    export let src = "";
    export let tip = "";
    export let icon = "auto";

    let ext = src.split(".").at(-1).toLocaleLowerCase();
    let iconComponent;
    if (typeof icon === "string") {
        if (icon === "auto") icon = ext;
        switch (icon) {
            case "pdf":
            case "DocumentPdf":
                iconComponent = DocumentPdf;
                break;

            case "html":
            case "htm":
            case "ChartLineData":
                iconComponent = ChartLineData;
                break;

            case "png":
            case "Png":
                iconComponent = Png;
                break;

            case "jpg":
            case "jpeg":
            case "Jpg":
                iconComponent = Jpg;
                break;

            case "gif":
            case "Gif":
                iconComponent = Gif;
                break;

            case "tif":
            case "tiff":
            case "Tif":
                iconComponent = Tif;
                break;

            case "eps":
            case "DatabaseElastic":
                iconComponent = DatabaseElastic;
                break;

            case "mp4":
            case "avi":
            case "mov":
            case "mkv":
            case "webm":
            case "VideoPlayer":
                iconComponent = VideoPlayer;
                break;

            case "Image":
                iconComponent = Image;
                break;

            case "Data":
            case "DataVolume":
                iconComponent = DataVolume;
                break;

            case "Code":
            case "IbmWatsonxCodeAssistantForZRefactor":
                iconComponent = IbmWatsonxCodeAssistantForZRefactor;
                break;

            case "svg":
            case "Svg":
                iconComponent = Svg;
                break;

            case "zip":
            case "tar":
            case "gz":
            case "bz2":
            case "7z":
            case "rar":
            case "xz":
            case "Archive":
                iconComponent = Archive;
                break;

            default:
                iconComponent = DocumentDownload;
                break;
        }
    }

    const download = () => {
        const link = document.createElement("a");
        link.href = src;
        // console.log(src);
        link.download = src.split("/").pop();
        link.click();
    };

    const props = {
        ...$$restProps,
        class: [
            $$restProps.class,
            "pipen-report-image-download"
        ].filter(Boolean).join(" ")
    };
</script>

<TooltipIcon
    tooltipText={tip}
    on:click={download}
    icon={iconComponent}
    direction="bottom"
    align="start"
    {...props} />

<style>
    :global(.pipen-report-image-download) {
        cursor: pointer !important;
        padding: 0.2rem !important;
    }
    :global(.pipen-report-image-download:hover) {
        background-color: revert;
    }
    :global(.pipen-report-image-download svg) {
        fill: #616161 !important;
    }
</style>
