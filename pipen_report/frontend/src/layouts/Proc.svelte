<script>
  import {
    Column,
    Content,
    Grid,
    SideNav,
    Row
  } from "carbon-components-svelte";

  import Base from './Base.svelte';
  import Footer from './Footer.svelte';

  let isSideNavOpen = false;

  export let logo;
  export let logotext = null;
  export let versions;
  export let procs;
  export let pipeline_name;
</script>

<Base bind:isSideNavOpen {logo} {logotext} {procs} {pipeline_name}>

    <SideNav bind:isOpen={isSideNavOpen}>
      <slot name="toc" />
    </SideNav>

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
</Base>
