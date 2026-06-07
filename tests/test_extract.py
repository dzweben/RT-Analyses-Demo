from pathlib import Path

from rt_demo.synth import generate_log
from rt_demo.parsers.presentation import parse_log
from rt_demo.extract import extract_rts, ExtractConfig


def _make_log(tmp_path: Path, **kwargs) -> Path:
    return generate_log(tmp_path / "sub.log", subject_id=1, **kwargs)


def test_extract_recovers_all_trials_with_no_misses(tmp_path: Path):
    log = _make_log(tmp_path, n_trials=20, miss_rate=0.0, seed=7)
    df = parse_log(log)
    rts = extract_rts(df)
    assert len(rts) == 20
    assert (rts["rt_ms"] != "").all()
    # all RTs positive
    assert (rts["rt_ms"].astype(float) > 0).all()


def test_miss_rate_produces_empty_rts(tmp_path: Path):
    log = _make_log(tmp_path, n_trials=200, miss_rate=0.25, seed=11)
    df = parse_log(log)
    rts = extract_rts(df)
    n_missed = (rts["rt_ms"] == "").sum()
    # 25% miss rate ± slack on 200 trials
    assert 35 <= n_missed <= 65


def test_response_codes_filter_ignores_advance_keys(tmp_path: Path):
    log = _make_log(tmp_path, n_trials=10, miss_rate=0.0, seed=3)
    df = parse_log(log)
    # restrict response codes to {99} (nothing matches) → all trials missed
    cfg = ExtractConfig(response_codes={"99"})
    rts = extract_rts(df, cfg)
    assert len(rts) == 10
    assert (rts["rt_ms"] == "").all()


def test_rt_matches_synth_seed(tmp_path: Path):
    # generated RT mean should be in the same neighborhood as the synth target
    log = _make_log(tmp_path, n_trials=500, miss_rate=0.0,
                    rt_mean_ms=700, rt_sd_ms=150, seed=42)
    df = parse_log(log)
    rts = extract_rts(df)
    vals = rts["rt_ms"].astype(float)
    assert abs(vals.mean() - 700) < 30   # within 30 ms of target mean
