<script>
    import { DataTable, Image } from '$components';
    import { Tile, Tabs, Tab, TabContent } from 'carbon-components-svelte';
</script>

<h1>Mean-variance plot</h1>
<p>
    The plot on the left is created within the voom function which extracts residual variances from fitting linear models to log-CPM transformed data. Variances are then rescaled to quarter-root variances (or square-root of standard deviations) and plotted against the mean expression of each gene. The means are log2-transformed mean-counts with an offset of 2. The plot on the right is created using plotSA which plots log2 residual standard deviations against mean log-CPM values. The average log2 residual standard deviation is marked by a horizontal blue line. In both plots, each black dot represents a gene and a red curve is fitted to these points.
</p>
<Image src={{job.out.outdir | joinpaths: "saplot.png" | quote}} />

<h1>Gene list</h1>

<DataTable
    src={{job.out.outdir | joinpaths: "results.txt" | quote}}
    data={ {{job.out.outdir | joinpaths: "results.txt" | datatable: sep="\t", nrows=100}} }
/>

<h1>Gene list</h1>

<Tile>
    Added intentionally to test <a href="https://github.com/pwwang/pipen-report/issues/3">[#3]</a>
</Tile>

<h1>Examining DE genes</h1>

<Tabs>
    <Tab label="Venn diagram" />
    <Tab label="Volcano plot" />
    <Tab label="Heatmap" />
    <div slot="content">
        <TabContent>
            <p>
                Venn diagram showing the number of genes DE in the comparison between basal versus LP only (left), basal versus ML only (right), and the number of genes that are DE in both comparisons (center). The number of genes that are not DE in either comparison are marked in the bottom-right.
            </p>
            <Image src={{job.out.outdir | joinpaths: "venn.png" | quote}} />
        </TabContent>

        <TabContent>
            <p>
                A volcano plot displays log fold changes on the x-axis versus a measure of statistical significance on the y-axis. Here the significance measure can be -log(p-value), which give the posterior log-odds of differential expression.
            </p>
            <Image src={{job.out.outdir | joinpaths: "vol.png" | quote}} />
        </TabContent>

        <TabContent>
            <p>
                Heatmap of log-CPM values for top 100 genes DE in basal versus LP. Expression across each gene (or row) have been scaled so that mean expression is zero and standard deviation is one. Samples with relatively high expression of a given gene are marked in red and samples with relatively low expression are marked in blue. Lighter shades and white represent genes with intermediate expression levels. Samples and genes have been reordered by the method of hierarchical clustering. A dendrogram is shown for the sample clustering.
            </p>
            <Image src={{job.out.outdir | joinpaths: "heatmap.png" | quote}} />
        </TabContent>
    </div>
</Tabs>
