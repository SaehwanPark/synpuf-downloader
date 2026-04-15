from __future__ import annotations

import logging

import pyarrow as pa

from synpuf_downloader.domain.conversion import (
  build_arrow_schema,
  build_conversion_jobs,
  derive_column_rules,
  group_csv_artifacts,
)
from synpuf_downloader.domain.models import (
  ConversionJob,
  ConversionResult,
  ConversionStatus,
  OutputLayout,
)
from synpuf_downloader.infrastructure.protocols import (
  EnsureLayout,
  InferSchema,
  InspectDataset,
  ListCsvPaths,
  ReadCsvHeader,
  ReadTable,
  RemovePath,
  WriteDataset,
)


def run_conversion(
  layout: OutputLayout,
  *,
  ensure_layout: EnsureLayout,
  list_csv_paths: ListCsvPaths,
  remove_path: RemovePath,
  read_csv_header: ReadCsvHeader,
  infer_schema: InferSchema,
  read_table: ReadTable,
  write_dataset: WriteDataset,
  inspect_dataset: InspectDataset,
  logger: logging.Logger,
) -> tuple[ConversionResult, ...]:
  ensure_layout(layout)
  grouped_artifacts = group_csv_artifacts(list_csv_paths(layout))
  jobs = build_conversion_jobs(grouped_artifacts)
  return tuple(
    _run_conversion_job(
      layout,
      job,
      remove_path=remove_path,
      read_csv_header=read_csv_header,
      infer_schema=infer_schema,
      read_table=read_table,
      write_dataset=write_dataset,
      inspect_dataset=inspect_dataset,
      logger=logger,
    )
    for job in jobs
  )


def _run_conversion_job(
  layout: OutputLayout,
  job: ConversionJob,
  *,
  remove_path: RemovePath,
  read_csv_header: ReadCsvHeader,
  infer_schema: InferSchema,
  read_table: ReadTable,
  write_dataset: WriteDataset,
  inspect_dataset: InspectDataset,
  logger: logging.Logger,
) -> ConversionResult:
  destination = layout.parquet_dir / job.output_name
  try:
    header = read_csv_header(job.artifacts[0].path)
    inferred_schema = infer_schema(job.artifacts[0].path)
    rules = derive_column_rules(header, inferred_schema)
    schema = build_arrow_schema(rules)
    tables = tuple(
      _append_sample_column(
        read_table(artifact.path, schema),
        artifact.sample_id.value,
      )
      for artifact in job.artifacts
    )
    combined_table = pa.concat_tables(list(tables)) if len(tables) > 1 else tables[0]
    remove_path(destination)
    write_dataset(combined_table, destination, job.max_rows_per_file)
    inspection = inspect_dataset(destination)
    logger.info('Wrote dataset %s', destination)
    return ConversionResult(
      dataset_kind=job.dataset_kind,
      status=ConversionStatus.WRITTEN,
      output_path=destination,
      row_count=inspection.row_count,
      partition_count=inspection.parquet_files,
      column_count=inspection.column_count,
    )
  except Exception as error:
    logger.exception('Failed to convert %s', job.dataset_kind.value)
    return ConversionResult(
      dataset_kind=job.dataset_kind,
      status=ConversionStatus.FAILED,
      output_path=destination,
      detail=str(error),
    )


def _append_sample_column(table: pa.Table, sample_id: int) -> pa.Table:
  sample_values = pa.array([sample_id] * len(table), type=pa.int32())
  return table.append_column('sample', sample_values)
