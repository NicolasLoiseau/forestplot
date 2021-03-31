import numpy as np
from lifelines import CoxPHFitter

from forestplot import PVALUE_NAME, ESTIMATOR_NAME, CI_NAME


def Log_HR(df, feature, time, event):
    df = df[df[feature].notna()]
    if df.shape[0] < 20:
        return None
    cph = CoxPHFitter()
    cph.fit(df[[feature, time, event]], duration_col=time, event_col=event)
    return {
        ESTIMATOR_NAME: np.log(cph.hazard_ratios_.at[feature]),
        CI_NAME: cph.confidence_intervals_.loc[feature].values,
        PVALUE_NAME: cph.summary.at[feature, 'p']
    }
