# RT-Analyses-Demo

Extracting reaction times from fMRI task event logs.

A small Python repo demonstrating how to pull per-trial RTs out of the kind of behavioral output files fMRI tasks produce — Presentation `.log` files and BIDS `events.tsv` files. Includes synthetic example data, a parser library, summary stats, and a CLI.

The point: when you run a task in the scanner the behavioral software dumps timestamps and button presses. Computing RT is straightforward once you know which columns mean what, but every task encodes it differently. This repo shows the pattern.

## Quick start

```bash
pip install -e .
rt-demo extract examples/synthetic_data/sub-01_task-demo_run-1.log
```

That prints a per-trial RT table to stdout.

## What's in here

- `rt_demo/` — the Python package
- `examples/` — synthetic data + notebook walkthrough
- `tests/` — pytest suite
- `.github/workflows/` — CI runs the tests on every push

More below as the pieces land.
