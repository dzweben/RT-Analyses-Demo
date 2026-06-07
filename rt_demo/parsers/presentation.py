"""
Parse Presentation (NBS) .log files.

Presentation logs have a short text header, then tab-delimited rows. Each row
is one event — Picture, Response, Pulse, Sound, Nothing, Text Input.

Standard columns:
    Subject  Trial  Event Type  Code  Time  TTime  Uncertainty  Duration ...

Time + TTime are in 10 kHz ticks (1 tick = 0.1 ms). To get ms: divide by 10.

Data rows always start with the numeric subject id; the header doesn't.
That's the simplest robust way to skip the header.
"""

from __future__ import annotations

import pandas as pd
from pathlib import Path

# 13 standard columns. Some Presentation versions only emit 8-9 — we pad.
LOG_COLS = [
    "Subject", "Trial", "EventType", "Code", "Time",
    "TTime", "Uncertainty", "Duration", "Uncertainty2",
    "ReqTime", "ReqDur", "StimType", "PairIndex",
]


def parse_log(path: str | Path) -> pd.DataFrame:
    """
    Read a Presentation .log, return a DataFrame keyed by LOG_COLS.

    Rows that don't start with a numeric subject id (i.e. header lines,
    blank lines, format anomalies) are silently dropped.
    """
    path = Path(path)
    rows: list[list[str]] = []
    with path.open(encoding="utf-8", errors="replace") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 5:
                continue
            if not parts[0].strip().isdigit():
                continue
            rows.append((parts + [""] * len(LOG_COLS))[: len(LOG_COLS)])
    return pd.DataFrame(rows, columns=LOG_COLS)


def filter_events(
    df: pd.DataFrame,
    event_type: str | None = None,
    codes: set[str] | None = None,
) -> pd.DataFrame:
    """Convenience: subset by EventType and/or Code."""
    out = df
    if event_type is not None:
        out = out[out["EventType"] == event_type]
    if codes is not None:
        out = out[out["Code"].isin(codes)]
    return out.reset_index(drop=True)
