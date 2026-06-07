"""
Command-line entry point: pull RTs from one or more Presentation .log files.

Usage:
    rt-demo extract PATH [PATH ...]               # write raw RT table to stdout
    rt-demo extract PATH --out output.csv          # write CSV
    rt-demo extract PATH --summary                 # add a summary table at end
    rt-demo synth examples/synth/sub-99.log        # generate a fresh synthetic log
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .parsers.presentation import parse_log
from .extract import extract_rts, ExtractConfig
from .summary import summarize
from .synth import generate_log


def cmd_extract(args):
    all_rows = []
    for path in args.paths:
        df = parse_log(path)
        rts = extract_rts(df, ExtractConfig(
            probe_code=args.probe_code,
            response_codes=set(args.response_codes.split(",")),
        ))
        # tag with source filename so multi-subject runs are mergeable
        rts.insert(0, "subject", Path(path).stem)
        all_rows.append(rts)
    import pandas as pd
    out = pd.concat(all_rows, ignore_index=True) if all_rows else pd.DataFrame()

    target = sys.stdout if args.out is None else open(args.out, "w")
    try:
        out.to_csv(target, index=False)
        if args.summary and not out.empty:
            target.write("\n# summary\n")
            summarize(out, group_cols=["subject"]).to_csv(target, index=False)
    finally:
        if target is not sys.stdout:
            target.close()


def cmd_synth(args):
    path = generate_log(
        args.out,
        subject_id=args.subject_id,
        n_trials=args.n_trials,
        miss_rate=args.miss_rate,
        seed=args.seed,
    )
    print(f"wrote {path}")


def build_parser():
    p = argparse.ArgumentParser(prog="rt-demo")
    sub = p.add_subparsers(dest="cmd", required=True)

    ex = sub.add_parser("extract", help="extract RTs from one or more .log files")
    ex.add_argument("paths", nargs="+", help="Presentation .log paths")
    ex.add_argument("--out", help="output CSV path (default: stdout)")
    ex.add_argument("--probe-code", default="probe",
                    help="Picture Code that opens the response window")
    ex.add_argument("--response-codes", default="3,4,5,6,7",
                    help="comma-separated valid button codes")
    ex.add_argument("--summary", action="store_true",
                    help="append a per-subject summary block")
    ex.set_defaults(func=cmd_extract)

    sy = sub.add_parser("synth", help="generate a synthetic Presentation .log")
    sy.add_argument("out", help="output .log path")
    sy.add_argument("--subject-id", type=int, default=99)
    sy.add_argument("--n-trials", type=int, default=60)
    sy.add_argument("--miss-rate", type=float, default=0.05)
    sy.add_argument("--seed", type=int, default=0)
    sy.set_defaults(func=cmd_synth)

    return p


def main(argv: list[str] | None = None):
    args = build_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
