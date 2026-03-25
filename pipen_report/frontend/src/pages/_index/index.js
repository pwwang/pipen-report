import App from './index.svelte';
import data from '../../init_data.json';

const app = new App({
	target: document.body,
	props: {
        pipeline: data.pipeline,
        entries: data.entries,
        versions: data.versions,
        page_chat: data.page_chat
    }
});

export default app;
