# Filters

Filters are used in template rendering. They are defined in `filters.py` and
can be used in the template files.

## `datatable`

Read data from a file, using pandas.read_csv() and make it to json so
js can handle it and render it with `<DataTable />`

- Args:
    - `path` (PathLike): The path to the data file.
    - `*args` (Any): Additional positional arguments to pass to pandas.read_csv().
    - `ncols` (Union[int, Iterable], optional): Either the number of columns to
        select or an iterable of column indices or names. Defaults to None.
    - `nrows` (Union[int, Iterable], optional): Either the number of rows to select
        or an iterable of row indices. Defaults to None.
    - `double_precision` (int, optional): The precision for double numbers.
        See also pandas.DataFrame.to_json(). Defaults to 4.
    - `excluded` (set, optional): A set of column names to exclude from the resulting
        DataFrame. Defaults to None.
    - `**kwargs` (Any): Additional keyword arguments to pass to pandas.read_csv().
      - Note that `sep` is set to `"\t"` instead of `,` by default.

- Returns:
    `str`: A JSON format of the data.

- Examples:

    ```html
    <DataTable data="{{ '/path/to/data.tsv' | datatable: nrows=10) }}" />
    ```

    ```html
    <DataTable data="{{ '/path/to/data.tsv' | datatable: nrows=10, excluded={'col1', 'col2'}) }}" />
    ```

## `render_job`

Generate the `svelte` components for a job.

- Args:

    - `job` (Mapping[str, Any]): The job object used to render the template.
    - `report_file` (str): Absolute path to a report file or relative to `job.outdir`
    - `h` (int): The starting level of the headers

- Examples:

    A json should be defined at `<job.outdir>/report.json` for the report structure:

    ```json
    {
      "h1": {
        "h2": {
          "h3": {
            "ui": [
              {
                "kind": "datatable",
                "src": "data.tsv"
              },
              # more components
            ]
          }
        }
      }
    }
    ```

    The `h2` and `h3` are optional. You can set them to `#xxx` to let `pipen-report` to
    ignore them. Same `h2`s are also supported. You can use `#<suffiex>` to make them
    different. For example, `Heading2#1` and `Heading2#2` to have two `h2` with the same
    name under the same `h1`.

    For details of `ui` and components, see following sections.

## `render_ui`

Render a set of components with a certain `ui` layout.

In the `report.json` file, under `h3`, you should specify a dict with `ui` keys, which defined a large set of components. Supported `ui`s are:

- `flat`: The components will be rendered sequentially.
- `tabs`: The components will be rendered as tabs. Each component should be with `kind` `"tab"`. If not specified, `kind = "tab"` will be added automatically.
- `table_of_images`: The components will be rendered as a table of images. Each component should be with `kind` `"table_image"`. If not specified, `kind = "image"` will be added automatically. You can specify the number of columns like `table_of_images:3`. The default number of columns is 2.
- `accordion`: The components will be rendered as an accordion. Each component should be with `kind` `"accordion"`. If not specified, `kind = "accordion"` will be added automatically.

This can also be used as a filter in the template files by passing a json object and the `ui`:

- Args:

    - `contents` (List[Mapping[str, Any]]): The contents of components to render.
    - `ui` (str): The `ui` layout to render.
    - `job` (Mapping[str, Any]): The job object used to render the template.
    - `level` (int): The indent level of the components. Defaults to 0.

### UI: `flat`

A `flat` ui will render the components sequentially.

```html
<Component1 />
<Component2 />
<Component3 />
<!-- ... -->
```

### UI: `tabs`

A `tabs` ui will render the components as tabs. See also the [`Tabs`](https://carbon-components-svelte.onrender.com/components/Tabs) component of `carbon-components-svelte`.

```html
<Tabs>
  <Tab label="Component1" />
  <Tab label="Component2" />
  <Tab title="Component3" />
  <svelte:fragment>
    <TabContent>
      <ui of Component1 />
    </TabContent>
    <TabContent>
      <ui of Component2 />
    </TabContent>
    <TabContent>
      <ui of Component3 />
    </TabContent>
  </svelte:fragment>
</Tabs>
```

See also [```Component: `tab```](#component-tab) for how each component is rendered.

### UI: `table_of_images`

A `table_of_images` ui will render the components as a table of images.

```html
<div class="pipen-report-table-of-images" style="grid-template-columns: repeat(2, auto); ">
    <div>
        <!-- A tab_image component -->
        <Descr title="Image 2" class="pipen-report-table-image-descr">This is a description about the image.</Descr>
        <Image src="placeholder.png"
        class="pipen-report-table-image"
        width={ 526 }
        height={ 360 } />
        <!-- end of tab_image component -->
    </div>
    <div>
        <Descr title="Image 3" class="pipen-report-table-image-descr">This is a description about the image.</Descr>
        <Image src="placeholder.png"
        class="pipen-report-table-image"
        width={ 526 }
        height={ 360 } />
    </div>
</div>
```

See also [Component: `table_image`](#component-table_image) for how each component is rendered.

### UI: `accordion`

A `accordion` ui will render the components as an accordion. See also the [`Accordion`](https://carbon-components-svelte.onrender.com/components/Accordion) component of `carbon-components-svelte`.

```html
<Accordion>
    <AccordionItem title="title of Component1">
        <ui of Component1 />
    </AccordionItem>
    <AccordionItem title="title of Component2">
        <ui of Component2 />
    </AccordionItem>
    <AccordionItem title="title of Component3">
        <ui of Component3 />
    </AccordionItem>
</Accordion>
```

See also [Component: `accordion`](#component-accordion) for how each component is rendered.

## `render_component`

Each component of the `ui` should be rendered with this filter.

- Args:

    - `component` (Mapping[str, Any]): The component to render.
    - `job` (Mapping[str, Any]): The job object used to render the template.
    - `level` (int): The indent level of the components. Defaults to 0.

### Component: `accordion`

Full configuration of an `accordion` item:

```python
{
  "kind": "accordion",  # When under an `accordion` ui, this can be omitted
  "title": "title of the accordion",
  "ui": "flat",  # The ui of the components under this accordion item
  "contents": [ ... ]  # The components to render under this accordion item using the `ui`
}
```

This will be rendered as:

```html
<AccordionItem title="title of the accordion">
    <ui of the components under this accordion item using the `ui` />
</AccordionItem>
```

### Component: `descr`

Full configuration of a `descr` component:

```python
{
    "kind": "descr",
    "title": "title of the descr",  # or use key `name`
    "content": "The description content",  # or use key `descr`
}
```

This will be rendered as:

```html
<Descr title="title of the descr">The description content</Descr>
```

### Component: `error`

Full configuration of an `error` component:

```python
{
    "kind": "error",
    "content": "The error content",
    "kind_": "warning",  # use the warning style by default
    # more props passed to InlineNotification
}
```

This will be rendered as:

```html
<InlineNotification kind="warning">The error content</InlineNotification>
```

See also the [`InlineNotification`](https://carbon-components-svelte.onrender.com/components/InlineNotification) component of `carbon-components-svelte`.

### Component: `list`

Render a list of items. Full configuration of a `list` component:

```python
{
    "kind": "list",
    "items": [
        "item1",
        "item2",
        "item3",
        # ...
    ],
    "ordered": False,  # Whether to render an ordered list (OrderedList)
}
```

This will be rendered as:

```html
<UnorderedList>
    <ListItem>item1</ListItem>
    <ListItem>item2</ListItem>
    <ListItem>item3</ListItem>
    <!-- ... -->
</UnorderedList>
```

### Component: `table`

Render a data table. Full configuration of a `table` component:

```python
{
    "kind": "table",
    # Arguments passed to pandas.read_csv()
    # See datatable filter for details
    # If path is not specified, `src` will be used
    "data": {},
    # The path to the data file
    # You can set to False, so that download the datafile is disabled
    # If so, you need to set path in `data` to let the datatable filter to read the data
    "src": "/path/to/data.tsv",
    # Other arguments passed to DataTable
}
```

This will be rendered as:

```html
<DataTable data={ [ ... ] } />
```

See also the [`DataTable`](https://carbon-components-svelte.onrender.com/components/DataTable) component of `carbon-components-svelte`.

### Component: `image`

Render an image. Full configuration of an `image` component:

```python
{
    "kind": "image",
    "src": "/path/to/image.png",  # The path to the image file
    "width": 526,  # The width of the image
    "height": 360,  # The height of the image
    # Other arguments passed to Image
}
```

This will be rendered as:

```html
<Image src="/path/to/image.png" width={ 526 } height={ 360 } />
```

The `width` and `height` are optional. If not specified, the size will be obtained from the image file using `pillow`. This is useful for the loading placeholder to have the same size as the image.

### Component: `table_image`

Render a table of images. Full configuration of a `table_image` component:

```python
{
    "kind": "table_image",
    "src": "/path/to/image.png",  # The path to the image file
    "name": "Image 1",  # The name of the image
    "descr": "This is a description about the image.",  # The description of the image
    # Other arguments passed to Image
}
```

This will be rendered as:

```html
<div>
    <Descr title="Image 1" class="pipen-report-table-image-descr">
    This is a description about the image.
    </Descr>
    <Image src="placeholder.png"
        class="pipen-report-table-image"
        width={ 526 }
        height={ 360 } />
</div>
```

### Component: `tab`

Render a tab. Full configuration of a `tab` component:

```python
{
    "kind": "tab",
    "label": "label of the tab",  # or use key `name` or `title`
    "ui": "flat",  # The ui of the components under this tab
    "contents": [ ... ]  # The components to render under this tab using the `ui`
}
```

This will be rendered as a tuple of `Tab` and `TabContent`:

```html
<Tab label="label of the tab" />
<!-- and -->
<TabContent>
    <ui of the components under this tab using the `ui` />
</TabContent>
```

See also the [`Tabs`](https://carbon-components-svelte.onrender.com/components/Tabs) component of `carbon-components-svelte`.

### Component: `tag`

You can also directly use a `tag` (`<tag ... />`) as a component. Full configuration of a `tag` component:

```python
{
    "kind": "tag",
    "tag": "tag-name",  # The tag name
    # Other attributes passed to the tag
}
```

This will be rendered as:

```html
<tag-name ... />
```

!!! Attention

    To build the report using the above filters, you need to import the components in the template files manually:

    ```html
    <script>
        import { Descr, Image, DataTable } from "$libs";
        import { Accordion, AccordionItem, Tabs, Tab, TabContent } from "$ccs";
        // import more if needed, e.g InlineNotification, OrderedList, UnorderedList, ListItem, etc
    </script>

    {{ job | render_job }}
    ```
