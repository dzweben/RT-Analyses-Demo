# Changelog

## 0.1.0 — initial release

- Presentation `.log` parser + extractor (probe Picture → first valid Response)
- BIDS `events.tsv` parser + extractor (response_time column OR onset-pairing fallback)
- Per-group summary stats (mean / median / SD / min / max / counts)
- RT distribution and per-trial scatter plotting helpers
- Synthetic log generator for testable demos without real data
- `rt-demo extract` / `rt-demo synth` CLI
- Notebook walkthrough in `examples/01_walkthrough.ipynb`
- CI: pytest on py3.10, 3.11, 3.12
