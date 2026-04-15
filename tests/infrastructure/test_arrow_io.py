from __future__ import annotations

from pathlib import Path

import pyarrow as pa

from synpuf_downloader.infrastructure.arrow_io import inspect_dataset, write_partitioned_dataset


def test_write_partitioned_dataset_supports_small_max_rows_per_file(tmp_path: Path) -> None:
  destination = tmp_path / 'dataset.parquet'
  table = pa.table(
    {
      'BENE_ID': ['0001', '0002'],
      'CLAIM_COUNT': [2, 3],
      'sample': pa.array([1, 2], type=pa.int32()),
    }
  )

  write_partitioned_dataset(table, destination, max_rows_per_file=1000)
  inspection = inspect_dataset(destination)

  assert inspection.row_count == 2
  assert inspection.column_count == 2
  assert inspection.parquet_files == 2
