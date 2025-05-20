<script>
	import temml from 'temml';

    // see https://www.npmjs.com/package/svelte-math
    // This is a modified version to adopt svelte 4
	export let latex;
	export let displayMode = false;
	export let options = {};

	let slot;
	let slotContent = '';
    let html = '';
    let markup = '';

	$: {
        slotContent = slot?.innerText ?? '';
	    markup = latex ?? slotContent ?? '';
        // check if markup is base64 encoded (data:text/plain;base64,...)
        if (markup.startsWith('data:text/plain;base64,')) {
            // decode base64
            const base64 = markup.split(',')[1];
            const decoded = atob(base64);
            markup = decoded;
        }
	    html = temml.renderToString(markup, { displayMode, ...options });
    }
</script>

<!-- Display rendered math -->
{@html html}

<!-- Hidden slot -->
<span class="svelte-math-slot" bind:this={slot} style="display: none">
	<slot />
</span>
