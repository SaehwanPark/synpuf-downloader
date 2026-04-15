# SynPUF Tools Specification

## Purpose
SynPUF Tools provides two stable CLIs for working with CMS DE-SynPUF data:
- `downloader.py` downloads and extracts the official ZIP archives into a reproducible local layout.
- `converter.py` converts extracted CSV artifacts into partitioned Parquet datasets grouped by SynPUF dataset kind.

This document is the source of truth for functional requirements, ubiquitous language, architecture, and quality expectations.

## Ubiquitous Language
- `Sample`: One of the 20 CMS DE-SynPUF samples, identified by integers `1..20`.
- `Source artifact`: A downloadable ZIP file for a single sample and file kind.
- `CSV artifact`: An extracted CSV file associated with one sample and one dataset kind.
- `Dataset kind`: A logical SynPUF dataset family such as `beneficiary_2008` or `carrier_claims`.
- `Carrier part`: The `A` or `B` suffix for carrier-claims CSV inputs. Output Parquet combines both parts.
- `Output layout`: The directory contract rooted at `SYNPUF_DIR` and containing `zip_files`, `csv_files`, `parquets`, and `logs`.

## Non-Negotiable Behaviors
- The public CLIs stay stable: `downloader.py` and `converter.py` remain directly executable.
- Existing flags stay supported.
- `SYNPUF_DIR` remains the primary environment variable.
- Download execution is sequential for deterministic logs and simpler failure handling.
- Converter outputs remain partitioned by `sample`.
- Carrier claims `A` and `B` inputs are merged into a single Parquet dataset.
- Domain models are Pydantic v2 with `frozen=True`.
- Domain and application logic are functional-first and side-effect free where possible.
- Infrastructure concerns are isolated behind `Protocol`s.

## Domain Model
- `SampleId`: Root model that only accepts integer values between 1 and 20.
- `FileKind`: `beneficiary_2008`, `beneficiary_2009`, `beneficiary_2010`, `carrier_claims`, `inpatient_claims`, `outpatient_claims`, `prescription_drug_events`.
- `DatasetKind`: `beneficiary_2008`, `beneficiary_2009`, `beneficiary_2010`, `carrier_claims`, `inpatient_claims`, `outpatient_claims`, `prescription_drug_events`.
- `CarrierPart`: `A` or `B`.
- `OutputLayout`: Absolute paths for the required directories under `SYNPUF_DIR`.
- `SourceArtifact`: Sample-specific download descriptor including URL, filename, and output destination.
- `CsvArtifact`: Parsed CSV descriptor including dataset kind, sample, and optional carrier part.
- `DownloadRequest`, `DownloadResult`, `DownloadSummary`: Models for planning and reporting download runs.
- `ConversionJob`, `ConversionResult`, `ConversionSummary`: Models for planning and reporting conversion runs.
- `ColumnSemantic` and `ColumnRule`: Models for schema policy, especially preservation of IDs and medical codes as strings.

## Architecture
- `src/synpuf_downloader/domain`: Pure domain models and pure planners/reducers.
- `src/synpuf_downloader/application`: Orchestration functions that translate domain plans into infrastructure calls.
- `src/synpuf_downloader/infrastructure`: Concrete adapters for HTTP, filesystem, ZIP extraction, and PyArrow I/O.
- `src/synpuf_downloader/cli`: Argument parsing, environment loading, logging setup, and user-facing reporting.
- Root scripts only delegate to CLI entrypoints.

## Download Requirements
- Build exactly 8 source artifacts per sample:
  - 3 beneficiary summary archives for 2008, 2009, and 2010
  - 2 carrier claims archives for parts `A` and `B`
  - 1 inpatient claims archive
  - 1 outpatient claims archive
  - 1 prescription drug events archive
- Preserve the currently known CMS edge cases:
  - Sample 1 uses an uppercase filename and a different path for the 2010 beneficiary archive.
  - Sample 20 uses alternate CMS path segments for the 2008 beneficiary archive and inpatient archive.
  - Sample 11 carrier part `A` archive has a `.csv.zip` filename.
- `--validate` performs availability checks without mutating downloaded datasets.
- `--force` disables skip-existing behavior.
- Invalid sample numbers fail at the CLI boundary before any work starts.

## Conversion Requirements
- Read input CSV files from `${SYNPUF_DIR}/csv_files`.
- Write output Parquet datasets to `${SYNPUF_DIR}/parquets`.
- Preserve dataset names currently exposed in the README and CLI output.
- Group CSV files by dataset kind and sample.
- Combine carrier claim part `A` and `B` inputs into the single `DE1_0_2008_to_2010_Carrier_Claims.parquet` dataset.
- Preserve nullable numeric types by using PyArrow-native schema handling.
- Preserve IDs and medical code columns as strings.
- Partition output datasets by `sample`.

## Quality Gates
- Python 3.13 and `uv` are required.
- `ruff format`, `ruff check`, `mypy`, and `pytest` must all pass before finalization.
- Tests must cover pure domain logic, CLI contracts, and integration behavior with fake infrastructure.
- GitHub Actions must execute the same quality gates on pushes and pull requests.

## Documentation Requirements
- `README.md` is a concise operator guide.
- `.env.example` documents the required environment variable.
- `prompts/` remain in the repo as historical references and are not treated as current executable specifications.
