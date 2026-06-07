"""
Per-subject (or per-anything-else) RT summary stats.

Functions take a per-trial RT DataFrame (from `rt_demo.extract.extract_rts`)
and return one summary row per group: n / mean / median / SD / min / max,
plus the number of missed trials.

Missed trials are rows with empty rt_ms — they count toward n_total but not
toward the moments.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def summarize(rts: pd.DataFrame, group_cols: list[str] | None = None) -> pd.DataFrame:
    """
    Return a summary DataFrame.

    If `group_cols` is given, group by them; otherwise return one overall row.
    """
    if rts.empty:
        return pd.DataFrame()

    # numeric RT column where missing → NaN
    rt = pd.to_numeric(rts["rt_ms"], errors="coerce")
    df = rts.copy()
    df["_rt"] = rt

    if not group_cols:
        return _one_group(df).to_frame().T.reset_index(drop=True)

    return (df.groupby(group_cols, dropna=False, group_keys=True)[df.columns.difference(group_cols).tolist()]
              .apply(_one_group)
              .reset_index())


def _one_group(g: pd.DataFrame) -> pd.Series:
    rt = g["_rt"].dropna()
    n_total = len(g)
    n_resp  = int(rt.notna().sum())
    return pd.Series({
        "n_total_trials": n_total,
        "n_responded":    n_resp,
        "n_missed":       n_total - n_resp,
        "mean_rt_ms":     float(rt.mean())   if n_resp else np.nan,
        "median_rt_ms":   float(rt.median()) if n_resp else np.nan,
        "sd_rt_ms":       float(rt.std())    if n_resp > 1 else np.nan,
        "min_rt_ms":      float(rt.min())    if n_resp else np.nan,
        "max_rt_ms":      float(rt.max())    if n_resp else np.nan,
    })
