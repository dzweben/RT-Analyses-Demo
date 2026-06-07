"""
Quick RT visualizations: distribution and per-trial time-series.

Returns matplotlib Figure objects so callers can save / display / customize.
No styling opinions enforced.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def plot_rt_distribution(rts: pd.DataFrame, bins: int = 30, title: str | None = None):
    """Histogram of RTs with mean/median lines."""
    fig, ax = plt.subplots(figsize=(6, 4))
    vals = pd.to_numeric(rts["rt_ms"], errors="coerce").dropna()
    if vals.empty:
        ax.text(0.5, 0.5, "no responses", ha="center", va="center")
        return fig

    ax.hist(vals, bins=bins, alpha=0.8, edgecolor="white")
    ax.axvline(vals.mean(),   color="red",  linestyle="--", label=f"mean = {vals.mean():.0f} ms")
    ax.axvline(vals.median(), color="black", linestyle=":",  label=f"median = {vals.median():.0f} ms")
    ax.set_xlabel("RT (ms)")
    ax.set_ylabel("n trials")
    if title:
        ax.set_title(title)
    ax.legend()
    fig.tight_layout()
    return fig


def plot_rt_over_trials(rts: pd.DataFrame, title: str | None = None):
    """Per-trial RT scatter — handy to see drift or warm-up effects."""
    fig, ax = plt.subplots(figsize=(8, 3))
    df = rts.copy()
    df["rt_ms_num"] = pd.to_numeric(df["rt_ms"], errors="coerce")

    ax.scatter(df["trial"], df["rt_ms_num"], s=15, alpha=0.7)
    missed = df[df["rt_ms_num"].isna()]
    if not missed.empty:
        ax.scatter(missed["trial"], np.zeros(len(missed)) - 50,
                   marker="x", color="red", s=20, label=f"missed ({len(missed)})")
        ax.legend()
    ax.set_xlabel("trial")
    ax.set_ylabel("RT (ms)")
    if title:
        ax.set_title(title)
    fig.tight_layout()
    return fig
