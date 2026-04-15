from __future__ import annotations

import argparse

from dotenv import load_dotenv

from synpuf_downloader.application.conversion import run_conversion
from synpuf_downloader.cli.common import (
  configure_logging,
  format_conversion_summary,
  require_env_path,
  resolve_layout,
)
from synpuf_downloader.domain import summarize_conversions
from synpuf_downloader.infrastructure.arrow_io import (
  infer_schema,
  inspect_dataset,
  read_csv_header,
  read_table,
  write_partitioned_dataset,
)
from synpuf_downloader.infrastructure.filesystem import ensure_layout, list_csv_paths, remove_path


def main() -> int:
  parser = _build_parser()
  args = parser.parse_args()
  load_dotenv()
  input_dir = require_env_path(args.input_dir)
  if input_dir is None:
    parser.error(
      'Input directory must be specified via --input-dir or SYNPUF_DIR environment variable'
    )
  layout = resolve_layout(input_dir)
  logger, log_file = configure_logging('convert', layout, args.log_level)
  print('SynPUF CSV to Parquet Converter')
  print(f'Input directory: {layout.base_dir}')
  print(f'Log file: {log_file}')
  print('-' * 50)
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
    logger=logger,
  )
  summary = summarize_conversions(results)
  print(format_conversion_summary(summary, log_file))
  if summary.failed_datasets == 0:
    print('\nAll conversions completed successfully.')
    return 0
  print('\nSome conversions failed. Check the log file for details.')
  return 1


def _build_parser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser(
    description='Convert SynPUF CSV files to partitioned Parquet format',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="""
Examples:
  %(prog)s
  %(prog)s --input-dir /path/to/synpuf
  %(prog)s --log-level DEBUG
    """,
  )
  parser.add_argument(
    '--input-dir',
    help='SynPUF directory (overrides SYNPUF_DIR environment variable)',
  )
  parser.add_argument(
    '--log-level',
    choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
    default='INFO',
    help='Logging level',
  )
  return parser
