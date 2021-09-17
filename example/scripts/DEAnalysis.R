library(limma)
library(edgeR)
library(Mus.musculus)
library(RColorBrewer)
library(dplyr)


samplefile = {{in.samplefile | quote}}
exprfile = {{in.exprfile | quote}}

outdir = {{out.outdir | quote}}
saplot = file.path(outdir, "saplot.png")
vennplot = file.path(outdir, "venn.png")
retfile = file.path(outdir, "results.txt")

x = readRDS(exprfile)
samples = read.table(samplefile, sep=",", header=TRUE, row.names=1)

group = samples$group
lane = samples$lane
design <- model.matrix(~0+group+lane)
colnames(design) <- gsub("group", "", colnames(design))
design

contr.matrix <- makeContrasts(
   BasalvsLP = Basal-LP,
   BasalvsML = Basal - ML,
   LPvsML = LP - ML,
   levels = colnames(design))
contr.matrix

v <- voom(x, design, plot=TRUE)
v

vfit <- lmFit(v, design)
vfit <- contrasts.fit(vfit, contrasts=contr.matrix)
efit <- eBayes(vfit)

png(saplot, res=100, width=500, height=500)
plotSA(efit)
dev.off()

summary(decideTests(efit))

tfit <- treat(vfit, lfc=1)
dt <- decideTests(tfit, p.value=0.25)
summary(dt)

de.common <- which(dt[,1]!=0 & dt[,2]!=0)
length(de.common)

## [1] 2784

head(tfit$genes$SYMBOL[de.common], n=20)

##  [1] "Xkr4"          "Rgs20"         "Cpa6"           "A830018L16Rik" "Sulf1"
##  [6] "Eya1"          "Msc"           "Sbspon"         "Pi15"          "Crispld1"
## [11] "Kcnq5"         "Rims1"         "Khdrbs2"        "Ptpn18"        "Prss39"
## [16] "Arhgef4"       "Cnga3"         "2010300C02Rik"  "Aff3"          "Npas2"

png(vennplot, res=70, height=500, width=500)
vennDiagram(dt[,1:2], circle.col=c("turquoise", "salmon"))
dev.off()
write.fit(tfit, dt, file=retfile)
