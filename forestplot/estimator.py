import numpy as np
from lifelines import CoxPHFitter

from forestplot import MISSING, PVALUE_NAME, PV_INTER_NAME, SUBGROUPS_NAME


def Hazard_Ratio(df, treatment, time, event):
    if df.shape[0] < 20:
        return None
    cph = CoxPHFitter()
    cph.fit(df[[treatment, time, event]], duration_col=time, event_col=event)
    return {
        'CI': np.exp(cph.confidence_intervals_.loc[treatment].values),
        PVALUE_NAME: cph.summary.at[treatment, 'p']
    }


def Hazard_Ratio_interaction(df, bins, treatment, time, event):
    res = {SUBGROUPS_NAME: {}}
    mods = df[bins].dropna().unique()
    for mod in mods:
        hr = Hazard_Ratio(df[df[bins] == mod], treatment=treatment, time=time, event=event)
        if hr is not None:
            ci = hr['CI']
            res[SUBGROUPS_NAME][mod] = f'{round(ci.mean(), 2)}({round(ci[0], 2)}-{round(ci[1], 2)})'
    mods = [mod for mod in mods if mod != MISSING]

    cph = CoxPHFitter()
    df_ = df.loc[df[bins].isin(mods), [bins, time, event]]
    df_[bins] = df_[bins].apply(lambda x: mods.index(x))
    cph.fit(df_, duration_col=time, event_col=event)
    res[PVALUE_NAME] = cph.summary.at[bins, 'p']

    res[PV_INTER_NAME] = np.nan
    cph = CoxPHFitter()
    df_ = df.loc[df[bins].isin(mods), [bins, treatment, time, event]]
    df_[bins] = df_[bins].apply(lambda x: mods.index(x))
    df_[PV_INTER_NAME] = df_[bins] * df_[treatment]
    try:
        cph.fit(df_, duration_col=time, event_col=event)
        res[PV_INTER_NAME] = cph.summary.at[PV_INTER_NAME, 'p']
    except:
        print(f'Cox failed for {bins}')
    return res
