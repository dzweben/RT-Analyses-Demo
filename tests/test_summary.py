import pandas as pd

from rt_demo.summary import summarize


def _rts(values, group=None):
    df = pd.DataFrame({"trial": range(len(values)), "rt_ms": values})
    if group is not None:
        df["group"] = group
    return df


def test_overall_no_misses():
    df = _rts([100, 200, 300, 400])
    out = summarize(df)
    assert len(out) == 1
    row = out.iloc[0]
    assert row.n_total_trials == 4
    assert row.n_responded == 4
    assert row.n_missed == 0
    assert row.mean_rt_ms == 250
    assert row.median_rt_ms == 250
    assert row.min_rt_ms == 100
    assert row.max_rt_ms == 400


def test_handles_missed_trials():
    df = _rts([100, "", 300, ""])
    out = summarize(df)
    row = out.iloc[0]
    assert row.n_total_trials == 4
    assert row.n_responded == 2
    assert row.n_missed == 2
    assert row.mean_rt_ms == 200


def test_group_by_subject():
    df = pd.concat([
        _rts([100, 200], group="s1"),
        _rts([400, 500, 600], group="s2"),
    ], ignore_index=True)
    out = summarize(df, group_cols=["group"])
    out = out.sort_values("group").reset_index(drop=True)
    assert list(out["group"]) == ["s1", "s2"]
    assert out.loc[0, "n_total_trials"] == 2
    assert out.loc[1, "mean_rt_ms"] == 500


def test_empty_input_returns_empty():
    out = summarize(pd.DataFrame())
    assert out.empty
