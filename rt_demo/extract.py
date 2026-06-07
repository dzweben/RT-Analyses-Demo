"""
RT extraction: pair each probe Picture with the next valid Response.

The pattern is simple but easy to get wrong:
  1. walk the log in temporal order
  2. when you hit the probe Picture, mark it as the "open" trial
  3. the first Response within that trial's block with a valid button code
     is the RT, and TTime is the latency from probe onset

The probe-Picture code and the valid response button codes are configurable
because every task uses different labels.
"""

from __future__ import annotations

from dataclasses import dataclass
import pandas as pd

TICKS_PER_MS = 10.0


@dataclass
class ExtractConfig:
    probe_code: str = "probe"          # Picture Code that opens the response window
    response_codes: set[str] = None    # valid button codes (strings — log values)
    response_event_type: str = "Response"
    pulse_code: str = "99"

    def __post_init__(self):
        if self.response_codes is None:
            # default = 5-button Cedrus response box (codes 3-7)
            self.response_codes = {"3", "4", "5", "6", "7"}


def extract_rts(log_df: pd.DataFrame, config: ExtractConfig | None = None) -> pd.DataFrame:
    """
    Return a per-trial DataFrame with columns:
      trial, probe_onset_ticks, response_time_ticks, button_code, rt_ms

    `rt_ms` is empty for trials where no valid response landed.
    """
    cfg = config or ExtractConfig()
    rows = []
    current = None  # (trial, probe_time_ticks)

    for _, row in log_df.iterrows():
        try:
            trial = int(row["Trial"])
        except (ValueError, TypeError):
            continue
        ev, code = row["EventType"], row["Code"]

        if ev == "Picture" and code == cfg.probe_code:
            # close out previous trial if it never got a response
            if current is not None:
                rows.append(_make_row(current, None, None))
            try:
                current = (trial, int(row["Time"]))
            except ValueError:
                current = None
            continue

        if (ev == cfg.response_event_type
                and current is not None
                and trial == current[0]
                and code in cfg.response_codes):
            try:
                ttime = int(row["TTime"])
            except ValueError:
                continue
            rows.append(_make_row(current, ttime, code))
            current = None  # only first valid press per trial

    if current is not None:
        rows.append(_make_row(current, None, None))

    return pd.DataFrame(rows)


def _make_row(current, ttime, btn):
    trial, probe_time = current
    rt_ms = ttime / TICKS_PER_MS if ttime is not None else ""
    return {
        "trial":               trial,
        "probe_onset_ticks":   probe_time,
        "response_time_ticks": (probe_time + ttime) if ttime is not None else "",
        "button_code":         btn if btn is not None else "",
        "rt_ms":               rt_ms,
    }
