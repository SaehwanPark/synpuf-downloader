from __future__ import annotations

from pathlib import Path

import pyarrow as pa

from synpuf_downloader.domain import (
  CarrierPart,
  ColumnSemantic,
  ConversionResult,
  ConversionStatus,
  DatasetKind,
  build_conversion_jobs,
  dataset_output_name,
  derive_column_rules,
  group_csv_artifacts,
  summarize_conversions,
)


def test_group_csv_artifacts_parses_known_filenames(tmp_path: Path) -> None:
  grouped = group_csv_artifacts(
    (
      tmp_path / 'DE1_0_2008_Beneficiary_Summary_File_Sample_1.csv',
      tmp_path / 'DE1_0_2008_to_2010_Carrier_Claims_Sample_1A.csv',
      tmp_path / 'DE1_0_2008_to_2010_Carrier_Claims_Sample_1B.csv',
      tmp_path / 'ignored.csv',
    )
  )

  assert DatasetKind.BENEFICIARY_2008 in grouped
  assert DatasetKind.CARRIER_CLAIMS in grouped
  assert [artifact.carrier_part for artifact in grouped[DatasetKind.CARRIER_CLAIMS]] == [
    CarrierPart.A,
    CarrierPart.B,
  ]


def test_derive_column_rules_preserves_ids_and_nullable_numbers() -> None:
  schema = pa.schema(
    [
      pa.field('BENE_ID', pa.int64(), nullable=True),
      pa.field('CLAIM_COUNT', pa.int32(), nullable=True),
      pa.field('TOTAL_PMT', pa.float64(), nullable=True),
    ]
  )
  rules = derive_column_rules(('BENE_ID', 'CLAIM_COUNT', 'TOTAL_PMT'), schema)

  assert rules[0].semantic == ColumnSemantic.STRING_CODE
  assert rules[0].arrow_type == pa.string()
  assert rules[1].semantic == ColumnSemantic.INTEGER
  assert rules[1].arrow_type == pa.int64()
  assert rules[2].semantic == ColumnSemantic.FLOAT


def test_build_conversion_jobs_uses_stable_output_names_and_row_limits(tmp_path: Path) -> None:
  grouped = group_csv_artifacts(
    (
      tmp_path / 'DE1_0_2008_Beneficiary_Summary_File_Sample_1.csv',
      tmp_path / 'DE1_0_2008_to_2010_Carrier_Claims_Sample_1A.csv',
    )
  )

  jobs = build_conversion_jobs(grouped)

  assert jobs[0].output_name == dataset_output_name(DatasetKind.BENEFICIARY_2008)
  carrier_job = next(job for job in jobs if job.dataset_kind == DatasetKind.CARRIER_CLAIMS)
  assert carrier_job.max_rows_per_file == 2_000_000


def test_summarize_conversions_counts_statuses() -> None:
  summary = summarize_conversions(
    (
      ConversionResult(dataset_kind=DatasetKind.BENEFICIARY_2008, status=ConversionStatus.WRITTEN),
      ConversionResult(dataset_kind=DatasetKind.BENEFICIARY_2009, status=ConversionStatus.FAILED),
      ConversionResult(dataset_kind=DatasetKind.BENEFICIARY_2010, status=ConversionStatus.SKIPPED),
    )
  )

  assert summary.successful_datasets == 1
  assert summary.failed_datasets == 1
  assert summary.skipped_datasets == 1
