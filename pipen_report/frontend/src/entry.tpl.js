{% if page == 0 %}
import App from "../pages/{{proc_slug}}.svelte";
{% else %}
import App from "../pages/{{proc_slug}}-part{{page}}.svelte";
{% endif %}

const app = new App({
	target: document.body,
	props: {
		name: '{{proc.name}}',
        desc: '{{proc.desc}}'
	}
});

export default app;
