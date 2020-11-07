from pathlib import Path
from pipen import Proc, Pipen

HERE = Path(__file__).parent

class Subset(Proc):
    """Subset the input data using pandas"""
    input_keys = 'datafile'
    input = ['https://raw.githubusercontent.com/tidyverse/ggplot2/master/data-raw/mpg.csv']
    output = 'outfile:file:mpg-subset.csv'
    lang = 'python'
    script = """
        import pandas
        data = pandas.read_csv('{{in.datafile}}')
        data = data[['model', 'displ']]
        data.to_csv('{{out.outfile}}')
    """
    plugin_opts = {'report': True}

class Plot(Proc):
    """Plot the data with ggplot2 in R"""
    requires = Subset
    input_keys = 'datafile:file'
    output = 'plotfile:file:mpg.png'
    lang = 'Rscript'
    script = """
        library(ggplot2)
        data = read.csv('{{in.datafile}}')
        png('{{out.plotfile}}')
        ggplot(data) + geom_boxplot(aes(x=model, y=displ)) +
            theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1))
        dev.off()
    """

if __name__ == '__main__':
    pipen = Pipen(name='plot-mpg', outdir=HERE / 'output', starts=Subset)
    pipen.run()
