from __future__ import annotations

import logging
from pathlib import Path

from synpuf_downloader.application.downloads import run_download
from synpuf_downloader.domain import DownloadRequest, DownloadStatus, OutputLayout, SampleId


def test_run_download_extracts_artifacts_with_fake_ports(tmp_path: Path) -> None:
  layout = OutputLayout.from_base_dir(tmp_path)
  logger = logging.getLogger('test.download.extract')
  request = DownloadRequest(output_layout=layout, samples=(SampleId(1),), skip_existing=False)

  results = run_download(
    request,
    ensure_layout=lambda current_layout: _ensure_layout(current_layout),
    existing_zip_filenames=lambda current_layout: frozenset(),
    head_url=lambda url, timeout_seconds=10: (200, {'content-length': '10'}),
    download_file=_fake_download,
    extract_zip=_fake_extract,
    remove_path=lambda path: None,
    logger=logger,
  )

  assert len(results) == 8
  assert all(result.status == DownloadStatus.EXTRACTED for result in results)
  assert (layout.csv_dir / 'DE1_0_2008_Beneficiary_Summary_File_Sample_1.csv').exists()


def test_run_download_marks_existing_files_as_skipped(tmp_path: Path) -> None:
  layout = OutputLayout.from_base_dir(tmp_path)
  logger = logging.getLogger('test.download.skip')
  request = DownloadRequest(output_layout=layout, samples=(SampleId(1),), skip_existing=True)

  results = run_download(
    request,
    ensure_layout=lambda current_layout: _ensure_layout(current_layout),
    existing_zip_filenames=lambda current_layout: frozenset(
      {'de1_0_2008_beneficiary_summary_file_sample_1.zip'}
    ),
    head_url=lambda url, timeout_seconds=10: (200, {'content-length': '10'}),
    download_file=_fake_download,
    extract_zip=_fake_extract,
    remove_path=lambda path: None,
    logger=logger,
  )

  assert results[0].status == DownloadStatus.SKIPPED


def test_run_download_reports_extract_failures(tmp_path: Path) -> None:
  layout = OutputLayout.from_base_dir(tmp_path)
  logger = logging.getLogger('test.download.failure')
  request = DownloadRequest(output_layout=layout, samples=(SampleId(1),), skip_existing=False)

  results = run_download(
    request,
    ensure_layout=lambda current_layout: _ensure_layout(current_layout),
    existing_zip_filenames=lambda current_layout: frozenset(),
    head_url=lambda url, timeout_seconds=10: (200, {'content-length': '10'}),
    download_file=_fake_download,
    extract_zip=lambda zip_path, destination, progress_label=None: (_ for _ in ()).throw(
      ValueError('bad zip')
    ),
    remove_path=lambda path: None,
    logger=logger,
  )

  assert all(result.status == DownloadStatus.EXTRACT_FAILED for result in results)


def _ensure_layout(layout: OutputLayout) -> None:
  for directory in (
    layout.base_dir,
    layout.zip_dir,
    layout.csv_dir,
    layout.parquet_dir,
    layout.log_dir,
  ):
    directory.mkdir(parents=True, exist_ok=True)


def _fake_download(
  url: str,
  destination: Path,
  timeout_seconds: int = 30,
  chunk_size: int = 8192,
  progress_label: str | None = None,
) -> int:
  destination.parent.mkdir(parents=True, exist_ok=True)
  destination.write_bytes(b'zip-bytes')
  return len(b'zip-bytes')


def _fake_extract(
  zip_path: Path,
  destination: Path,
  progress_label: str | None = None,
) -> tuple[str, ...]:
  destination.mkdir(parents=True, exist_ok=True)
  csv_name = _csv_name_for_zip(zip_path.name)
  (destination / csv_name).write_text('BENE_ID,CLAIM_COUNT\n1,2\n', encoding='utf-8')
  return (csv_name,)


def _csv_name_for_zip(zip_name: str) -> str:
  normalized = zip_name.removesuffix('.zip')
  if normalized.endswith('.csv'):
    normalized = normalized.removesuffix('.csv')
  if normalized.startswith('de1_0_2008_beneficiary_summary_file_sample_'):
    suffix = normalized.rsplit('_', 1)[-1]
    return f'DE1_0_2008_Beneficiary_Summary_File_Sample_{suffix}.csv'
  transformed = (
    normalized.replace(
      'de1_0_2008_to_2010_inpatient_claims',
      'DE1_0_2008_to_2010_Inpatient_Claims',
    )
    .replace(
      'de1_0_2008_to_2010_outpatient_claims',
      'DE1_0_2008_to_2010_Outpatient_Claims',
    )
    .replace(
      'de1_0_2008_to_2010_prescription_drug_events',
      'DE1_0_2008_to_2010_Prescription_Drug_Events',
    )
  )
  return f'{transformed}.csv'
