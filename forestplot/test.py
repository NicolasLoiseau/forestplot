from forestplot.plot import ForestPlot
from forestplot.synthetic import sample_df
from forestplot.utils import interaction, association

trt, T, E = 'trt', 'T', 'E'
delta = 0.5

if __name__ == '__main__':
    df = sample_df(500, trt, T, E)
    headers, results = interaction(df[df.columns[:]], trt, T, E, dropna=False)
    #headers, results = association(df[df.columns[:]], trt, T, E)
    fp = ForestPlot(headers, results, ci_col='log HR', fontsize=20, hmargin=0, vmargin=0.)
    fp.plot(savefig='../tmp/test.png')
