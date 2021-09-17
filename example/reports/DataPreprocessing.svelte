<script>
    import { Image } from "@@";
</script>

<h1>Removing genes that are lowly expressed</h1>

<p>
    The density of log-CPM values for raw pre-filtered data (A) and post-filtered data (B) are shown for each sample. Dotted vertical lines mark the log-CPM threshold (equivalent to a CPM value of about 0.2) used in the filtering step.
</p>
<Image
    src={{job.outdir | joinpaths: "data_filtering.png" | quote}}
/>

<h1>Normalising gene expression distributions</h1>

<p>
    Example data: Boxplots of log-CPM values showing expression distributions for unnormalised data (A) and normalised data (B) for each sample in the modified dataset where the counts in samples 1 and 2 have been scaled to 5% and 500% of their original values respectively.
</p>
<Image
    src={{job.outdir | joinpaths: "data_normalizing.png" | quote}}
/>

<h1>Unsupervised clustering of samples</h1>
<p>MDS plots of log-CPM values over dimensions 1 and 2 with samples coloured and labeled by sample groups (A) and over dimensions 3 and 4 with samples coloured and labeled by sequencing lane (B). Distances on the plot correspond to the leading fold-change, which is the average (root-mean-square) log2-fold-change for the 500 genes most divergent between each pair of samples by default.</p>

<Image
    src={{job.outdir | joinpaths: "data_clustering.png" | quote}}
/>
