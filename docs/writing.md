
## Using carbon-components-svelte components

[`carbon-components-svelte`][1] is supported by default. So you can use any components from the package. See their [documentations][2].

To use a components from `carbon-components-svelte`:

```jsx
<script>
    import { Button } from 'carbon-components-svelte`;
</script>

<Button />
```

Or you can also use a shortcut:

```js
import { Button } from '@@ccs';  // just a shotcut ot 'carbon-components-svelte'
```

## Using builtin components

There are also builting components to enhance some functions.

To use a builtin component:

```jsx
import { Image } from '../components'; // use shortcut '@@'
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
        import { DataTable } from "@@";
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


## Advanced usage

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


### Writing your own components

You can also write your own components, well, only based on `carbon-components-svelte` components. If you want to use other dependencies, see [Using other svelte components](#using-other-svelte-components).

Just put your components in `<pipeline-workdir>/<pipeline-name>/.report-workdir/src/components`, just like those builtin components.

To use it (say the component is called `Dialog`):

```jsx
<script>
    import { Dialog } from "../components/Dialog";
    // if you added it to `components/index.js`, you can do:
    // import {Dialog} from "@@";
</script>
```


[1]: https://github.com/carbon-design-system/carbon-components-svelte
[2]: http://ibm.biz/carbon-svelte
[3]: https://smeltejs.com/
