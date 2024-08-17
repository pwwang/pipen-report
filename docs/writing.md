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

Thanks to the `rollup-alias` plugin, you can use the following aliases:

```js
{
  entries: [
  { find: '$components', replacement: '../../components' },
  { find: '$component', replacement: '../../components' },
  { find: '$layouts', replacement: '../../layouts' },
  { find: '$layout', replacement: '../../layouts' },
  { find: '$libs', replacement: '../../components' },
  { find: '$lib', replacement: '../../components' },
  { find: '$extlibs', replacement: '../../extlibs/{{extlibs.split("/")[-1]}}' },
  { find: '$ccs', replacement: 'carbon-components-svelte' },
 ]
}
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
- Added a toolbar on the top-left corner of the image, with buttons to download the resources related to this image (i.e. the high-resolution image, the data file, etc.)
  - To provide the information about the resources, use the `data` property. It should be:
  - a list of objects or a single object, each object should have a `src`, `tip` and a `icon` property, where `src` is the path to the resource, `tip` is the tooltip, and `icon` is the icon to show. By default, the `icon` is auto, which will be inferred from the extension of the `src`. Available icons:
    - `DocumentPdf`: Associated extensions: `pdf`
    - `ChartLineData`: Associated extensions: `html`
    - `Png`: Associated extensions: `png`
    - `Jpg`: Associated extensions: `jpg`, `jpeg`
    - `Gif`: Associated extensions: `gif`
    - `Svg`: Associated extensions: `svg`
    - `Tif`: Associated extensions: `tif`, `tiff`
    - `Archive`: Associated extensions: `zip`, `tar`, `gz`, `bz2`, `xz`, `7z`, `rar`
    - `DatabaseElastic`: Associated extensions: `eps`
    - `Data`/`DataVolume`: No associated extensions, can be used for user specification
    - `IbmWatsonxCodeAssistantForZRefactor`/`Code`: No associated extensions, can be used for user specification
    - `VideoPlayer`: Associated extensions: `mp4`, `avi`, `mov`, `mkv`, `webm`
    - `Image`: No associated extensions, can be used for user specification
    - `DocumentDownload`: Default icon
  - a list of strings or a single string, each string will be the `src` and `tip` will be inferred from the `src`. The `icon` will be `auto`.

### Iframe

An iframe component to embed an external page.

Properties:

- `src`: the url of the page to embed
- `width`: the width of the iframe
- `title`: the title of the iframe
- `frameborder`: the border of the iframe

### Markdown

A markdown tag is processed at server side by python, which is not implemented as a svelte component. So you don't need to import it in `script` tag.

Everything inside the `<Markdown>` is passed to `markdown.markdown()` from python `Markdown` package to convert to html.

## Advanced usage

### Using self-defined components

Say you have a set of components that you want to use in all your reports. You can specify the path to the directory containing the components in `report_extlibs` by either `pipen report config --extlibs <path>` or `pipeline.config.plugin_opts.report_extlibs = <path>`.

Then you can import the components from the path you specified.

```jsx
<script>
    import { MyComponent } from '$extlibs/MyComponent.svelte';
</script>
```

You can write your own components based on `carbon-components-svelte` components.

Note that the shortcut `$ccs` is not available in the components you write. You have to use 'carbon-components-svelte'.

!!! Tip

    You can also use the aliases/shortcuts for modules in your components. See [Using builtin components](#using-builtin-components) for the list of aliases.

    For those relative paths, you have to pay attention to the path of your components.
    The `extlibs` are symbolically linked to the `~/.pipen/Pipeline/.report-workdir/src/extlibs/{{extlibs.split("/")[-1]}}` directory. So you have to use the relative path from the `~/.pipen/Pipeline/.report-workdir/src/extlibs/{{extlibs.split("/")[-1]}}` directory. So it is Okay to use the aliases/shortcuts when your components are directly under the `extlibs` directory.
    If your components are in a subdirectory, you have to go up more levels for the components. For example, let's say your component is in `<extlibs>/components/MyComponent.svelte`, then you have to import it like this:

    ```jsx
    <script>
        // instead of using $libs
        import { Image } from '../../../components';
    </script>
    ```

### Using other svelte components

- Can you use other svelte components?

    Yes. But you have to do it for every pipeline run. And you have to set `report_nobuild` to `True`.

- How?

    In the working directory (`~/.pipen/Pipeline/.report-workdir/`), remove `node_modules` and make a copy of `package.json` instead of a symbolinc link. This is important, you may not want to pollute the global one.

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

### Converting paths to urls

When we write a report template, we usually specify the path on the file system to the resources. But when we want to deploy the report, we need to convert the paths to urls, so that the resources can be accessed by the browser.

Here is the rule to convert the paths to urls:

- If the resource is a file from process results, which are usually stored in one-level up from the `REPORTS` directory, the path should be converted to a relative path to the `REPORTS` directory. For example, if the `REPORTS` directory is `/path/to/REPORTS`, the path to the resource is `/path/to/someproc/image.png`, then the converted path should be `../someproc/image.png`.
- If the resource is a file from process results, but the process does not exports the results to the output directory (i.e. some intermediate processes), the resource will be copied to `/path/to/REPORTS/data` directory. The converted path should be `data/image.<id>.png`, where `<id>` is associated with the raw resource path.
- A relative path or a URL to the resource will be kept as is.

When we are using other, self-defined or external components, we should register the tag and the property with the path for conversion.

For example, if we have a component `MyComponent` that has a property `src` that is a path to a resource, we should register the tag and the property with the path for conversion, using the `report_relpath_tags` configuration.

```python
from pipen import Pipen

class Pipeline(Pipen):
    plugin_opts = {
        "report_relpath_tags": {
            "MyComponent": "src",
            "MyComponent2": ["src", "src2"],  # multiple properties
        }
    }
```

Already registered tags are:

```python
{
    "a": "href",
    "embed": "src",
    "img": "src",
    "Link": "href",
    "Image": ("src", "download"),
    "ImageLoader": "src",
    "DataTable": "src",
    "iframe": "src",
    "Iframe": "src",
    "Download": "href",
}
```

[1]: https://github.com/carbon-design-system/carbon-components-svelte
[2]: http://ibm.biz/carbon-svelte
[3]: https://smeltejs.com/
