<script>
  import {
    Content
  } from "carbon-components-svelte";

  import Header from './Header.svelte';
  import Footer from './Footer.svelte';

  export let logo;
  export let logotext = null;
  export let versions;
  export let page_chat;
</script>

<Header {logo} {logotext} entries={[]} {page_chat} />

<Content>
    <slot />
</Content>

<Footer {versions} />

<p>&nbsp;</p>
