from __future__ import annotations

from pathlib import Path

import pyarrow as pa
import pyarrow.csv as pv
import pyarrow.dataset as ds

from synpuf_downloader.domain.models import DatasetInspection

NULL_VALUES = ['', 'NULL', 'null', 'NA', 'na', 'N/A']
TRUE_VALUES = ['true', 'True', 'TRUE', '1', 'yes', 'Yes', 'YES']
FALSE_VALUES = ['false', 'False', 'FALSE', '0', 'no', 'No', 'NO']


def read_csv_header(csv_path: Path) -> tuple[str, ...]:
  with csv_path.open('r', encoding='utf-8') as input_handle:
    first_line = input_handle.readline().strip()
  return tuple(segment.strip().strip('"') for segment in first_line.split(','))


def infer_schema(csv_path: Path) -> pa.Schema:
  table = pv.read_csv(
    csv_path,
    read_options=pv.ReadOptions(block_size=2 * 1024 * 1024),
    parse_options=_parse_options(),
    convert_options=pv.ConvertOptions(
      strings_can_be_null=True,
      include_missing_columns=True,
      auto_dict_encode=False,
    ),
  )
  header = read_csv_header(csv_path)
  return pa.schema([table.schema.field(column_name) for column_name in header])


def read_table(csv_path: Path, schema: pa.Schema) -> pa.Table:
  return pv.read_csv(
    csv_path,
    read_options=pv.ReadOptions(block_size=64 * 1024 * 1024),
    parse_options=_parse_options(),
    convert_options=pv.ConvertOptions(
      column_types=schema,
      strings_can_be_null=True,
      include_missing_columns=True,
      auto_dict_encode=False,
      null_values=NULL_VALUES,
      true_values=TRUE_VALUES,
      false_values=FALSE_VALUES,
    ),
  )


def write_partitioned_dataset(
  table: pa.Table,
  destination: Path,
  max_rows_per_file: int,
) -> None:
  destination.parent.mkdir(parents=True, exist_ok=True)
  parquet_format = ds.ParquetFileFormat()
  file_options = parquet_format.make_write_options(
    compression='snappy',
    use_dictionary=True,
    write_statistics=True,
  )
  ds.write_dataset(
    data=table,
    base_dir=destination,
    format=parquet_format,
    partitioning=['sample'],
    file_options=file_options,
    existing_data_behavior='overwrite_or_ignore',
    max_open_files=1000,
    max_rows_per_file=max_rows_per_file,
  )


def inspect_dataset(destination: Path) -> DatasetInspection:
  dataset = ds.dataset(destination, format='parquet', partitioning='hive')
  files = tuple(
    sorted(_resolve_dataset_path(destination, file_name) for file_name in dataset.files)
  )
  return DatasetInspection(
    dataset_path=destination,
    parquet_files=len(files),
    row_count=dataset.count_rows(),
    column_count=len(dataset.schema),
    size_bytes=sum(path.stat().st_size for path in files if path.exists()),
  )


def _parse_options() -> pv.ParseOptions:
  return pv.ParseOptions(
    delimiter=',',
    quote_char='"',
    escape_char='\\',
    newlines_in_values=False,
    ignore_empty_lines=True,
  )


def _resolve_dataset_path(base_dir: Path, file_name: str) -> Path:
  resolved = Path(file_name)
  return resolved if resolved.is_absolute() else base_dir / file_name
