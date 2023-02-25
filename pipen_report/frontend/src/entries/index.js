import App from '../pages/index.svelte';

const app = new App({
	target: document.body,
	props: {
		name: 'world'
	}
});

export default app;
