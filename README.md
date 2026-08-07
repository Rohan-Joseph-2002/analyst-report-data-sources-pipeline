# Analyst Report Data Sources Pipeline

Standalone, regex-only pipeline that prepares cleaned analyst-report text, extracts the
alternative data sources those reports cite, and summarizes how often each source is used.

## Overview

Knowing which alternative datasets (app, transaction, web, and similar signals) analysts lean
on reveals where the market's attention is concentrated. This pipeline turns free-text reports
into a structured, countable record of cited sources — deterministically and without any LLM.

## Quickstart

```bash
python setup_env.py                 # create .venv, install deps, write .env from .env.example
source .venv/bin/activate
python run_all.py                   # run the data/ then analysis/ stages in order
pytest                              # run the tests
```

The repo ships small **synthetic** sample inputs under `input/`, so everything above works with
no external data. Real inputs are gitignored.

## Stages

Run in order by `run_all.py`; each writes a Markdown log to `logs/`.

| Script | Does | Writes to |
|--------|------|-----------|
| `data/d001_prepare_input_data.py` | Clean the report sample; reshape the wide alternative-source dictionary into a long lookup | `output/data-output/` |
| `data/d002_regex_source_extraction.py` | Extract source phrases, then match them to the dictionary via explicit-mention + fuzzy passes | `output/data-output/` |
| `analysis/a001_source_frequency_analysis.py` | Build source-frequency, contributor-frequency, and summary-metric tables | `output/analysis-output/` |

## Layout

```text
src/          shared code: settings (config + paths), io, logger, utils, validation
data/         d001, d002 data-processing scripts
analysis/     a001 analysis script
input/        committed synthetic samples (real data gitignored)
output/       data-output/ and analysis-output/ (gitignored)
logs/         one <script>.md per run
tests/        pytest
```

## Data & reproducibility

- Inputs: a cleaned report table (`REPORT_REQUIRED_COLUMNS` in `src/settings.py`) and a wide
  alternative-source dictionary. Point `.env` at your own files to run on real data.
- Deterministic: matching uses word-boundary exact mentions plus a `difflib` similarity
  threshold (`REGEX_SIMILARITY_THRESHOLD`, default 0.88). No network, no models.

## Testing

```bash
pytest
```

## License

Apache-2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
