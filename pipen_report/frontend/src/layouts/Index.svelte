<script>
  import {
    Content
  } from "carbon-components-svelte";

  import Base from './Base.svelte';

  export let logo;
  export let logotext = null;
</script>

<Base {logo} {logotext} procs={[]}>
    <Content>
        <slot />
    </Content>
</Base>
