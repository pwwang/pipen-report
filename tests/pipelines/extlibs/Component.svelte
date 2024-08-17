<script>
    import { Link } from "$ccs";
    import { Image } from "$lib";

    export let text;
    export let src = null;
</script>

{#if src}
    <Image src={src} alt={text} />
    <Link href={src}>{text}</Link>
{:else}
    <button>{text}</button>
{/if}
