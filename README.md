# SynPUF Downloader

A reproducible local builder for the CMS DE-SynPUF dataset.

SynPUF Downloader downloads the official CMS synthetic public use files, extracts the source CSVs, and converts them into sample-partitioned Parquet datasets that are easier to query from Python, DuckDB, PyArrow, Spark, or an LLM-assisted analysis workflow.

## Why This Exists

CMS DE-SynPUF is useful for teaching, prototyping claims pipelines, testing cohort logic, and validating feature-engineering code. The raw distribution is less convenient: each sample is split across multiple ZIP archives, carrier claims arrive in two parts, filenames have historical quirks, and CSVs need careful typing so identifiers and medical codes are not corrupted.

This project turns that archive into a local, analysis-ready data lake while keeping the process explicit and reproducible.

## What It Does

- Downloads the 8 official source archives for each requested SynPUF sample.
- Extracts ZIP files into a consistent local layout.
- Converts extracted CSV files into partitioned Parquet datasets.
- Merges carrier claims part `A` and part `B` into one carrier claims dataset.
- Adds `sample` as a partition column so samples remain traceable after conversion.
- Preserves identifiers, ICD codes, HCPCS codes, NDC-like fields, NPIs, UPINs, and other code-like columns as strings.
- Writes logs for download and conversion runs.

## Requirements

- `uv`
- Python 3.13
- A writable directory for SynPUF outputs

The project currently targets Python 3.13. Broader Python support may be possible, but it has not been declared in `pyproject.toml` yet.

## Setup

```bash
uv sync
cp .env.example .env
```

Set `SYNPUF_DIR` in `.env` to the directory where SynPUF outputs should live:

```bash
SYNPUF_DIR=/path/to/synpuf
```

You can also skip `.env` and pass the directory with `--output-dir` or `--input-dir` at runtime.

## Quickstart

Validate that the expected CMS URLs are reachable:

```bash
uv run synpuf-downloader --samples 1 20 --validate
```

Download and extract a small subset:

```bash
uv run synpuf-downloader --samples 1 2 3
```

Convert the extracted CSVs to Parquet:

```bash
uv run synpuf-converter
```

Query the resulting Parquet dataset with DuckDB:

```sql
SELECT sample, COUNT(*) AS rows
FROM read_parquet('/path/to/synpuf/parquets/DE1_0_2008_Beneficiary_Summary_File.parquet/**/*.parquet')
GROUP BY sample
ORDER BY sample;
```

Or with PyArrow:

```python
import pyarrow.dataset as ds

beneficiaries = ds.dataset(
  '/path/to/synpuf/parquets/DE1_0_2008_Beneficiary_Summary_File.parquet',
  format='parquet',
  partitioning='hive',
)

print(beneficiaries.count_rows())
print(beneficiaries.schema)
```

## CLI Usage

Download selected samples:

```bash
uv run synpuf-downloader --samples 1 2 3
```

Download all 20 samples:

```bash
uv run synpuf-downloader --all
```

Validate URLs without downloading:

```bash
uv run synpuf-downloader --samples 1 20 --validate
```

Force re-download of existing archives:

```bash
uv run synpuf-downloader --samples 5 --force
```

Convert extracted CSV files to Parquet:

```bash
uv run synpuf-converter
```

Override the base directory at runtime:

```bash
uv run synpuf-downloader --all --output-dir /path/to/synpuf
uv run synpuf-converter --input-dir /path/to/synpuf
```

The repository also keeps thin compatibility wrappers at the project root:

```bash
uv run python downloader.py --samples 1 2 3
uv run python converter.py
```

## Output Layout

```text
${SYNPUF_DIR}/
  zip_files/   # downloaded CMS ZIP archives
  csv_files/   # extracted source CSV files
  parquets/    # converted Parquet dataset directories
  logs/        # downloader and converter logs
```

Each converted output under `parquets/` is a Parquet dataset directory, not a single file. The directory names end in `.parquet` to preserve the source dataset identity:

```text
${SYNPUF_DIR}/parquets/
  DE1_0_2008_Beneficiary_Summary_File.parquet/
    sample=1/
    sample=2/
    ...
  DE1_0_2008_to_2010_Carrier_Claims.parquet/
    sample=1/
    sample=2/
    ...
```

Expected converted datasets are:

| Dataset | Output directory |
| --- | --- |
| 2008 beneficiary summary | `DE1_0_2008_Beneficiary_Summary_File.parquet` |
| 2009 beneficiary summary | `DE1_0_2009_Beneficiary_Summary_File.parquet` |
| 2010 beneficiary summary | `DE1_0_2010_Beneficiary_Summary_File.parquet` |
| Inpatient claims | `DE1_0_2008_to_2010_Inpatient_Claims.parquet` |
| Outpatient claims | `DE1_0_2008_to_2010_Outpatient_Claims.parquet` |
| Prescription drug events | `DE1_0_2008_to_2010_Prescription_Drug_Events.parquet` |
| Carrier claims | `DE1_0_2008_to_2010_Carrier_Claims.parquet` |

## Verifying a Local Build

After conversion, inspect the output directories:

```bash
find "$SYNPUF_DIR/parquets" -maxdepth 2 -type d | sort
```

Check row counts with DuckDB:

```sql
SELECT COUNT(*) AS rows
FROM read_parquet('/path/to/synpuf/parquets/DE1_0_2008_Beneficiary_Summary_File.parquet/**/*.parquet');
```

Check available samples:

```sql
SELECT sample, COUNT(*) AS rows
FROM read_parquet('/path/to/synpuf/parquets/DE1_0_2008_Beneficiary_Summary_File.parquet/**/*.parquet')
GROUP BY sample
ORDER BY sample;
```

## Analysis Notes

- DE-SynPUF is synthetic Medicare claims data. It is useful for software development, methods prototyping, teaching, and workflow validation, but it should not be interpreted as real epidemiologic evidence.
- Beneficiary summary files are year-specific: 2008, 2009, and 2010.
- Claims and prescription drug event files cover 2008 to 2010.
- Carrier claims are distributed by CMS as two CSV parts per sample; this project combines those parts into one carrier claims Parquet dataset.
- Code-like columns are intentionally written as strings to avoid losing leading zeros or changing categorical semantics.

## Repository Guide

```text
src/synpuf_downloader/
  domain/          # pure planning, dataset naming, parsing, schema rules
  application/     # workflow orchestration
  infrastructure/  # filesystem, HTTP, and Arrow implementations
  cli/             # command-line entrypoints

tests/             # domain, application, infrastructure, and CLI tests
docs/              # codebook and user-manual references
skills/            # optional agent-facing SynPUF analysis guidance
prompts/           # historical development prompts
SPEC.md            # architecture and implementation specification
```

## Developer Workflow

`SPEC.md` is the source of truth for architecture and requirements.

Run the full quality gate before merging changes:

```bash
uv run ruff format .
uv run ruff check .
uv run mypy .
uv run pytest
```

Recommended implementation flow:

1. Start from `SPEC.md`.
2. Add or update tests first when behavior changes.
3. Keep domain functions pure where practical.
4. Keep infrastructure side effects behind protocols.
5. Run the quality gate before merging.

## Current Limitations

- Conversion currently materializes each output dataset from grouped CSV artifacts. Very large runs may benefit from a future streaming or incremental writer.
- Downloads rely on standard HTTP requests. Retry/backoff, checksums, and a persistent manifest would make long unattended runs more robust.
- ZIP extraction assumes trusted CMS archives. A stricter safe-extraction helper would be a useful hardening improvement.
- There is not yet a built-in `summary` or `inspect` command for reporting row counts and missing samples.

## Good Future Additions

- `synpuf-summary` command for local dataset validation.
- Download manifest with URL, filename, byte size, status, and timestamp.
- Retry/backoff controls for downloads.
- Incremental or streaming Parquet conversion.
- Example DuckDB and Python cohort-building notebooks or scripts.
- Broader Python version support if tests pass outside Python 3.13.

## License

See `LICENSE`.
