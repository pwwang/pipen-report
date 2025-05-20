<script>
	import temml from 'temml';

    // see https://www.npmjs.com/package/svelte-math
    // This is a modified version to adopt svelte 4
	export let latex;
	export let displayMode = false;
	export let options = {};

	let slot;
	let slotContent = '';

	$: slotContent = slot?.innerText ?? '';
	$: markup = latex ?? slotContent ?? '';
	$: html = temml.renderToString(markup, { displayMode, ...options });
</script>

<!-- Display rendered math -->
{@html html}

<!-- Hidden slot -->
<span class="svelte-math-slot" bind:this={slot} style="display: none">
	<slot />
</span>
