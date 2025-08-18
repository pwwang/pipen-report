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
        const proc = url.searchParams.get("proc") || "_index";
        // if the proc is _index, the page should be 0
        // if the proc is _index-1, the page should be 1, etc.
        const curpage = parseInt((proc.match(/-(\d+)$/) || ["-0", "0"])[1]);
        const topage = dir === "up" ? curpage - 1 : curpage + 1;
        const procbase = proc.replace(/-\d+$/, "");
        const toproc = topage === 0 ? procbase : `${procbase}-${topage}`;

        url.searchParams.set("proc", toproc);

        return url.toString()
    };
</script>

<div class={`pagenav ${dir}`}>
    <Button {icon} kind="tertiary" href={get_url()}>
        {text}
    </Button>
</div>

