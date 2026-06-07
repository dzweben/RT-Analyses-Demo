"""
Parse BIDS events.tsv files.

BIDS spec: each row is one task event with columns `onset` (s), `duration` (s),
and `trial_type`. Optional columns: `response_time` (s), `value`, `stim_file`.

If `response_time` is present, you can read it directly per row. If it isn't,
you derive RT yourself by pairing rows of one trial_type (the probe) with the
next rows of another trial_type (the response).

This parser handles both cases.
"""

from __future__ import annotations

from pathlib import Path
import pandas as pd


def parse_events(path: str | Path) -> pd.DataFrame:
    """Read a BIDS events.tsv. Returns a DataFrame with onset/duration in seconds."""
    df = pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False)
    for col in ("onset", "duration", "response_time"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def extract_rts_from_events(
    events: pd.DataFrame,
    probe_type: str = "probe",
    response_type: str = "response",
) -> pd.DataFrame:
    """
    Compute RT by pairing probe rows with the next response row.

    If the events file already has a `response_time` column on the probe rows,
    we use that directly (and skip the pairing step).

    Returns a per-probe DataFrame: trial_type, probe_onset_s, response_onset_s,
    rt_ms.
    """
    if "trial_type" not in events.columns:
        raise ValueError("events file is missing trial_type column")

    probes = events[events["trial_type"] == probe_type].reset_index(drop=True)
    if probes.empty:
        return pd.DataFrame(columns=["trial", "probe_onset_s", "response_onset_s", "rt_ms"])

    # path 1: probe row already has response_time in seconds
    if "response_time" in probes.columns and probes["response_time"].notna().any():
        out = probes.copy()
        out["rt_ms"] = out["response_time"] * 1000
        out["probe_onset_s"] = out["onset"]
        out["response_onset_s"] = out["onset"] + out["response_time"]
        out["trial"] = range(1, len(out) + 1)
        return out[["trial", "probe_onset_s", "response_onset_s", "rt_ms"]].reset_index(drop=True)

    # path 2: pair probe rows with the next response row by onset order
    responses = events[events["trial_type"] == response_type].reset_index(drop=True)
    rows = []
    for i, probe in probes.iterrows():
        nxt = responses[responses["onset"] > probe["onset"]]
        if nxt.empty:
            rt_ms = pd.NA
            resp_onset = pd.NA
        else:
            resp_onset = nxt.iloc[0]["onset"]
            rt_ms = (resp_onset - probe["onset"]) * 1000
        rows.append({
            "trial": i + 1,
            "probe_onset_s": probe["onset"],
            "response_onset_s": resp_onset,
            "rt_ms": rt_ms,
        })
    return pd.DataFrame(rows)
