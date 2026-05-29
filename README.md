# AI Product Feedback Prioritizer

Entry-level AI product project inspired by product-intern work: turn messy user feedback into a prioritized roadmap.

## What it does

- Reads feedback from CSV.
- Scores sentiment with a lightweight keyword model.
- Groups similar requests using token overlap.
- Ranks themes by frequency, urgency, and customer impact.
- Exports a Markdown roadmap summary.

## Quick start

```bash
python3 -m src.cli data/sample_feedback.csv --top 5
```

## Example use case

An AI product intern can use this to summarize beta-user feedback after a pilot launch and identify which product improvements should be discussed first.

## Tests

```bash
PYTHONPATH=. pytest -q
```

