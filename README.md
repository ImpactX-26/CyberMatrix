# LandShield synthetic investigation demo

This workspace contains a deterministic synthetic land-record dataset, five
normal control scenarios, five suspicious investigation scenarios, expected
ground truth, and a small rule-based evaluation tool. All people, parcels, and
records are fictional.

## Layout

- `data/synthetic/`: canonical JSON record sets and CSV exports, including a
  generated event stream.
- `data/scenarios/`: five normal and five suspicious case definitions.
- `data/ground_truth/`: expected findings in JSON and CSV.
- `tests/person4/`: standard-library unit tests for the data, scenarios, events,
  edge cases, and evaluation.
- `tools/`: event generation, demo reset/export, and evaluation scripts.

## Run

From this directory with Python 3.9 or newer:

```text
python tools/reset_demo.py
python tools/evaluate_person4.py
python -m unittest discover -s tests/person4 -v
```

The evaluator checks ownership mismatches, gaps between consecutive
registrations, parcel extent inconsistencies (with a 0.01-acre tolerance), and
active encumbrance totals greater than the property extent. The checks are
illustrative data-quality rules, not legal conclusions.
