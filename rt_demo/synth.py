"""
Synthetic Presentation-format .log generator.

Make fake but realistic fMRI task logs so the rest of the package has
something to chew on without needing real participant data. The
generated logs follow the same row layout Presentation (NBS) emits:

  Subject  Trial  EventType  Code  Time  TTime  Uncertainty  Duration ...

Trial structure (per "trial"):
    ITI Picture        — fixed display
    Cue Picture        — fixed display
    Probe Picture      — opens response window
    Response           — subject's button press (the RT we want)

Time units are 10 kHz ticks to match Presentation (1 tick = 0.1 ms).
"""

from __future__ import annotations

import random
from pathlib import Path

TICKS_PER_MS = 10
TR_INTERVAL_TICKS = 17_500   # 1.75 s TR, classic fMRI value
DEFAULT_RT_MEAN_MS = 650
DEFAULT_RT_SD_MS = 180
ITI_DUR_TICKS = 30_000       # 3 s
CUE_DUR_TICKS = 5_000        # 0.5 s
PROBE_WINDOW_TICKS = 20_000  # 2 s max response window


def _row(subj, trial, event_type, code, time, ttime=0, dur=""):
    return f"{subj}\t{trial}\t{event_type}\t{code}\t{time}\t{ttime}\t1\t{dur}"


def generate_log(
    out_path: str | Path,
    subject_id: int = 1,
    n_trials: int = 60,
    miss_rate: float = 0.05,
    rt_mean_ms: float = DEFAULT_RT_MEAN_MS,
    rt_sd_ms: float = DEFAULT_RT_SD_MS,
    seed: int = 42,
) -> Path:
    """
    Write a synthetic Presentation .log with `n_trials` trials.

    Each trial has an ITI → cue → probe sequence, with a Response row whose
    TTime is the RT (sampled from a clipped normal in ms, then converted to
    ticks). About `miss_rate` of trials get no Response (subject missed).

    Returns the path written to.
    """
    rng = random.Random(seed)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "Scenario - demo_task",
        "Logfile written - synthetic",
        "",
        "Subject\tTrial\tEvent Type\tCode\tTime\tTTime\tUncertainty\tDuration",
        "",
    ]

    t = 0
    trial_counter = 1
    # a few pre-task button presses (codes 1-2 = experimenter keyboard advance)
    for _ in range(3):
        lines.append(_row(subject_id, 0, "Response", rng.choice([1, 2]), t, t))
        t += 1500

    # main trial loop
    for paradigm_trial in range(1, n_trials + 1):
        # ITI
        t += rng.randint(20_000, 40_000)  # jittered ITI 2-4s
        lines.append(_row(subject_id, trial_counter, "Picture", "iti", t, dur=ITI_DUR_TICKS))
        t += ITI_DUR_TICKS
        trial_counter += 1

        # TR pulse interleaved
        if rng.random() < 0.6:
            lines.append(_row(subject_id, trial_counter, "Pulse", "99", t, 1))

        # Cue
        t += rng.randint(0, 200)
        lines.append(_row(subject_id, trial_counter, "Picture", "cue", t, dur=CUE_DUR_TICKS))
        t += CUE_DUR_TICKS

        # Probe (opens response window)
        probe_onset = t + rng.randint(0, 200)
        lines.append(_row(subject_id, trial_counter, "Picture", "probe", probe_onset, dur=PROBE_WINDOW_TICKS))

        # Response — drawn from clipped normal, possibly skipped
        if rng.random() >= miss_rate:
            rt_ms = max(80, rng.gauss(rt_mean_ms, rt_sd_ms))
            rt_ms = min(rt_ms, PROBE_WINDOW_TICKS / TICKS_PER_MS - 50)
            rt_ticks = int(round(rt_ms * TICKS_PER_MS))
            btn = rng.choice([3, 4, 5, 6, 7])  # 5-button response box
            lines.append(_row(subject_id, trial_counter, "Response", btn,
                              probe_onset + rt_ticks, ttime=rt_ticks))
            t = probe_onset + rt_ticks + 200
        else:
            # no press; probe stays up the full window
            t = probe_onset + PROBE_WINDOW_TICKS

        trial_counter += 1

    out_path.write_text("\n".join(lines) + "\n")
    return out_path
