# Rune OCR Analyzer

A tool I built to automate rune evaluation in Summoners War, a mobile RPG where farming generates hundreds of items per session that each need to be manually assessed.

## What it does

The game shows rune stats on screen. This tool reads them automatically via OCR, scores each rune, and decides in real time whether to keep it, sell it, or upgrade it further before deciding. Every decision is logged, and a separate analysis script generates charts to review patterns over time.

## Why I built it

Evaluating a rune manually means reading 4 to 8 stats, computing a weighted score, and comparing it against thresholds that depend on the rune type and how useful the set is. Doing this hundreds of times per session is tedious and inconsistent. I wanted something that could make the same decision I would, reliably and instantly.

## How it works

**Screen capture and OCR** — The tool takes a screenshot of the rune panel, crops the relevant regions, and runs Tesseract OCR to extract the text. A normalization layer corrects frequent misreads specific to the game font before parsing.

**Scoring** — Each rune is scored using the community efficiency formula, which weights each sub-stat relative to its theoretical maximum. Two profiles are computed (DPS and support) and the better one is kept. The number of relevant sub-stats (called the bucket) determines which threshold applies.

**Threshold calibration** — To set fair thresholds across different bucket sizes, I ran a Monte Carlo simulation (400,000 samples) of the efficiency distribution for each profile and bucket combination. This lets me find thresholds that represent equivalent difficulty regardless of how many good sub-stats a rune has.

**Decision** — A rune is kept if any single sub-stat exceeds a "big proc" threshold (an exceptional single roll), or if its efficiency score meets the minimum for its bucket. Otherwise it is sold, unless it has not yet reached its maximum upgrade level, in which case it is flagged to upgrade further and re-evaluate.

**Logging** — Each decision is written to a JSONL file with the full rune details, the computed scores, and the reason for the decision.

**Analysis** — A separate script reads the logs and produces 16 charts: keep rates by set, slot, and rarity; margin distributions; efficiency scatter plots; heatmaps; volume over time; and tables of the best and borderline runes.

## Running the analysis

The analysis script works standalone — no game required, just the log files.

```bash
pip install -r requirements.txt

python rune_analysis.py              # all logged runes
python rune_analysis.py --today      # today only
python rune_analysis.py --date 2026-05-20
python rune_analysis.py --save report.pdf
```

Use the left/right arrow keys to navigate between charts and up/down to scroll through tables.

## Project structure

```
src/up_runes.py       decision engine and OCR text parser
src/eff_equiv.py      Monte Carlo threshold calibration
src/runes.py          screen capture loop (requires the game running)
src/flask_app.py      web UI to adjust thresholds without editing code
src/debug_runes.py    OCR diagnostic tool
rune_analysis.py      analysis dashboard
data/                 logged rune decisions (JSONL)
templates/            Flask UI template
```

## Tech stack

Python, OpenCV, Tesseract OCR, NumPy, pandas, matplotlib, Flask.
