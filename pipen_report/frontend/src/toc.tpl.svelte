<script>
    import {
        SideNavItems,
        SideNavLink,
        SideNavMenu,
        SideNavMenuItem,
    } from "carbon-components-svelte";
    /**
     * This is passed from python
     * [{
     *     slug: "h1-slug1", text: ..., children: {"h2-slug1": {text: ...}}}
     * }]
     */
    const toc = {{toc}};
    const page = {{page}};

    const get_url = (toc_page) => {
        if (page === toc_page) {
            return "";
        }
        let url = new URL(window.location.href);
        url.hash = "";
        if (toc_page === 0) {
            url.pathname = url.pathname.replace(/-part\d+\.html/, ".html");
        } else if (page === 0) {
            url.pathname = url.pathname.replace(".html", `-part${toc_page}.html`);
        } else {
            url.pathname = url.pathname.replace(/-part\d+\.html/, `-part${toc_page}.html`);
        }

        return url.toString()
    };

    const get_class = (toc_page) => toc_page != page ? "toc-noncurrent-page" : "";
</script>

<SideNavItems>

    {#each toc as h1_toc}
        {#if h1_toc.children.length == 0}
        <SideNavLink href={`${get_url(h1_toc.page)}#${h1_toc.slug}`} class={get_class(h1_toc.page)} title={h1_toc.text} text={h1_toc.text} />
        {:else}
        <SideNavMenu href={`${get_url(h1_toc.page)}#${h1_toc.slug}`} class={get_class(h1_toc.page)} title={h1_toc.text} text={h1_toc.text} expanded>
        {#each h1_toc.children as h2_toc}
            <SideNavMenuItem href={`${get_url(h2_toc.page)}#${h2_toc.slug}`} class={get_class(h2_toc.page)} title={h2_toc.text} text={h2_toc.text} />
        {/each}
        </SideNavMenu>
        {/if}
    {/each}

</SideNavItems>
