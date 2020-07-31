import pandas as pd

from forestplot import MISSING
from forestplot.estimator import Hazard_Ratio_interaction


def analyse(df, treatment, time, event, max_mod=10, dropna=True):
    feats = [f for f in df.columns if f not in [treatment, time, event]]
    res = {}
    for feat in feats:
        df_ = df.copy()
        df_[feat] = binning(df[feat], max_mod=max_mod, dropna=dropna)
        res[feat] = Hazard_Ratio_interaction(df_, feat, treatment, time, event)
    return res


def binning(series, max_mod=10, dropna=True):
    counts = series.value_counts(dropna=dropna)
    out = pd.Series(None, index=series.index)
    if not dropna:
        out[series.isna()] = MISSING
    if counts.shape[0] < max_mod:
        for cat in counts.index:
            if not pd.isnull(cat):
                out[series == cat] = str(cat)
    else:
        med = round(series.median(), 2)

        def split(x):
            return f' ⩽{med}' if x <= med else f' >{med}'

        out[~series.isna()] = series.dropna().apply(split)
        if (f' ⩽{med}' not in out.unique()) or (f' >{med}' not in out.unique()):
            def split(x): return f' <{med}' if x < med else f' ⩾{med}'

            out[~series.isna()] = series.dropna().apply(split)
    return out
