<script>
  import { onMount } from "svelte";
  import {
    Column,
    Content,
    Grid,
    Row,
    SideNav,
  } from "carbon-components-svelte";

  import ProcToc from "./ProcToc.svelte";
  import Header from "./Header.svelte";
  import Footer from "./Footer.svelte";

  export let logo;
  export let logotext = null;
  export let versions;
  export let entries;
  export let pipeline_name;
  export let report_toc;
  export let toc;
  export let page;
  export let isSideNavOpen;
  export let runinfo;

  let intersectionObserver;

  onMount(() => {
    const url = new URL(window.location.href);
    let tocActiveItem;
    if (url.hash.length > 0) {
      tocActiveItem = document.querySelector(`li:has(>[href="${url.hash}"])`);
    } else {
      tocActiveItem = document.querySelector("li:has(>.toc-current-page)");
    }
    if (tocActiveItem) {
      tocActiveItem.classList.add("toc-active");
      tocActiveItem.scrollIntoView();
    }

    const observerCallback = (entries) => {
      entries.forEach((entry) => {
        const id = entry.target.getAttribute("id");
        const tocItem = document.querySelector(`li:has(>[href="#${id}"])`);
        if (!tocItem) {
          return;
        }
        if (entry.isIntersecting) {
          tocItem.classList.add("toc-active");
        } else {
          tocItem.classList.remove("toc-active");
        }
      });
    };

    const tocHeadings = document.querySelectorAll(".pipen-report-toc-anchor");
    intersectionObserver = new IntersectionObserver(observerCallback, {
      root: null,
      rootMargin: "0px",
      threshold: 0.5,
    });
    tocHeadings.forEach((heading) => {
      intersectionObserver.observe(heading);
    });
  });
</script>

<Header {logo} {logotext} {entries} {pipeline_name} bind:isSideNavOpen />
{#if report_toc && toc.length > 0}
  <SideNav bind:isOpen={isSideNavOpen}>
    <ProcToc {toc} {page} />
  </SideNav>
{/if}

<Content>
  <Grid>
    <Row>
      <Column>
        <slot />
      </Column>
    </Row>
  </Grid>
  <Footer {versions} {runinfo} />
</Content>
