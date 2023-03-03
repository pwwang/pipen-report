<script>
    import { Button } from "carbon-components-svelte";
    import ChevronUp from "carbon-icons-svelte/lib/ChevronUp.svelte";
    import ChevronDown from "carbon-icons-svelte/lib/ChevronDown.svelte";

    export let dir = undefined;  // up or down

    let icon = dir === "up" ? ChevronUp : ChevronDown;
    let text = dir === "up" ? "Go to previous page" : "Go to next page";

    const get_url = () => {
        let url = new URL(window.location.href);
        url.hash = "";
        let matching = url.pathname.match(/-(\d+)\.html/);
        if (matching === null) {
            // curpage = 0
            url.pathname = url.pathname.replace(".html", `-1.html`);
        } else {
            let curpage = parseInt(matching[1]);
            let topage = dir === "up" ? curpage - 1 : curpage + 1;
            if (topage === 0) {
                url.pathname = url.pathname.replace(
                    `-${curpage}.html`,
                    `.html`
                );
            } else {
                url.pathname = url.pathname.replace(
                    `-${curpage}.html`,
                    `-${topage}.html`
                );
            }
        }

        return url.toString()
    };
</script>

<div class={`pagenav ${dir}`}>
    <Button {icon} kind="tertiary" href={get_url()}>
        {text}
    </Button>
</div>

