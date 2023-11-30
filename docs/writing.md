# Writing reports

## Using carbon-components-svelte components

[`carbon-components-svelte`][1] is supported by default. So you can use any components from the package. See their [documentations][2].

To use a components from `carbon-components-svelte`:

```jsx
<script>
    import { Button } from 'carbon-components-svelte`;
    // or use a shortcut
    import { Button } from '$ccs';
</script>

<Button />
```

## Using builtin components

There are also builting components to enhance some functions.

To use a builtin component:

```jsx
import { Image } from '../../components';
// or use a shortcut
import { Image } from '$libs';
import { Image } from '$components';
```

### DataTable

An enhanced `DataTable` from `carbon-components-svelte/DataTable`.

Additional features:

- Paginations enabled by default, with properties:

  - `page`: set current page
  - `pageSize`: set current page size
  - `pageSizes`: allowed page sizes to set

- Sorting enabled by default (with `sortable = true`)
- `zebra` set to `true` by default (with `zebra = true`)
- Added a frame around the table, so tables and images can be aligned (better looking)
  - You can set `frameProps` to `null`/`undefined` to disable it.
- Implemented download of data in the table or the entire data file if property `src` is set.
- Implemented search
- Allowing a single `data` property to pass data instead of `headers` and `rows`
  - `data` is just `rows`, but `headers` will be inferred from it.

!!! tip

    A `datatable` filter is added for python to render the template, so that we can read the data from a data file.

    ```jsx
    <script>
        import { DataTable } from "$libs";
    </script>

    <DataTable src="{{job.out.outfile}}" data={ {{ job.out.outfile | datafile: sep="\t" }} } />
    ```

    All other arguments will be passed to `pandas.read_csv()` except `doule_precision`, which will be passed to `pandas.DataFrame.to_json()` to control the precision of the numbers.

### Image

An enhanced `ImageLoader` from `carbon-components-svelte/ImageLoader`

Additional features:

- Similarly, a frame is added and enabled by default. To disable it, set `frameProps` to `null`/`undefined`
- Removed the width 100% style, added a class, and set the default width 45%.
- Added a modal when clicking on the image, the original dimension of the image is shown.
- Added "open in new window" for the image in the modal.

### Markdown

A markdown tag is processed at server side by python, which is not implemented as a svelte component. So you don't need to import it in `script` tag.

Everything inside the `<Markdown>` is passed to `markdown.markdown()` from python `Markdown` package to convert to html.

## Advanced usage

## Using self-defined components

Say you have a set of components that you want to use in all your reports. You can specify the path to the directory containing the components in `report_exlibs` by either `pipen report config --exlibs <path>` or `pipeline.config.plugin_opts.report_exlibs = <path>`.

Then you can import the components from the path you specified.

```jsx
<script>
    import { MyComponent } from '$exlibs/MyComponent.svelte';
</script>
```

You can write your own components based on `carbon-components-svelte` components.

Note that the shortcut `$ccs` is not available in the components you write. You have to use 'carbon-components-svelte'.

### Using other svelte components

- Can you use other svelte components?

    Yes. But you have to do it for every pipeline run. And you have to set `report_nobuild` to `True`.

- How?

    In the working directory, remove `node_modules` and make a copy of `package.json` instead of a symbolinc link. This is important, you may not want to pollute the global one.

    For example, if you want to use [`smelte`][3]
    Then run `npm install` and `npm install -D smelte`

    In your template:
    ```jsx
    <script>
        import { Chip } from "smelte";

        let closed = false;
        let clicked = false;
    </script>

    <Chip
        icon="face"
        removable
        selectable
        on:close={() => closed = true}
        on:click={() => clicked = true}
    >test</Chip>
    ```

    Finally, run `npm build` to buld your reports

[1]: https://github.com/carbon-design-system/carbon-components-svelte
[2]: http://ibm.biz/carbon-svelte
[3]: https://smeltejs.com/
