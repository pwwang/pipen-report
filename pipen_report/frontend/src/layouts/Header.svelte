<script>
  import {
    Header,
    HeaderAction,
    HeaderPanelLinks,
    HeaderPanelDivider,
    HeaderPanelLink,
    Tile,
    Theme
  } from "carbon-components-svelte";

  let isOpen = false;
  let transition = { duration: 200 };

  export let entries;
  export let logo;
  export let logotext = null;
  export let pipeline_name = undefined;
  export let isSideNavOpen;

  pipeline_name = pipeline_name || logo;
</script>

<Header bind:isSideNavOpen>
  <Tile class="header-tile" slot="platform">
    <h1>{logo}</h1>
    {#if logotext !== null}
    {logotext}
    {/if}
  </Tile>
  <div class:bx--header__global={true} class="header-util">
    <Theme
      render="select"
      theme="g10"
      persist
      persistKey="__pipen-report-theme"
      select={{
          themes: ['g10', 'white', 'g80', 'g90', 'g100'],
          labelText: 'Theme',
          inline: true
      }}
    />
    {#if entries.length > 0}
    <HeaderAction isOpen={isOpen} transition={transition}>
      <HeaderPanelLinks>
        <HeaderPanelDivider>Go to home: </HeaderPanelDivider>
        <HeaderPanelLink href="index.html">
          {pipeline_name}
        </HeaderPanelLink>

        <HeaderPanelDivider>Switch to process: </HeaderPanelDivider>
        {#each entries as entry}
          {#if entry.procs}
            <HeaderPanelLink class="procgroup">{entry.name}</HeaderPanelLink>
            {#each entry.procs as proc}
            <HeaderPanelLink title={proc.name} class="procgroup-proc" href={`?proc=${proc.name}`}>
                - {proc.name}
            </HeaderPanelLink>
            {/each}
          {:else}
          <HeaderPanelLink title={entry.name} href={`?proc=${entry.name}`}>
              {entry.name}
          </HeaderPanelLink>
          {/if}
        {/each}
      </HeaderPanelLinks>
    </HeaderAction>
    {/if}
  </div>
</Header>

<style>
  :global(.header-util .bx--select--inline) {
    /* to keep it while resizing */
    justify-content: flex-end;
  }
  :global(.header-util .bx--label) {
    color: #cfcfcf;
  }
  :global(.header-util .bx--select-input) {
    background-color: var(--cds-ui-background, #ffffff);
    outline-color: var(--cds-border-inverse, #f4f4f4);
    font-size: var(--cds-caption-01-font-size, 0.75rem);
    height: 2rem;
  }
</style>
