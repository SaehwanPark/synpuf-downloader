from __future__ import annotations

import logging
import os
from datetime import datetime
from pathlib import Path

from synpuf_downloader.domain.models import (
  ConversionSummary,
  DownloadResult,
  DownloadStatus,
  DownloadSummary,
  OutputLayout,
  SampleId,
)


def resolve_layout(base_dir_text: str | None) -> OutputLayout:
  if base_dir_text is None:
    raise ValueError('directory must be specified via CLI argument or SYNPUF_DIR')
  return OutputLayout.from_base_dir(Path(base_dir_text).expanduser().resolve())


def parse_samples(sample_values: list[int] | None, all_requested: bool) -> tuple[SampleId, ...]:
  if all_requested:
    return tuple(SampleId(value) for value in range(1, 21))
  if sample_values is None:
    raise ValueError('must specify either --samples or --all')
  ordered_values = tuple(dict.fromkeys(sample_values))
  return tuple(SampleId(value) for value in ordered_values)


def configure_logging(
  command_name: str,
  layout: OutputLayout,
  log_level: str,
) -> tuple[logging.Logger, Path]:
  layout.log_dir.mkdir(parents=True, exist_ok=True)
  logger = logging.getLogger(f'synpuf.{command_name}')
  logger.handlers.clear()
  logger.propagate = False
  logger.setLevel(getattr(logging, log_level.upper()))
  formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
  console_handler = logging.StreamHandler()
  console_handler.setFormatter(formatter)
  file_name = layout.log_dir / f'synpuf_{command_name}_{datetime.now():%Y%m%d_%H%M%S}.log'
  file_handler = logging.FileHandler(file_name)
  file_handler.setFormatter(formatter)
  logger.addHandler(console_handler)
  logger.addHandler(file_handler)
  return logger, file_name


def format_download_summary(
  summary: DownloadSummary,
  log_file: Path,
  validate_only: bool,
) -> str:
  heading = 'VALIDATION SUMMARY' if validate_only else 'DOWNLOAD SUMMARY'
  lines = [
    '',
    '=' * 50,
    heading,
    '=' * 50,
    f'Total files expected:      {summary.total_files}',
    f'Files skipped (existing):  {summary.skipped_files}',
    f'Files attempted:           {summary.attempted_files}',
    f'Successful downloads:      {summary.successful_downloads}',
    f'Failed downloads:          {summary.failed_downloads}',
    f'Successful extractions:    {summary.successful_extractions}',
    f'Failed extractions:        {summary.failed_extractions}',
    f'Validated files:          {summary.validated_files}',
    f'Log file:                 {log_file}',
    '=' * 50,
  ]
  return '\n'.join(lines)


def format_download_failures(results: tuple[DownloadResult, ...]) -> str:
  failures = tuple(
    result
    for result in results
    if result.status in {DownloadStatus.DOWNLOAD_FAILED, DownloadStatus.EXTRACT_FAILED}
  )
  if not failures:
    return ''
  lines = ['', '=' * 60, 'DETAILED FAILURE REPORT', '=' * 60]
  lines.extend(
    (
      f'Sample {result.artifact.sample_id.value}: '
      f'{result.artifact.filename} [{result.status.value}] {result.detail}'
    )
    for result in failures
  )
  lines.append('=' * 60)
  return '\n'.join(lines)


def format_conversion_summary(summary: ConversionSummary, log_file: Path) -> str:
  lines = ['', '=' * 50, 'CONVERSION SUMMARY', '=' * 50]
  if not summary.results:
    lines.append('No CSV artifacts were found to convert.')
  else:
    for result in summary.results:
      lines.extend(
        [
          f'{result.dataset_kind.value}:',
          f'  status={result.status.value}',
          f'  rows={result.row_count}',
          f'  parquet_files={result.partition_count}',
          f'  columns={result.column_count}',
          f'  output={result.output_path}' if result.output_path is not None else '  output=<none>',
          f'  detail={result.detail}' if result.detail else '  detail=',
        ]
      )
  lines.extend(
    [
      f'Written datasets: {summary.successful_datasets}',
      f'Failed datasets:  {summary.failed_datasets}',
      f'Skipped datasets: {summary.skipped_datasets}',
      f'Log file:         {log_file}',
      '=' * 50,
    ]
  )
  return '\n'.join(lines)


def require_env_path(cli_value: str | None) -> str | None:
  return cli_value or os.getenv('SYNPUF_DIR')
