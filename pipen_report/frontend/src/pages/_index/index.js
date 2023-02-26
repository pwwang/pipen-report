import App from './index.svelte';
import data from '../../data.json';

const app = new App({
	target: document.body,
	props: {
        pipeline: data.pipeline,
        procs: data.procs,
        versions: data.versions
    }
});

export default app;
