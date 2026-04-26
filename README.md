# Analyst Report Data Sources Pipeline

Standalone research pipeline for preparing analyst report text, extracting cited alternative data sources with regex-based rules, and summarizing source usage from cleaned LSEG-style analyst report exports.

## Overview

This repository is intentionally regex-only. It takes cleaned analyst report text plus an alternative-source reference dictionary, prepares both inputs, runs deterministic source extraction, and writes final frequency summaries for downstream review.

The repo is organized as a small staged pipeline rather than a notebook workflow. Each stage writes explicit CSV outputs and a Markdown run log so intermediate artifacts stay inspectable and reproducible.

Future versions of the project may add an LLM-based source extraction stage, but the current repository does not include any LLM implementation, API dependency, or model-specific workflow.

## Purpose

The repository does three things:

1. Standardize the cleaned analyst report sample and reshape the alternative-source dictionary into a prepared lookup table.
2. Extract potential alternative data sources from report text using rule-based phrase matching plus explicit-reference matching against the prepared dictionary.
3. Generate regex-only frequency tables and summary metrics for downstream analysis.

## Key Definitions

- `Analyst Report`: a research note or report produced by a brokerage or research contributor about one or more companies, sectors, or themes.
- `LSEG-style Export`: a cleaned tabular export containing report metadata and extracted report text.
- `Alternative Data Source`: a nontraditional data source mentioned in report text, such as app data, card data, web traffic, or geolocation data.
- `Regex Extraction`: rule-based text extraction using deterministic phrase and pattern matching.

## Data Access Notes

The raw input data is not tracked in this repository. If you'd like to discuss the sample data structure, expected schema, or reproduction details, feel free to contact me.

## Pipeline Stages

### Stage 1: Prepare Input Data

This stage reads the cleaned analyst report sample and the alternative-source dictionary, removes scaffolding columns, standardizes whitespace, creates compact text previews, computes report word counts, and reshapes the alternative-source reference into a long lookup table.

Primary outputs:

- `output/exports/001_prepare_input_data/prepared_reports.csv`
- `output/exports/001_prepare_input_data/prepared_alternative_sources.csv`

### Stage 2: Regex Source Extraction

This stage scans report text for source-like phrases using a base-phrase pattern, splits those phrases into candidate source names, checks for explicit dictionary mentions in the report text, and matches candidate source names back to the prepared alternative-source dictionary.

Primary outputs:

- `output/exports/002_regex_source_extraction/regex_source_extraction_summary.csv`
- `output/exports/002_regex_source_extraction/regex_source_extraction_long.csv`

### Stage 3: Source Frequency Analysis

This stage aggregates the regex output into source-frequency tables, contributor-level source summaries, and a compact set of regex-stage metrics.

Primary outputs:

- `output/exports/003_source_frequency_analysis/regex_source_frequency.csv`
- `output/exports/003_source_frequency_analysis/contributor_source_frequency.csv`
- `output/exports/003_source_frequency_analysis/source_frequency_summary_metrics.csv`

## Repository Structure

```text
analyst-report-data-sources-pipeline/
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── pyproject.toml
├── scripts/
│   ├── 001_prepare_input_data.py
│   ├── 002_regex_source_extraction.py
│   ├── 003_source_frequency_analysis.py
│   ├── 00A_run_all.py
│   ├── check_env.py
│   ├── run_pipeline.py
│   └── setup_env.py
├── src/
│   ├── analysis/
│   │   ├── __init__.py
│   │   └── frequency_analysis.py
│   ├── extraction/
│   │   ├── __init__.py
│   │   └── regex_sources.py
│   ├── pipelines/
│   │   ├── __init__.py
│   │   ├── prepare_input_data.py
│   │   ├── regex_source_extraction.py
│   │   └── source_frequency_analysis.py
│   └── project/
│       ├── __init__.py
│       ├── config.py
│       ├── env.py
│       ├── io.py
│       ├── logger.py
│       ├── paths.py
│       ├── settings.py
│       ├── utils.py
│       └── validation.py
├── tests/
│   ├── conftest.py
│   ├── test_frequency_analysis.py
│   ├── test_prepare_input_data.py
│   ├── test_regex_source_extraction.py
│   └── test_validation.py
├── input/
│   ├── lseg_workspace_sample/
│   └── reference/
└── output/
    ├── exports/
    ├── figures/
    ├── logs/
    └── tables/
```

## Required Inputs

- A cleaned analyst report CSV at `RAW_REPORTS_PATH`
- An alternative-source dictionary CSV at `ALTERNATIVE_SOURCES_PATH`

These files are expected to be local inputs. Everything under `input/` and `output/` is gitignored, so if this repository is moved or cloned elsewhere you will need to place the input files back into the expected local paths or update `.env`.

Expected local raw layout:

```text
input/
├── lseg_workspace_sample/
│   └── sample_cleaned_lseg_reports.csv
└── reference/
    └── alternative_data_sources_sample.csv
```

## Input Data Examples

### Example Cleaned Analyst Report Rows

| Unnamed: 0 | DocumentID | Date | Year | Contributor | Report File Ticker | Partial Title | Pages | PDF File Name | Report Text |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `0` | `90000001` | `2021-11-02` | `2021` | `Example Research` | `ABCD.N` | `Global Retail Initiation` | `48` | `2021-11-02-ABCD.N-Example Research-Global Retail Initiation-90000001.pdf` | `Source: Demo Analytics. According to SamplePulse, mobile app downloads improved...` |
| `1` | `90000002` | `2021-11-03` | `2021` | `Sample Securities` | `WXYZ.O` | `Digital Payments Update` | `36` | `2021-11-03-WXYZ.O-Sample Securities-Digital Payments Update-90000002.pdf` | `Source: Example Data Labs. Bloomberg and Refinitiv estimates suggest...` |

### Example Alternative-Source Dictionary Rows

| List of Alternative Company Names \| ATT = 1 | List of Alternative Product Names \| ATT = 1 | List of Alternative Company Names \| 0 < ATT < 1 | List of Alternative Product Names \| 0 < ATT < 1 | List of Alternative Company Names \| ATT = 0 | List of Alternative Product Names \| ATT = 0 |
| --- | --- | --- | --- | --- | --- |
| `Demo Analytics` | `Mobile download panel` | `SamplePulse` | `Store traffic dataset` | `Example Data Labs` | `Payments trend tracker` |
| `Refinitiv` | `Cloud usage index` | `App Annie` | `Digital shelf monitor` | `SensorTower` | `Audience overlap model` |

## Setup

`setup_env.py` creates the expected local directories, creates a repo-local `.env` from the tracked `.env.example` template when `.env` is missing, and installs the packages listed in `requirements.txt` into the current interpreter or the local `.venv` if one exists.

```bash
python3 scripts/setup_env.py
python3 scripts/check_env.py
```

The setup script will create a repo-local `.env` from `.env.example` on first run. The tracked template contains this sample configuration:

```bash
RAW_REPORTS_PATH=input/lseg_workspace_sample/sample_cleaned_lseg_reports.csv
ALTERNATIVE_SOURCES_PATH=input/reference/alternative_data_sources_sample.csv
REGEX_SIMILARITY_THRESHOLD=0.88
MAX_REPORTS=15
RUNTIME_MODE=local
```

## Run

Run all stages:

```bash
python3 scripts/run_pipeline.py --all
```

Run one stage:

```bash
python3 scripts/run_pipeline.py --stage 002_regex_source_extraction
```

## Outputs

The repository writes two kinds of outputs:

- Stage logs in `output/logs/`
- Stage exports in `output/exports/`

Expected output structure:

```text
output/
├── exports/
│   ├── 001_prepare_input_data/
│   │   ├── prepared_alternative_sources.csv
│   │   └── prepared_reports.csv
│   ├── 002_regex_source_extraction/
│   │   ├── regex_source_extraction_long.csv
│   │   └── regex_source_extraction_summary.csv
│   └── 003_source_frequency_analysis/
│       ├── contributor_source_frequency.csv
│       ├── regex_source_frequency.csv
│       └── source_frequency_summary_metrics.csv
└── logs/
    ├── 001_prepare_input_data.md
    ├── 002_regex_source_extraction.md
    └── 003_source_frequency_analysis.md
```

### Example Output Rows

Stage 1 prepared reports output should look like this:

| DocumentID | Date | Year | Contributor | Report File Ticker | Partial Title | Pages | PDF File Name | Report Text | Report Text Cleaned | Report Text Preview | Report Word Count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `90000001` | `2021-11-02` | `2021` | `Example Research` | `ABCD.N` | `Global Retail Initiation` | `48` | `2021-11-02-ABCD.N-Example Research-Global Retail Initiation-90000001.pdf` | `Source: Demo Analytics. According to SamplePulse...` | `Source: Demo Analytics. According to SamplePulse...` | `Source: Demo Analytics. According to SamplePulse...` | `3120` |

Stage 1 prepared alternative sources output should look like this:

| source_name | source_name_normalized | source_group | attention_tier |
| --- | --- | --- | --- |
| `Demo Analytics` | `Demo Analytics` | `alternative_company_name` | `ATT = 1` |
| `Mobile download panel` | `Mobile download panel` | `alternative_product_name` | `ATT = 1` |

Stage 2 regex summary output should look like this:

| DocumentID | Year | Date | Contributor | Report File Ticker | Partial Title | Pages | PDF File Name | Potential Source Phrases | Regex Candidate Sources | Explicit Mentioned Sources | Matched Alternative Sources | Matched Source Count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `90000001` | `2021` | `2021-11-02` | `Example Research` | `ABCD.N` | `Global Retail Initiation` | `48` | `2021-11-02-ABCD.N-Example Research-Global Retail Initiation-90000001.pdf` | `Demo Analytics \| SamplePulse` | `Demo Analytics \| SamplePulse` | `Demo Analytics` | `Demo Analytics \| SamplePulse` | `2` |

Stage 2 regex long output should look like this:

| DocumentID | Year | Date | Contributor | Report File Ticker | PDF File Name | Source Name | Source Name Normalized | Source Origin | Source Group | Attention Tier | Match Score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `90000001` | `2021` | `2021-11-02` | `Example Research` | `ABCD.N` | `2021-11-02-ABCD.N-Example Research-Global Retail Initiation-90000001.pdf` | `Demo Analytics` | `Demo Analytics` | `explicit_mention` | `alternative_company_name` | `ATT = 1` | `1.0` |

Stage 3 regex frequency output should look like this:

| Source Name | Frequency |
| --- | --- |
| `Demo Analytics` | `4` |
| `SamplePulse` | `3` |

Stage 3 summary metrics output should look like this:

| section | metric | value | notes |
| --- | --- | --- | --- |
| `regex_stage` | `row_count` | `36` | `Total regex long-output rows.` |
| `regex_stage` | `unique_sources` | `11` | `Unique sources identified by the regex stage.` |
| `regex_stage` | `matched_documents` | `9` | `Unique reports with at least one extracted source.` |

## Data Management

- Everything under `input/` and `output/` is gitignored.
- You should place the local input files for this repo inside `input/` or point the `.env` paths to an external location on your machine.
- At minimum, `input/` needs:
  - A cleaned analyst report CSV with the exact columns shown above
  - An alternative-source dictionary CSV with the exact columns shown above
- The repository code, tests, and configuration are meant to be versioned; the raw inputs and generated outputs are not.

## Limitations

- The repository is path-configured through `.env`, so reproducibility still depends on the local input layout being restored correctly.
- The current extraction logic is entirely regex-based and deterministic, so it may miss sources that are implied rather than explicitly phrased in source-like language.
- The included tests cover core preparation, regex extraction, validation, and frequency-analysis helpers.
- The current test suite is unit-level rather than fully end-to-end: it checks core transformation logic in isolation, but it does not yet serve as a full integration test of every written output.

## Future Work

- A future version of this project may add an LLM-based source extraction implementation behind a separate stage or optional mode.
- That work is intentionally out of scope for the current repository so the codebase stays small, reproducible, and easy to reason about.
