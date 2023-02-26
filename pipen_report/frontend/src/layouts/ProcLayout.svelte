<script>
  import { Column, Content, Grid, Row, SideNav } from "carbon-components-svelte";

  import ProcToc from "./ProcToc.svelte";
  import Header from './Header.svelte';
  import Footer from './Footer.svelte';

  export let logo;
  export let logotext = null;
  export let versions;
  export let procs;
  export let pipeline_name;
  export let report_toc;
  export let toc;
  export let page;
  export let isSideNavOpen;
</script>

<Header {logo} {logotext} {procs} {pipeline_name} bind:isSideNavOpen />
{#if report_toc}
<SideNav bind:isOpen={isSideNavOpen}>
  <ProcToc {toc} {page}  />
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
  <Footer {versions} />
</Content>
