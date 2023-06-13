<script>
  import {
    Content
  } from "carbon-components-svelte";

  import Header from './Header.svelte';
  import Footer from './Footer.svelte';

  export let logo;
  export let logotext = null;
  export let versions;
</script>

<Header {logo} {logotext} entries={[]} />

<Content>
    <slot />
</Content>

<Footer {versions} />
