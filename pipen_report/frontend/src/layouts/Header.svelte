<script>
  import {
    Header,
    HeaderAction,
    HeaderPanelLinks,
    HeaderPanelDivider,
    HeaderPanelLink,
    Accordion,
    AccordionItem,
    InlineNotification,
    Tile,
    Modal,
    TextInput,
    PasswordInput,
    Select,
    SelectItem,
    Stack,
    Theme,
    Link,
    LocalStorage
  } from "carbon-components-svelte";
  import AiObservability from "carbon-icons-svelte/lib/AiObservability.svelte";
  import Information from "carbon-icons-svelte/lib/Information.svelte";
  import { PageChat } from 'page-chat';
  import { onMount } from "svelte";

  let isOpen = false;
  let transition = { duration: 200 };
  let pageChatSettingsOpen = false;

  // Storage keys for page chat settings
  const LS_MODEL = "__pipen-report-pagechat-model";
  const LS_BASEURL = "__pipen-report-pagechat-baseURL";
  const LS_LANGUAGE = "__pipen-report-pagechat-language";
  const LS_APIKEY_DURATION = "__pipen-report-pagechat-apiKeyDuration";
  const LS_APIKEY = "__pipen-report-pagechat-apiKey";
  const is_file_protocol = location.protocol === 'file:';

  let apiKeyStorageDuration = "1-day";

  let pageChatSettings = {
    model: '',
    baseURL: '',
    apiKey: '',
    language: 'en-US',
  }

  // Expirable apiKey storage helpers
  // session = until browser closed (tracked via lastAccess timestamp)
  const DURATION_MS = {
    'session': 12 * 60 * 60 * 1000, // 12 hours max, refreshed on access
    '1-day': 24 * 60 * 60 * 1000,
    '7-days': 7 * 24 * 60 * 60 * 1000,
    '30-days': 30 * 24 * 60 * 60 * 1000,
  };

  function parseApiKeyRecord(raw) {
    if (!raw) return null;
    try {
      const parsed = JSON.parse(raw);
      if (parsed.value !== undefined && parsed.expiresAt !== undefined) {
        return parsed;
      }
      // Legacy: plain string value
      return { value: raw, expiresAt: null };
    } catch {
      // Legacy: plain string
      return { value: raw, expiresAt: null };
    }
  }

  function loadApiKey() {
    const raw = localStorage.getItem(LS_APIKEY);
    if (!raw) return '';

    const record = parseApiKeyRecord(raw);
    if (!record) return '';

    // No expiration (forever)
    if (record.expiresAt === null) {
      return record.value;
    }

    // Check if expired
    if (Date.now() > record.expiresAt) {
      localStorage.removeItem(LS_APIKEY);
      return '';
    }

    // For session duration, refresh expiration on each access
    if (apiKeyStorageDuration === 'session' && DURATION_MS['session']) {
      const newExpiresAt = Date.now() + DURATION_MS['session'];
      localStorage.setItem(LS_APIKEY, JSON.stringify({ value: record.value, expiresAt: newExpiresAt }));
    }

    return record.value;
  }

  function clearApiKey() {
    localStorage.removeItem(LS_APIKEY);
  }

  function saveApiKey(value, duration) {
    if (!value) {
      clearApiKey();
      return;
    }
    if (duration === 'forever') {
      localStorage.setItem(LS_APIKEY, JSON.stringify({ value, expiresAt: null }));
    } else if (DURATION_MS[duration]) {
      const expiresAt = Date.now() + DURATION_MS[duration];
      localStorage.setItem(LS_APIKEY, JSON.stringify({ value, expiresAt }));
    }
  }

  // Load apiKey on mount (checks expiration)
  onMount(() => {
    pageChatSettings.apiKey = loadApiKey();
    if (pageChatSettings.model || pageChatSettings.baseURL || pageChatSettings.apiKey) {
      updatePageChat();
    }
  });

  export let entries;
  export let logo;
  export let logotext = null;
  export let pipeline_name = undefined;
  export let isSideNavOpen;
  export let page_chat;

  pipeline_name = pipeline_name || logo;

  window.page_chat_client = null;
  const updatePageChat = function() {
    if (!page_chat) {
      return;
    }

    // Persist apiKey according to selected duration
    saveApiKey(pageChatSettings.apiKey, apiKeyStorageDuration);

    if (window.page_chat_client) {
      window.page_chat_client.panel.dispose();
    }
    window.page_chat_client = new PageChat({
      model: pageChatSettings.model,
      baseURL: pageChatSettings.baseURL,
      apiKey: pageChatSettings.apiKey,
      language: pageChatSettings.language || 'en-US',
      title: 'Page Chat',
      persist: true,
      systemPrompt: `
You are a professional assistant on the report page of a data processing pipeline. Your task is to help users understand the information on this page and provide guidance on how to use the page effectively. You have access to all the information on this page, including details about the pipeline, processes, and any relevant documentation.

Guidelines:
- Always provide accurate and helpful information based on the content of the page.
- If the user asks about specific processes or components, provide detailed explanations and how they relate to the overall pipeline.
- If the user is unsure about how to navigate the page or use certain features, offer step-by-step guidance.
- If the user asks for recommendations on how to analyze the data or interpret the results, provide insights based on the information available on the page.
- If we don't have enough information to answer the user's question, be honest about it and suggest what information they might need to provide for you to assist them better.
- When asking about an interactive plot or 3D plot, find the plot generated by plotly wrapped in one of the iframes.
`
    });
    window.page_chat_client.panel.show();
    pageChatSettingsOpen = false;
  };

</script>

{#if page_chat}
<LocalStorage key={LS_MODEL} bind:value={pageChatSettings.model} />
<LocalStorage key={LS_BASEURL} bind:value={pageChatSettings.baseURL} />
<LocalStorage key={LS_LANGUAGE} bind:value={pageChatSettings.language} />
<LocalStorage key={LS_APIKEY_DURATION} bind:value={apiKeyStorageDuration} />
{/if}

{#if page_chat && pageChatSettingsOpen}
<Modal
  size="sm"
  bind:open={pageChatSettingsOpen}
  primaryButtonText="Update"
  secondaryButtonText="Cancel"
  hasScrollingContent
  preventCloseOnClickOutside
  primaryButtonDisabled={is_file_protocol}
  hasForm
  formId="page-chat-settings-form"
  class="page-chat-settings-modal"
  on:click:button--secondary={() => (pageChatSettingsOpen = false)}
>
  <div slot="heading" style="display: flex; align-items: center; gap: 0.5rem;">
      <AiObservability size={24} />
      <div style="font-weight: bold;">Page-Chat Settings</div>
  </div>
  {#if is_file_protocol}
    <InlineNotification kind="warning" title="Warning" subtitle="Due to browser security restrictions, page-chat.js does not work properly when the report is opened via the file:// protocol. Please access the report via a server for full functionality." />
  {/if}
  <form id="page-chat-settings-form" on:submit|preventDefault={updatePageChat}>
    <Stack gap={5}>
      <Accordion>
        <AccordionItem>
        <div slot="title" style="display: flex; align-items: center; gap: 0.5rem;">
          <Information size={20} />
          <div>About page-chat.js</div>
        </div>
        <p><code>page-chat.js</code> is a client library for integrating a page-specific chatbot into your web application. It provides an easy way to set up a chatbot that can assist users based on the content of the page. In this settings panel, you can configure the model, base URL, and API key for the page chat. After updating the settings, click "Update" to apply the changes and see the updated chatbot in action.</p>
        <p>You may check <Link href="https://alibaba.github.io/page-agent/docs/features/models" target="_blank">the page-agent documentation</Link> for more details, but note that <code>page-chat.js</code> doesn't require the model to be capable of function or tool calling.</p>
        <p style="font-weight: bold;">Limitations:</p>
        <ul>
          <li>The chatbot's knowledge is limited to the information available on the page. It may not be able to answer questions that require external knowledge or context.</li>
          <li>The chatbot's performance and accuracy depend on the quality and relevance of the information on the page. If the page lacks clear and comprehensive information, the chatbot may struggle to provide helpful responses.</li>
          <li>A visual model is required to answer questions about plots. If the model configured in the settings doesn't support visual understanding, the chatbot won't be able to assist with questions related to plots or visualizations on the page.</li>
        </ul>
        </AccordionItem>
      </Accordion>
      <TextInput disabled={is_file_protocol} bind:value={pageChatSettings.model} labelText="Model" placeholder="Enter model" />
      <TextInput disabled={is_file_protocol} bind:value={pageChatSettings.baseURL} labelText="Base URL" placeholder="Enter base URL" />
      <PasswordInput disabled={is_file_protocol} bind:value={pageChatSettings.apiKey} labelText="API Key" placeholder="Enter API key" />
      <Select
        disabled={is_file_protocol}
        labelText="API Key Storage Duration"
        bind:selected={apiKeyStorageDuration}
      >
        <SelectItem value="1-day" text="1 day" />
        <SelectItem value="7-days" text="7 days" />
        <SelectItem value="30-days" text="30 days" />
        <SelectItem value="session" text="Session (shared across tabs, max 12h)" />
        <SelectItem value="forever" text="Forever (not recommended)" />
      </Select>
    </Stack>
  </form>
</Modal>
{/if}

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
    {#if page_chat}
    <!-- svelte-ignore a11y-invalid-attribute -->
    <a class="page-chat-icon"
      on:click={() => (pageChatSettingsOpen = true)}
      title="Page Chat Settings"
      href="javascript:void(0);">
      <AiObservability size={24} />
    </a>
    {/if}
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
