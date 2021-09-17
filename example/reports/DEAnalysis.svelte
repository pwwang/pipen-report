<script>
    import { DataTable, Image } from '@@';
</script>

<h1>Mean-variance plot</h1>
<p>
    The plot on the left is created within the voom function which extracts residual variances from fitting linear models to log-CPM transformed data. Variances are then rescaled to quarter-root variances (or square-root of standard deviations) and plotted against the mean expression of each gene. The means are log2-transformed mean-counts with an offset of 2. The plot on the right is created using plotSA which plots log2 residual standard deviations against mean log-CPM values. The average log2 residual standard deviation is marked by a horizontal blue line. In both plots, each black dot represents a gene and a red curve is fitted to these points.
</p>
<Image src={{job.out.outdir | joinpaths: "saplot.png" | quote}} />

<h1>Venn diagram</h1>
<p>
    Venn diagram showing the number of genes DE in the comparison between basal versus LP only (left), basal versus ML only (right), and the number of genes that are DE in both comparisons (center). The number of genes that are not DE in either comparison are marked in the bottom-right.
</p>
<Image src={{job.out.outdir | joinpaths: "venn.png" | quote}} />

<h1>Gene list</h1>

<DataTable
    src={{job.out.outdir | joinpaths: "results.txt" | quote}}
    data={ {{job.out.outdir | joinpaths: "results.txt" | datatable: sep="\t", nrows=100}} }
/>
