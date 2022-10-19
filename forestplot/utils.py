import numpy as np
import pandas as pd

pd.options.mode.chained_assignment = None

from forestplot import MISSING, PVALUE_NAME
from forestplot.estimator import Log_HR, CI_NAME, ESTIMATOR_NAME


def interaction(df, treatment, time, event, max_mod=10, dropna=True):
    feats = [f for f in df.columns if f not in [treatment, time, event]]
    results = []
    for feat in feats:
        df_ = df[[feat, treatment, event, time]]
        df_[feat] = binning(df[feat], max_mod=max_mod, dropna=dropna)

        # interaction
        mods = np.sort([mod for mod in df_[feat].dropna().unique() if mod != MISSING])
        res = [(feat, {'fontweight': 'bold'}), None, None]
        if len(mods) == 2:
            inter_name = f'{feat}_inter'
            df_[inter_name] = (df_[feat] == mods[1]).astype(float)
            df_[inter_name] = (df_[inter_name] - df_[inter_name].mean()) * (df_[treatment] - df_[treatment].mean())
            loghr = Log_HR(df_, feature=inter_name, time=time, event=event)
            if loghr is not None:
                res[-1] = str(round(loghr[PVALUE_NAME], 2))
        results.append(res)

        for mod in np.sort(df_[feat].dropna().unique()):
            res = [mod]
            loghr = Log_HR(df_[df_[feat] == mod], feature=treatment, time=time, event=event)
            if loghr is not None:
                ci = loghr[CI_NAME]
                coef = loghr[ESTIMATOR_NAME]
                res.append(f'{round(coef, 2)}({round(ci[0], 2)},{round(ci[1], 2)})')
            else:
                res.append(None)
            res.append(None)
            results.append(res)

    return ['Features', 'log HR', 'p value'], results


def association(df, time, event, max_mod=10, dropna=True):
    feats = [f for f in df.columns if f not in [time, event]]
    results = []
    for feat in feats:
        loghr = Log_HR(df, feature=feat, time=time, event=event)
        if loghr is not None:
            pv = str(round(loghr[PVALUE_NAME], 2))
            ci = loghr[CI_NAME]
            coef = loghr[ESTIMATOR_NAME]
            results.append([feat, f'{round(coef, 2)}({round(ci[0], 2)},{round(ci[1], 2)})', pv])
        else:
            results.append([feat, None, None])
    return ['Features', 'log HR', 'p value'], results


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
        med = series.median()
        medr = round(series.median(), 2)

        def split(x):
            return f' ⩽{medr}' if x <= med else f' >{medr}'

        out[~series.isna()] = series.dropna().apply(split)
        if (f' ⩽{medr}' not in out.unique()) or (f' >{medr}' not in out.unique()):
            def split(x): return f' <{medr}' if x < med else f' ⩾{medr}'

            out[~series.isna()] = series.dropna().apply(split)
    return out
