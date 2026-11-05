<script>
    import { onMount } from 'svelte';
    import {
        SideNavItems,
        SideNavLink,
        SideNavMenu,
        SideNavMenuItem,
    } from "carbon-components-svelte";

    /**
     * This is passed in and originally from python
     * [{
     *     slug: "h1-slug1", text: ..., children: [{"slug": "h2-slug1", ...}]
     * }]
     */
    export let toc;
    export let page;

    const totalPages = Math.max(0, ...toc.map((t) => t.page)) + 1;
    const h1Slugs = toc.map((t) => t.slug);

    // full url of another page of this process (no hash: the page switcher goes to the top)
    const page_href = (toc_page) => {
        let url = new URL(window.location.href);
        url.hash = "";
        const proc = url.searchParams.get("proc") || "_index";
        const procbase = proc.replace(/-\d+$/, "");
        url.searchParams.set("proc", toc_page === 0 ? procbase : `${procbase}-${toc_page}`);
        return url.toString();
    };

    // section links stay on the page (no reload) when the section lives here
    const get_url = (toc_page) => (page === toc_page ? "" : page_href(toc_page));

    // the h1 section being read
    let activeSlug = null;
    $: activeIndex = toc.findIndex((t) => t.slug === activeSlug);

    // slug -> class string for every row (h1 and h2)
    let rowClasses = {};
    $: {
        const next = {};
        toc.forEach((h1, i) => {
            const h1OnPage = h1.page === page;
            next[h1.slug] = [
                "toc-row",
                h1OnPage ? "on-page" : "off-page",
                h1.slug === activeSlug ? "is-active" : "",
                h1OnPage && i <= activeIndex ? "is-passed" : "",
            ].filter(Boolean).join(" ");
            h1.children.forEach((h2) => {
                const h2OnPage = h2.page === page;
                next[h2.slug] = [
                    "toc-row toc-row--h2",
                    h2OnPage ? "on-page" : "off-page",
                    h2.slug === activeSlug ? "is-active" : "",
                    h2OnPage && i <= activeIndex ? "is-passed" : "",
                ].filter(Boolean).join(" ");
            });
        });
        rowClasses = next;
    }

    const scrollActiveIntoView = () => {
        if (!activeSlug) {
            return;
        }
        document
            .querySelector(`[href$="#${activeSlug}"]`)
            ?.scrollIntoView({ block: "nearest" });
    };
    $: scrollActiveIntoView(activeSlug);

    // Heading positions, measured in document space. The anchors the preprocessor emits are
    // zero-height, which an IntersectionObserver reports as "not intersecting", so the active
    // section is derived from the scroll position instead.
    let headingTops = [];

    const measureHeadings = () => {
        headingTops = h1Slugs
            .map((slug) => {
                const el = document.getElementById(slug);
                return el
                    ? { slug, top: el.getBoundingClientRect().top + window.scrollY }
                    : null;
            })
            .filter(Boolean)
            .sort((a, b) => a.top - b.top);
    };

    const syncActive = () => {
        if (!headingTops.length) {
            measureHeadings();
        }
        // a heading counts as current once it is 96px above the top edge
        const y = window.scrollY + 96;
        let current = headingTops.length ? headingTops[0].slug : null;
        for (const h of headingTops) {
            if (h.top <= y) {
                current = h.slug;
            }
        }
        if (current !== activeSlug) {
            activeSlug = current;
        }
    };

    onMount(() => {
        // initial active section: hash (h1, or h2 -> parent h1),
        // else the first section of the current page
        const hash = location.hash.slice(1);
        activeSlug = h1Slugs.includes(hash)
            ? hash
            : (toc.find((t) => t.children.some((c) => c.slug === hash))?.slug
                ?? (toc.find((t) => t.page === page) ?? toc[0])?.slug);

        measureHeadings();
        syncActive();
        // headings move once fonts and images settle
        const remeasure = () => {
            measureHeadings();
            syncActive();
        };
        const timers = [200, 800, 2000].map((ms) => setTimeout(remeasure, ms));

        // listen on both: depending on the engine the scroll event is delivered on the
        // window or on the document
        window.addEventListener("scroll", syncActive, { passive: true });
        document.addEventListener("scroll", syncActive, { passive: true });
        window.addEventListener("resize", remeasure);

        return () => {
            timers.forEach(clearTimeout);
            window.removeEventListener("scroll", syncActive);
            document.removeEventListener("scroll", syncActive);
            window.removeEventListener("resize", remeasure);
        };
    });
</script>

{#if totalPages > 1}
<nav class="toc-pages" aria-label="Pages of this process">
    {#each Array(totalPages) as _, i}
    <a
        class="toc-page-num"
        class:is-current={i === page}
        aria-current={i === page ? "page" : undefined}
        href={page_href(i)}
        title={`Go to page ${i + 1}`}>{i + 1}</a>
    {/each}
</nav>
{:else}
<div class="toc-spacer" aria-hidden="true"></div>
{/if}

<SideNavItems>
    {#each toc as h1_toc}
        {#if h1_toc.children.length === 0}
        <SideNavLink href={`${get_url(h1_toc.page)}#${h1_toc.slug}`} class={rowClasses[h1_toc.slug]} title={h1_toc.text} text={h1_toc.text} />
        {:else}
        <SideNavMenu href={`${get_url(h1_toc.page)}#${h1_toc.slug}`} class={rowClasses[h1_toc.slug]} title={h1_toc.text} text={h1_toc.text} expanded>
            {#each h1_toc.children as h2_toc}
            <SideNavMenuItem href={`${get_url(h2_toc.page)}#${h2_toc.slug}`} class={rowClasses[h2_toc.slug]} title={h2_toc.text} text={h2_toc.text} />
            {/each}
        </SideNavMenu>
        {/if}
    {/each}
</SideNavItems>

<style>
    /* SideNavItems renders this ul; keep it scrollable (not just on hover) */
    :global(.bx--side-nav .bx--side-nav__items) {
        padding: 4px 0 24px;
        overflow-y: auto;
    }

    /* rows: h1 and h2 share `.toc-row` (ccs puts `class` on the link/button) */
    :global(.bx--side-nav .bx--side-nav__items .toc-row) {
        position: relative;
        display: flex;
        align-items: center;
        min-height: 2rem;
        padding: 0 12px 0 32px;
        font-size: 0.875rem;
        line-height: 1.25;
        text-decoration: none;
        color: #525252;
        transition: color 70ms, background-color 70ms;
    }
    :global(.bx--side-nav .bx--side-nav__items .bx--side-nav__menu .toc-row--h2) {
        min-height: 1.75rem;
        height: auto; /* beat Carbon's `height: 2rem` on menu links */
        padding-left: 48px;
        font-size: 0.8125rem;
        color: #6f6f6f;
    }

    /* SideNavMenu renders a <button>; reset it to look like the links */
    :global(.bx--side-nav .bx--side-nav__items .bx--side-nav__submenu.toc-row) {
        width: 100%;
        border: 0;
        background: none;
        text-align: left;
    }

    /* Carbon sets colour/font on the inner text spans; inherit from the row */
    :global(.bx--side-nav .bx--side-nav__items .toc-row .bx--side-nav__link-text),
    :global(.bx--side-nav .bx--side-nav__items .toc-row .bx--side-nav__submenu-title) {
        font-size: inherit;
        font-weight: inherit;
        color: inherit;
    }

    /* the rail */
    :global(.bx--side-nav .bx--side-nav__items .toc-row::before) {
        content: "";
        position: absolute;
        left: 14px;
        top: 0;
        bottom: 0;
        width: 2px;
        background: #e0e0e0;
    }
    :global(.bx--side-nav .bx--side-nav__items .toc-row.is-passed::before) {
        background: #0f62fe;
    }
    :global(.bx--side-nav .bx--side-nav__items .toc-row.is-active::before) {
        width: 3px;
        background: #0f62fe;
    }

    /* the section being read: a bead on the rail */
    :global(.bx--side-nav .bx--side-nav__items .toc-row.is-active::after) {
        content: "";
        position: absolute;
        left: 11px;
        top: 50%;
        width: 8px;
        height: 8px;
        margin-top: -4px;
        border-radius: 50%;
        background: #0f62fe;
    }

    /* row states */
    :global(.bx--side-nav .bx--side-nav__items .toc-row.off-page) {
        color: #8d8d8d;
    }
    :global(.bx--side-nav .bx--side-nav__items .toc-row.is-active) {
        color: #161616;
        font-weight: 600;
    }
    :global(.bx--side-nav .bx--side-nav__items .toc-row.off-page.is-active) {
        color: #161616;
    }
    :global(.bx--side-nav .bx--side-nav__items .toc-row:hover) {
        background: #e5e5e5;
        color: #161616;
    }
    :global(.bx--side-nav .bx--side-nav__items .toc-row:focus-visible) {
        outline: 2px solid #0f62fe;
        outline-offset: -2px;
    }

    /* a process with a single page has no switcher row, so the list brings its own
       top spacing (the switcher's border would otherwise be the thing that separates
       the list from the header) */
    .toc-spacer {
        height: 1rem;
    }

    /* page switcher */
    .toc-pages {
        display: flex;
        gap: 2px;
        align-items: center;
        padding: 8px 12px 4px 32px;
        border-bottom: 1px solid #e0e0e0;
        margin-bottom: 4px;
    }
    .toc-page-num {
        min-width: 1.5rem;
        height: 1.5rem;
        padding: 0 6px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 0.75rem;
        font-variant-numeric: tabular-nums;
        color: #525252;
        text-decoration: none;
        border-bottom: 2px solid transparent;
    }
    .toc-page-num.is-current {
        color: #0f62fe;
        border-bottom-color: #0f62fe;
        font-weight: 600;
    }
    .toc-page-num:hover {
        background: #e5e5e5;
        color: #161616;
    }
    .toc-page-num:focus-visible {
        outline: 2px solid #0f62fe;
        outline-offset: -2px;
    }

    @media (prefers-reduced-motion: reduce) {
        :global(.bx--side-nav .bx--side-nav__items .toc-row) {
            transition: none;
        }
    }
</style>
