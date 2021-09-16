<script>
  import "carbon-components-svelte/css/all.css";
  import {
    Header,
    HeaderUtilities,
    HeaderAction,
    HeaderPanelLinks,
    HeaderPanelDivider,
    HeaderPanelLink,
    Tile,
    Theme
  } from "carbon-components-svelte";

  let isOpen = false;
  let transition = { duration: 200 };

  export let procs;
  export let logo;
  export let logotext = null;
  export let pipeline_name = undefined;
  export let isSideNavOpen = false;

  pipeline_name = pipeline_name || logo;
</script>

<Header bind:isSideNavOpen>
  <Tile class="header-tile" slot="platform">
    <h1>{logo}</h1>
    {#if logotext !== null}
    {logotext}
    {/if}
  </Tile>
  <HeaderUtilities>
    <Theme
      render="select"
      persist
      persistKey="__pipen-report-theme"
      select={{
          themes: ['g10', 'white', 'g80', 'g90', 'g100'],
          labelText: 'Select a theme',
          inline: true
      }}
    />
    {#if procs.length > 0}
    <HeaderAction isOpen={isOpen} transition={transition}>
      <HeaderPanelLinks>
        <HeaderPanelDivider>Go to home: </HeaderPanelDivider>
        <HeaderPanelLink href="./index.html">
          {pipeline_name}
        </HeaderPanelLink>

        <HeaderPanelDivider>Switch to process: </HeaderPanelDivider>
        {#each procs as proc}
          <HeaderPanelLink href={`./${proc.slug}.html`}>
              {proc.name}
          </HeaderPanelLink>
        {/each}
      </HeaderPanelLinks>
    </HeaderAction>
    {/if}
  </HeaderUtilities>
</Header>

<slot />
