import App from "../pages/{{proc_slug}}.svelte";

const app = new App({
	target: document.body,
	props: {
		name: '{{proc.name}}',
        desc: '{{proc.desc}}'
	}
});

export default app;
