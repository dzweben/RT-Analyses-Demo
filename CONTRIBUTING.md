# Contributing

If you want to add a parser for another event log format:

1. Drop a module in `rt_demo/parsers/`. The module should expose at minimum a
   `parse_*` function that returns a pandas DataFrame.
2. Write tests in `tests/test_<name>.py`. The synth utilities in
   `rt_demo/synth.py` are happy to fake additional formats.
3. Run `pytest`. CI runs on every push to main.

Style: terse, basic comments. Avoid restating the obvious in docstrings.

```bash
git clone https://github.com/dzweben/RT-Analyses-Demo.git
cd RT-Analyses-Demo
pip install -e ".[dev]"
pytest
```
