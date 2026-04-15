from __future__ import annotations

from enum import StrEnum
from pathlib import Path

import pyarrow as pa
from pydantic import BaseModel, ConfigDict, RootModel, field_validator


class FrozenModel(BaseModel):
  model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)


class SampleId(RootModel[int]):
  model_config = ConfigDict(frozen=True)

  @field_validator('root')
  @classmethod
  def validate_range(cls, value: int) -> int:
    if not 1 <= value <= 20:
      raise ValueError('sample id must be between 1 and 20')
    return value

  @property
  def value(self) -> int:
    return self.root

  def __int__(self) -> int:
    return self.root

  def __str__(self) -> str:
    return str(self.root)


class FileKind(StrEnum):
  BENEFICIARY_2008 = 'beneficiary_2008'
  BENEFICIARY_2009 = 'beneficiary_2009'
  BENEFICIARY_2010 = 'beneficiary_2010'
  CARRIER_CLAIMS = 'carrier_claims'
  INPATIENT_CLAIMS = 'inpatient_claims'
  OUTPATIENT_CLAIMS = 'outpatient_claims'
  PRESCRIPTION_DRUG_EVENTS = 'prescription_drug_events'


class DatasetKind(StrEnum):
  BENEFICIARY_2008 = 'beneficiary_2008'
  BENEFICIARY_2009 = 'beneficiary_2009'
  BENEFICIARY_2010 = 'beneficiary_2010'
  CARRIER_CLAIMS = 'carrier_claims'
  INPATIENT_CLAIMS = 'inpatient_claims'
  OUTPATIENT_CLAIMS = 'outpatient_claims'
  PRESCRIPTION_DRUG_EVENTS = 'prescription_drug_events'


class CarrierPart(StrEnum):
  A = 'A'
  B = 'B'


class DownloadStatus(StrEnum):
  VALIDATED = 'validated'
  SKIPPED = 'skipped'
  EXTRACTED = 'extracted'
  DOWNLOAD_FAILED = 'download_failed'
  EXTRACT_FAILED = 'extract_failed'


class ConversionStatus(StrEnum):
  WRITTEN = 'written'
  FAILED = 'failed'
  SKIPPED = 'skipped'


class ColumnSemantic(StrEnum):
  STRING_CODE = 'string_code'
  INTEGER = 'integer'
  FLOAT = 'float'
  BOOLEAN = 'boolean'
  DATE = 'date'
  TIMESTAMP = 'timestamp'
  TEXT = 'text'


class OutputLayout(FrozenModel):
  base_dir: Path
  zip_dir: Path
  csv_dir: Path
  parquet_dir: Path
  log_dir: Path

  @classmethod
  def from_base_dir(cls, base_dir: Path) -> OutputLayout:
    return cls(
      base_dir=base_dir,
      zip_dir=base_dir / 'zip_files',
      csv_dir=base_dir / 'csv_files',
      parquet_dir=base_dir / 'parquets',
      log_dir=base_dir / 'logs',
    )


class SourceArtifact(FrozenModel):
  sample_id: SampleId
  file_kind: FileKind
  dataset_kind: DatasetKind
  filename: str
  url: str
  carrier_part: CarrierPart | None = None


class CsvArtifact(FrozenModel):
  path: Path
  sample_id: SampleId
  dataset_kind: DatasetKind
  carrier_part: CarrierPart | None = None


class DownloadRequest(FrozenModel):
  output_layout: OutputLayout
  samples: tuple[SampleId, ...]
  validate_only: bool = False
  skip_existing: bool = True


class DownloadResult(FrozenModel):
  artifact: SourceArtifact
  status: DownloadStatus
  detail: str = ''
  bytes_downloaded: int = 0
  extracted_files: tuple[str, ...] = ()


class DownloadSummary(FrozenModel):
  total_files: int
  skipped_files: int
  attempted_files: int
  successful_downloads: int
  failed_downloads: int
  successful_extractions: int
  failed_extractions: int
  validated_files: int
  failed_validations: int
  results: tuple[DownloadResult, ...]


class ConversionJob(FrozenModel):
  dataset_kind: DatasetKind
  output_name: str
  artifacts: tuple[CsvArtifact, ...]
  max_rows_per_file: int


class ConversionResult(FrozenModel):
  dataset_kind: DatasetKind
  status: ConversionStatus
  output_path: Path | None = None
  row_count: int = 0
  partition_count: int = 0
  column_count: int = 0
  detail: str = ''


class ConversionSummary(FrozenModel):
  successful_datasets: int
  failed_datasets: int
  skipped_datasets: int
  results: tuple[ConversionResult, ...]


class ColumnRule(FrozenModel):
  name: str
  semantic: ColumnSemantic
  arrow_type: pa.DataType
  nullable: bool = True


class DatasetInspection(FrozenModel):
  dataset_path: Path
  parquet_files: int
  row_count: int
  column_count: int
  size_bytes: int
