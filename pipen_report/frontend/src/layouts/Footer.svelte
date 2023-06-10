<script>
    import { Modal, CodeSnippet, Tabs, Tab, TabContent, InlineNotification } from "carbon-components-svelte";

    export let versions;
    export let runinfo = undefined;

    let modal_open = false;

</script>

{#if runinfo}
<Modal
    bind:open={modal_open}
    modalHeading="Running Information"
    passiveModal
    hasScrollingContent
    class="runinfo"
>
    <InlineNotification
        kind="warning"
        lowContrast
        hideCloseButton
        title="Showing the first job only. Check the workdir for information of other jobs if any."
        />
    <Tabs>
        <Tab label="Session Information" />
        <Tab label="Time Spent" />
        <Tab label="Device Information" />
        <svelte:fragment slot="content">
            <TabContent>
                <CodeSnippet type="multi" code={runinfo.session} />
            </TabContent>
            <TabContent>
                <CodeSnippet type="multi" code={runinfo.time} />
            </TabContent>
            <TabContent>
                <CodeSnippet type="multi" code={runinfo.device} />
            </TabContent>
        </svelte:fragment>
    </Tabs>
</Modal>
{/if}

<div class="pipen-report-footer bx--grid">
    <div class="runinfo">
        {#if runinfo}
        <a href="javascript:void(0);" on:click={() => {modal_open = true}}>&gt; Running Information</a>
        {/if}
    </div>
    <div class="versions">
        Powered by <span class="pipen-report-footer-versions">{@html versions}</span>
    </div>
</div>
