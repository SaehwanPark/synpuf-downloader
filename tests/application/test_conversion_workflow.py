from __future__ import annotations

import logging
from pathlib import Path

from synpuf_downloader.application.conversion import run_conversion
from synpuf_downloader.domain import ConversionStatus, DatasetKind, OutputLayout
from synpuf_downloader.infrastructure.arrow_io import (
  infer_schema,
  inspect_dataset,
  read_csv_header,
  read_table,
  write_partitioned_dataset,
)
from synpuf_downloader.infrastructure.filesystem import ensure_layout, list_csv_paths, remove_path


def test_run_conversion_writes_partitioned_outputs(tmp_path: Path) -> None:
  layout = OutputLayout.from_base_dir(tmp_path)
  ensure_layout(layout)
  _write_csv(
    layout.csv_dir / 'DE1_0_2008_Beneficiary_Summary_File_Sample_1.csv',
    'BENE_ID,CLAIM_COUNT\n0001,2\n',
  )
  _write_csv(
    layout.csv_dir / 'DE1_0_2008_to_2010_Carrier_Claims_Sample_1A.csv',
    'BENE_ID,CLM_ID,TOTAL_PMT\n0001,100,10.5\n',
  )
  _write_csv(
    layout.csv_dir / 'DE1_0_2008_to_2010_Carrier_Claims_Sample_1B.csv',
    'BENE_ID,CLM_ID,TOTAL_PMT\n0002,101,20.5\n',
  )

  results = run_conversion(
    layout,
    ensure_layout=ensure_layout,
    list_csv_paths=list_csv_paths,
    remove_path=remove_path,
    read_csv_header=read_csv_header,
    infer_schema=infer_schema,
    read_table=read_table,
    write_dataset=write_partitioned_dataset,
    inspect_dataset=inspect_dataset,
    logger=logging.getLogger('test.convert'),
  )

  carrier_result = next(
    result for result in results if result.dataset_kind == DatasetKind.CARRIER_CLAIMS
  )
  beneficiary_result = next(
    result for result in results if result.dataset_kind == DatasetKind.BENEFICIARY_2008
  )

  assert all(result.status == ConversionStatus.WRITTEN for result in results)
  assert beneficiary_result.row_count == 1
  assert carrier_result.row_count == 2
  assert (layout.parquet_dir / 'DE1_0_2008_Beneficiary_Summary_File.parquet').exists()
  assert (layout.parquet_dir / 'DE1_0_2008_to_2010_Carrier_Claims.parquet').exists()


def test_run_conversion_handles_missing_carrier_half_files(tmp_path: Path) -> None:
  layout = OutputLayout.from_base_dir(tmp_path)
  ensure_layout(layout)
  _write_csv(
    layout.csv_dir / 'DE1_0_2008_to_2010_Carrier_Claims_Sample_1A.csv',
    'BENE_ID,CLM_ID,TOTAL_PMT\n0001,100,10.5\n',
  )

  results = run_conversion(
    layout,
    ensure_layout=ensure_layout,
    list_csv_paths=list_csv_paths,
    remove_path=remove_path,
    read_csv_header=read_csv_header,
    infer_schema=infer_schema,
    read_table=read_table,
    write_dataset=write_partitioned_dataset,
    inspect_dataset=inspect_dataset,
    logger=logging.getLogger('test.convert.missing-half'),
  )

  assert len(results) == 1
  assert results[0].row_count == 1


def test_run_conversion_returns_empty_tuple_for_empty_input(tmp_path: Path) -> None:
  layout = OutputLayout.from_base_dir(tmp_path)

  results = run_conversion(
    layout,
    ensure_layout=ensure_layout,
    list_csv_paths=list_csv_paths,
    remove_path=remove_path,
    read_csv_header=read_csv_header,
    infer_schema=infer_schema,
    read_table=read_table,
    write_dataset=write_partitioned_dataset,
    inspect_dataset=inspect_dataset,
    logger=logging.getLogger('test.convert.empty'),
  )

  assert results == ()


def _write_csv(path: Path, contents: str) -> None:
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(contents, encoding='utf-8')
