<script>
    import { Button } from "carbon-components-svelte";
    import ChevronUp20 from "carbon-icons-svelte/lib/ChevronUp20";
    import ChevronDown20 from "carbon-icons-svelte/lib/ChevronDown20";

    export let dir = undefined;  // up or down

    let icon = dir === "up" ? ChevronUp20 : ChevronDown20;
    let text = dir === "up" ? "Go to previous page" : "Go to next page";

    const get_url = () => {
        let url = new URL(window.location.href);
        url.hash = "";
        let matching = url.pathname.match(/-part(\d+)\.html/);
        if (matching === null) {
            // curpage = 0
            url.pathname = url.pathname.replace(".html", `-part1.html`);
        } else {
            let curpage = parseInt(matching[1]);
            let topage = dir === "up" ? curpage - 1 : curpage + 1;
            if (topage === 0) {
                url.pathname = url.pathname.replace(
                    `-part${curpage}.html`,
                    `.html`
                );
            } else {
                url.pathname = url.pathname.replace(
                    `-part${curpage}.html`,
                    `-part${topage}.html`
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

