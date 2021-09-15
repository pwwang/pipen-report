<script>
  import {
    Column,
    Content,
    Grid,
    SideNav,
    Row
  } from "carbon-components-svelte";

  import Base from './Base.svelte';

  let isSideNavOpen = false;

  export let logo;
  export let logotext = null;
  export let procs;
</script>

<Base bind:isSideNavOpen {logo} {logotext} {procs}>

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
    </Content>
</Base>
