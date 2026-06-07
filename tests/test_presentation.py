import textwrap
from pathlib import Path

from rt_demo.parsers.presentation import LOG_COLS, parse_log, filter_events


SAMPLE = textwrap.dedent("""\
    Scenario - sample
    Logfile written - 01/01/2026 00:00:00

    Subject\tTrial\tEvent Type\tCode\tTime\tTTime\tUncertainty\tDuration

    9999\t0\tResponse\t1\t100\t100\t1\t
    9999\t1\tPicture\tprobe\t1000\t0\t1\t20000
    9999\t1\tResponse\t3\t1750\t750\t1\t
    9999\t2\tPicture\tprobe\t5000\t0\t1\t20000
    9999\t2\tResponse\t5\t5400\t400\t1\t
    """)


def test_parse_skips_header(tmp_path: Path):
    p = tmp_path / "tiny.log"
    p.write_text(SAMPLE)
    df = parse_log(p)
    # 5 data rows, no header rows
    assert len(df) == 5
    assert list(df.columns) == LOG_COLS
    assert (df["Subject"] == "9999").all()


def test_filter_events_by_type_and_code(tmp_path: Path):
    p = tmp_path / "tiny.log"
    p.write_text(SAMPLE)
    df = parse_log(p)

    probes = filter_events(df, event_type="Picture", codes={"probe"})
    assert len(probes) == 2
    assert (probes["Code"] == "probe").all()

    responses = filter_events(df, event_type="Response")
    assert len(responses) == 3


def test_parse_handles_missing_optional_columns(tmp_path: Path):
    # 8-col log: pad to 13
    p = tmp_path / "short.log"
    p.write_text("1\t0\tResponse\t3\t1000\t1000\t1\t\n")
    df = parse_log(p)
    assert len(df) == 1
    # Should have all 13 columns padded
    assert len(df.columns) == 13
    assert df.iloc[0]["Subject"] == "1"
