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
</script>

<SideNavItems>

    {#each toc as h1_toc}
        {#if h1_toc.children.length == 0}
        <SideNavLink href={`#${h1_toc.slug}`} text={h1_toc.text} />
        {:else}
        <SideNavMenu href={`#${h1_toc.slug}`} text={h1_toc.text} />
        {#each h1_toc.children as h2_toc}
            <SideNavMenuItem href={`#${h2_toc.slug}`} text={h2_toc.text} />
        {/each}
        {/if}
    {/each}

    <!-- <SideNavLink text="Link 1" />
    <SideNavLink text="Link 2" />
    <SideNavLink text="Link 3" />
    <SideNavMenu text="Menu">
        <SideNavMenuItem href="/" text="Link 1" />
        <SideNavMenuItem href="/" text="Link 2" />
        <SideNavMenuItem href="/" text="Link 3" />
    </SideNavMenu> -->
</SideNavItems>
