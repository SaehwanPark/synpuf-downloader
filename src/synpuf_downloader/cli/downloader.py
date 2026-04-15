from __future__ import annotations

import argparse

from dotenv import load_dotenv

from synpuf_downloader.application.downloads import run_download
from synpuf_downloader.cli.common import (
  configure_logging,
  format_download_failures,
  format_download_summary,
  parse_samples,
  require_env_path,
  resolve_layout,
)
from synpuf_downloader.domain import DownloadRequest, summarize_downloads
from synpuf_downloader.infrastructure.filesystem import (
  ensure_layout,
  existing_zip_filenames,
  extract_zip,
  remove_path,
)
from synpuf_downloader.infrastructure.http import download_file, head_url


def main() -> int:
  parser = _build_parser()
  args = parser.parse_args()
  load_dotenv()
  output_dir = require_env_path(args.output_dir)
  if output_dir is None:
    parser.error(
      'Output directory must be specified via --output-dir or SYNPUF_DIR environment variable'
    )
  try:
    samples = parse_samples(args.samples, args.all)
  except ValueError as error:
    parser.error(str(error))
  layout = resolve_layout(output_dir)
  logger, log_file = configure_logging('download', layout, args.log_level)
  request = DownloadRequest(
    output_layout=layout,
    samples=samples,
    validate_only=args.validate,
    skip_existing=not args.force,
  )
  print('SynPUF Downloader')
  print(f'Output directory: {layout.base_dir}')
  print(f'Log file: {log_file}')
  print(f'Samples to process: {[sample.value for sample in samples]}')
  if args.validate:
    print('Mode: URL Validation')
  else:
    print(f'Skip existing files: {not args.force}')
  print('-' * 50)
  results = run_download(
    request,
    ensure_layout=ensure_layout,
    existing_zip_filenames=existing_zip_filenames,
    head_url=head_url,
    download_file=download_file,
    extract_zip=extract_zip,
    remove_path=remove_path,
    logger=logger,
  )
  summary = summarize_downloads(results)
  print(format_download_summary(summary, log_file, args.validate))
  failure_report = format_download_failures(summary.results)
  if failure_report:
    print(failure_report)
  success = summary.failed_downloads == 0 and summary.failed_extractions == 0
  if success:
    print('\nAll requested download operations completed successfully.')
    return 0
  print('\nSome download operations failed. Check the log file for details.')
  return 1


def _build_parser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser(
    description='Download and extract CMS SynPUF data files',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="""
Examples:
  %(prog)s --samples 1 2 3
  %(prog)s --all
  %(prog)s --samples 5 --force
    """,
  )
  parser.add_argument(
    '--samples',
    type=int,
    nargs='+',
    metavar='N',
    help='Sample numbers to download (1-20)',
  )
  parser.add_argument('--all', action='store_true', help='Download all 20 samples')
  parser.add_argument('--validate', action='store_true', help='Validate URLs without downloading')
  parser.add_argument(
    '--force',
    action='store_true',
    help='Re-download files even if they already exist',
  )
  parser.add_argument(
    '--output-dir',
    help='Output directory (overrides SYNPUF_DIR environment variable)',
  )
  parser.add_argument(
    '--log-level',
    choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
    default='INFO',
    help='Logging level',
  )
  return parser
