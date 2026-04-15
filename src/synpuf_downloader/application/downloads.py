from __future__ import annotations

import logging

from synpuf_downloader.domain.downloads import build_source_artifacts, plan_download
from synpuf_downloader.domain.models import (
  DownloadRequest,
  DownloadResult,
  DownloadStatus,
  SourceArtifact,
)
from synpuf_downloader.infrastructure.protocols import (
  DownloadFile,
  EnsureLayout,
  ExistingZipFilenames,
  ExtractZip,
  HeadUrl,
  RemovePath,
)


def run_download(
  request: DownloadRequest,
  *,
  ensure_layout: EnsureLayout,
  existing_zip_filenames: ExistingZipFilenames,
  head_url: HeadUrl,
  download_file: DownloadFile,
  extract_zip: ExtractZip,
  remove_path: RemovePath,
  logger: logging.Logger,
) -> tuple[DownloadResult, ...]:
  ensure_layout(request.output_layout)
  all_artifacts = build_source_artifacts(request.samples)
  planned_artifacts = plan_download(request, existing_zip_filenames(request.output_layout))
  planned_by_filename = {artifact.filename: artifact for artifact in planned_artifacts}
  return tuple(
    _execute_download_artifact(
      artifact,
      request,
      head_url=head_url,
      download_file=download_file,
      extract_zip=extract_zip,
      remove_path=remove_path,
      logger=logger,
    )
    if artifact.filename in planned_by_filename
    else DownloadResult(
      artifact=artifact,
      status=DownloadStatus.SKIPPED,
      detail='Skipped existing archive',
    )
    for artifact in all_artifacts
  )


def _execute_download_artifact(
  artifact: SourceArtifact,
  request: DownloadRequest,
  *,
  head_url: HeadUrl,
  download_file: DownloadFile,
  extract_zip: ExtractZip,
  remove_path: RemovePath,
  logger: logging.Logger,
) -> DownloadResult:
  if request.validate_only:
    return _validate_artifact(artifact, head_url=head_url, logger=logger)
  zip_path = request.output_layout.zip_dir / artifact.filename
  try:
    logger.info('Downloading %s', artifact.url)
    bytes_downloaded = download_file(artifact.url, zip_path, progress_label=artifact.filename)
  except Exception as error:
    logger.exception('Failed to download %s', artifact.filename)
    remove_path(zip_path)
    return DownloadResult(
      artifact=artifact,
      status=DownloadStatus.DOWNLOAD_FAILED,
      detail=str(error),
    )
  try:
    extracted_files = extract_zip(
      zip_path,
      request.output_layout.csv_dir,
      progress_label=f'Extracting {artifact.filename}',
    )
  except Exception as error:
    logger.exception('Failed to extract %s', artifact.filename)
    return DownloadResult(
      artifact=artifact,
      status=DownloadStatus.EXTRACT_FAILED,
      detail=str(error),
      bytes_downloaded=bytes_downloaded,
    )
  logger.info('Extracted %s into %s', artifact.filename, request.output_layout.csv_dir)
  return DownloadResult(
    artifact=artifact,
    status=DownloadStatus.EXTRACTED,
    bytes_downloaded=bytes_downloaded,
    extracted_files=extracted_files,
  )


def _validate_artifact(
  artifact: SourceArtifact,
  *,
  head_url: HeadUrl,
  logger: logging.Logger,
) -> DownloadResult:
  try:
    status_code, headers = head_url(artifact.url)
  except Exception as error:
    logger.exception('Failed to validate %s', artifact.filename)
    return DownloadResult(
      artifact=artifact,
      status=DownloadStatus.DOWNLOAD_FAILED,
      detail=str(error),
    )
  if status_code != 200:
    logger.warning('Validation failed for %s with status %s', artifact.filename, status_code)
    return DownloadResult(
      artifact=artifact,
      status=DownloadStatus.DOWNLOAD_FAILED,
      detail=f'HTTP {status_code}',
    )
  size_description = headers.get('content-length', 'unknown')
  logger.info('Validated %s (%s bytes)', artifact.filename, size_description)
  return DownloadResult(
    artifact=artifact,
    status=DownloadStatus.VALIDATED,
    detail=f'size={size_description}',
  )
