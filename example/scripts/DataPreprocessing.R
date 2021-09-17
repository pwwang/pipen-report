library(limma)
library(edgeR)
library(Mus.musculus)
library(RColorBrewer)
library(dplyr)

datadir = {{in.datadir | quote}}
samplefile = {{in.samplefile | quote}}
outdir = {{job.outdir | quote}}
exprfile = {{out.exprfile | quote}}

filtering_fig = file.path(outdir, "data_filtering.png")
normalizing_fig = file.path(outdir, "data_normalizing.png")
clustering_fig = file.path(outdir, "data_clustering.png")

samples = read.table(samplefile, sep=",", header=TRUE, row.names=1)
x <- readDGE(Sys.glob(file.path(datadir, paste0("*", samples$samples, "*.gz"))),
             columns=c(1,3))

class(x)
dim(x)

samplenames <- samples$samples
colnames(x) <- samplenames
group <- as.factor(samples$group)
x$samples$group <- group
lane <- as.factor(samples$lane)
x$samples$lane <- lane

x$samples

geneid <- rownames(x)
genes <- OrganismDbi::select(
    Mus.musculus,
    keys=geneid,
    columns=c("SYMBOL", "TXCHROM"),
    keytype="ENTREZID"
)

dim(genes)
head(genes)

genes <- genes[!duplicated(genes$ENTREZID),]
x$genes <- genes
x

# Transformations from the raw-scale
cpm <- cpm(x)
lcpm <- cpm(x, log=TRUE)

L <- mean(x$samples$lib.size) * 1e-6
M <- median(x$samples$lib.size) * 1e-6
c(L, M)

summary(lcpm)

# Removing genes that are lowly expressed
table(rowSums(x$counts==0)==9)

keep.exprs <- filterByExpr(x, group=group)
x <- x[keep.exprs,, keep.lib.sizes=FALSE]
dim(x)

lcpm.cutoff <- log2(10/M + 2/L)

nsamples <- ncol(x)
col <- brewer.pal(nsamples, "Paired")
data_filtering_plot = function() {
    par(mfrow=c(1,2))
    plot(density(lcpm[,1]), col=col[1], lwd=2, ylim=c(0,0.26), las=2, main="", xlab="")
    title(main="A. Raw data", xlab="Log-cpm")
    abline(v=lcpm.cutoff, lty=3)
    for (i in 2:nsamples){
    den <- density(lcpm[,i])
    lines(den$x, den$y, col=col[i], lwd=2)
    }
    legend("topright", samplenames, text.col=col, bty="n")
    lcpm <- cpm(x, log=TRUE)
    plot(density(lcpm[,1]), col=col[1], lwd=2, ylim=c(0,0.26), las=2, main="", xlab="")
    title(main="B. Filtered data", xlab="Log-cpm")
    abline(v=lcpm.cutoff, lty=3)
    for (i in 2:nsamples){
    den <- density(lcpm[,i])
    lines(den$x, den$y, col=col[i], lwd=2)
    }
    legend("topright", samplenames, text.col=col, bty="n")
}

png(filtering_fig, res=100, width=800, height=500)
data_filtering_plot()
dev.off()

x <- calcNormFactors(x, method = "TMM")
x$samples$norm.factors

x2 <- x
x2$samples$norm.factors <- 1
x2$counts[,1] <- ceiling(x2$counts[,1]*0.05)
x2$counts[,2] <- x2$counts[,2]*5

data_normalizing_plot = function() {
    par(mfrow=c(1,2))
    lcpm <- cpm(x2, log=TRUE)
    boxplot(lcpm, las=2, col=col, main="")
    title(main="A. Example: Unnormalised data", ylab="Log-cpm")
    x2 <- calcNormFactors(x2)
    x2$samples$norm.factors
    ## [1] 0.0577 6.0829 1.2202 1.1648 1.1966 1.0466 1.1505 1.2543 1.1090

    lcpm <- cpm(x2, log=TRUE)
    boxplot(lcpm, las=2, col=col, main="")
    title(main="B. Example: Normalised data", ylab="Log-cpm")
}
png(normalizing_fig, res=100, width=800, height=500)
data_normalizing_plot()
dev.off()

lcpm <- cpm(x, log=TRUE)
data_clustering_plot = function() {
    par(mfrow=c(1,2))
    col.group <- group
    levels(col.group) <-  brewer.pal(nlevels(col.group), "Set1")
    col.group <- as.character(col.group)
    col.lane <- lane
    levels(col.lane) <-  brewer.pal(nlevels(col.lane), "Set2")
    col.lane <- as.character(col.lane)
    plotMDS(lcpm, labels=group, col=col.group)
    title(main="A. Sample groups")

    plotMDS(lcpm, labels=lane, col=col.lane, dim=c(3,4))
    title(main="B. Sequencing lanes")
}
png(clustering_fig, res=100, width=800, height=500)
data_clustering_plot()
dev.off()

saveRDS(x, exprfile)


