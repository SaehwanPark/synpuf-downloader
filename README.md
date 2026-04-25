# SynPUF Downloader

Functional, type-first tooling for downloading CMS DE-SynPUF archives and converting extracted CSV files into partitioned Parquet datasets.

## What It Does
- `downloader.py` downloads and extracts the 8 source archives for each requested SynPUF sample.
- `converter.py` groups extracted CSV files by dataset kind and writes sample-partitioned Parquet datasets.
- Carrier claims part `A` and `B` CSV files are merged into a single Parquet dataset.

## Requirements
- `uv`
- Python 3.13
- A writable directory exposed through `SYNPUF_DIR`

## Setup
```bash
uv sync
cp .env.example .env
```

Set `SYNPUF_DIR` in `.env` to the directory where SynPUF outputs should live.

## Usage

Download selected samples:
```bash
uv run python downloader.py --samples 1 2 3
```

Download all samples:
```bash
uv run python downloader.py --all
```

Validate URLs without downloading:
```bash
uv run python downloader.py --samples 1 20 --validate
```

Convert extracted CSV files to Parquet:
```bash
uv run python converter.py
```

Override the base directory at runtime:
```bash
uv run python converter.py --input-dir /path/to/synpuf
uv run python downloader.py --all --output-dir /path/to/synpuf
```

## Output Layout
```text
${SYNPUF_DIR}/
  zip_files/
  csv_files/
  parquets/
  logs/
```

## Developer Workflow
- `SPEC.md` is the source of truth for architecture and requirements.
- Use a `temp/` branch for implementation work.
- Follow Red-Green-Refactor with checkpoint commits.
- Run the full quality gate before merging:

```bash
uv run ruff format .
uv run ruff check .
uv run mypy .
uv run pytest
```

## Notes
- IDs and medical code fields are preserved as strings in Parquet output.
- Nullable numeric columns are handled through PyArrow-native schema inference and overrides.
- `prompts/` remains in the repository as historical context and is not the active implementation spec.
