import numpy as np
import pandas as pd
from lorem.text import TextLorem


def sample_cat(n, n_mod=3, with_nan=True):
    mods = [str(i) for i in range(n_mod + 1)]
    if with_nan:
        out = np.random.choice(mods, n).astype(object)
        out[out == str(n_mod)] = np.nan
        return out
    else:
        return np.random.choice(mods[:-1], n).astype(object)

def sample_cont(n, loc=0, scale=1, r_nan=0.2):
    out = np.random.normal(loc, scale, n)
    out[np.random.binomial(1, r_nan, n) == 1] = np.nan
    return out

def sample_df(n, trt, time, event):
    text = TextLorem()
    df = pd.DataFrame(None)
    for n_mod in [2, 5, 3]:
        for with_nan in [0, 1]:
            df[text._word()] = sample_cat(n, n_mod=n_mod, with_nan=with_nan==1)
    for r_nan in [0., 0.3]:
        df[text._word()] = sample_cont(n, r_nan=r_nan)
    df[trt] = np.random.choice(2, n)
    df[event] = np.random.choice(2, n)
    df[time] = np.random.exponential(1, n)
    return df
