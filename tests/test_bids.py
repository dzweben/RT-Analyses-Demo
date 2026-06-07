import io
import textwrap
from pathlib import Path

import pandas as pd

from rt_demo.parsers.bids import parse_events, extract_rts_from_events


WITH_RT = textwrap.dedent("""\
    onset\tduration\ttrial_type\tresponse_time
    0.0\t2.0\tprobe\t0.5
    3.0\t2.0\tprobe\t0.8
    6.0\t2.0\tprobe\tn/a
    """)


WITHOUT_RT = textwrap.dedent("""\
    onset\tduration\ttrial_type
    0.0\t2.0\tprobe
    0.6\t0.05\tresponse
    3.0\t2.0\tprobe
    3.7\t0.05\tresponse
    6.0\t2.0\tprobe
    """)


def _write(tmp_path: Path, text: str, name="events.tsv") -> Path:
    p = tmp_path / name
    p.write_text(text)
    return p


def test_extract_uses_response_time_column(tmp_path: Path):
    p = _write(tmp_path, WITH_RT)
    events = parse_events(p)
    rts = extract_rts_from_events(events)
    assert len(rts) == 3
    assert rts.iloc[0]["rt_ms"] == 500
    assert rts.iloc[1]["rt_ms"] == 800
    # n/a → NaN
    assert pd.isna(rts.iloc[2]["rt_ms"])


def test_extract_pairs_by_onset_when_no_response_time(tmp_path: Path):
    p = _write(tmp_path, WITHOUT_RT)
    events = parse_events(p)
    rts = extract_rts_from_events(events)
    assert len(rts) == 3
    assert rts.iloc[0]["rt_ms"] == 600
    assert abs(rts.iloc[1]["rt_ms"] - 700) < 1e-6
    # last probe has no following response → NaN
    assert pd.isna(rts.iloc[2]["rt_ms"])


def test_missing_trial_type_raises(tmp_path: Path):
    p = _write(tmp_path, "onset\tduration\n0.0\t2.0\n")
    events = parse_events(p)
    try:
        extract_rts_from_events(events)
    except ValueError as e:
        assert "trial_type" in str(e)
    else:
        raise AssertionError("expected ValueError")
