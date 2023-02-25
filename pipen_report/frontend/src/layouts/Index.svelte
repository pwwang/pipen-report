<script>
  import {
    Content
  } from "carbon-components-svelte";

  import Base from './Base.svelte';
  import Footer from './Footer.svelte';

  export let logo;
  export let logotext = null;
  export let versions;
</script>

<Base {logo} {logotext} procs={[]}>
    <Content>
        <slot />
    </Content>
    <Footer {versions} />
</Base>
