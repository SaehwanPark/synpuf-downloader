from __future__ import annotations

from synpuf_downloader.domain.models import (
  CarrierPart,
  DatasetKind,
  DownloadRequest,
  DownloadResult,
  DownloadStatus,
  DownloadSummary,
  FileKind,
  SampleId,
  SourceArtifact,
)

CMS_ROOT = 'https://www.cms.gov/'
STANDARD_CMS_PATH = (
  'research-statistics-data-and-systems/downloadable-public-use-files/synpufs/downloads/'
)
LEGACY_CMS_PATH = (
  'research-statistics-data-and-systems/statistics-trends-and-reports/synpufs/downloads/'
)
SAMPLE_1_2010_PATH = 'sites/default/files/2020-09/'
DOWNLOADS_ROOT = 'http://downloads.cms.gov/files/'


def build_source_artifacts(samples: tuple[SampleId, ...]) -> tuple[SourceArtifact, ...]:
  return tuple(
    artifact
    for sample in samples
    for artifact in (
      _build_beneficiary_artifact(sample, 2008),
      _build_beneficiary_artifact(sample, 2009),
      _build_beneficiary_artifact(sample, 2010),
      _build_carrier_artifact(sample, CarrierPart.A),
      _build_carrier_artifact(sample, CarrierPart.B),
      _build_inpatient_artifact(sample),
      _build_outpatient_artifact(sample),
      _build_prescription_artifact(sample),
    )
  )


def plan_download(
  request: DownloadRequest,
  existing_files: frozenset[str],
) -> tuple[SourceArtifact, ...]:
  if request.validate_only or not request.skip_existing:
    return build_source_artifacts(request.samples)
  return tuple(
    artifact
    for artifact in build_source_artifacts(request.samples)
    if artifact.filename not in existing_files
  )


def summarize_downloads(results: tuple[DownloadResult, ...]) -> DownloadSummary:
  skipped_files = sum(result.status == DownloadStatus.SKIPPED for result in results)
  attempted_files = len(results) - skipped_files
  successful_downloads = sum(
    result.status in {DownloadStatus.EXTRACTED, DownloadStatus.EXTRACT_FAILED} for result in results
  )
  failed_downloads = sum(result.status == DownloadStatus.DOWNLOAD_FAILED for result in results)
  successful_extractions = sum(result.status == DownloadStatus.EXTRACTED for result in results)
  failed_extractions = sum(result.status == DownloadStatus.EXTRACT_FAILED for result in results)
  validated_files = sum(result.status == DownloadStatus.VALIDATED for result in results)
  failed_validations = sum(
    result.status == DownloadStatus.DOWNLOAD_FAILED and result.bytes_downloaded == 0
    for result in results
  )
  return DownloadSummary(
    total_files=len(results),
    skipped_files=skipped_files,
    attempted_files=attempted_files,
    successful_downloads=successful_downloads,
    failed_downloads=failed_downloads,
    successful_extractions=successful_extractions,
    failed_extractions=failed_extractions,
    validated_files=validated_files,
    failed_validations=failed_validations,
    results=results,
  )


def _build_beneficiary_artifact(sample: SampleId, year: int) -> SourceArtifact:
  file_kind = {
    2008: FileKind.BENEFICIARY_2008,
    2009: FileKind.BENEFICIARY_2009,
    2010: FileKind.BENEFICIARY_2010,
  }[year]
  dataset_kind = {
    2008: DatasetKind.BENEFICIARY_2008,
    2009: DatasetKind.BENEFICIARY_2009,
    2010: DatasetKind.BENEFICIARY_2010,
  }[year]
  filename = _beneficiary_filename(sample, year)
  path = _beneficiary_path(sample, year)
  return SourceArtifact(
    sample_id=sample,
    file_kind=file_kind,
    dataset_kind=dataset_kind,
    filename=filename,
    url=f'{CMS_ROOT}{path}{filename}',
  )


def _build_carrier_artifact(sample: SampleId, carrier_part: CarrierPart) -> SourceArtifact:
  filename = _carrier_filename(sample, carrier_part)
  return SourceArtifact(
    sample_id=sample,
    file_kind=FileKind.CARRIER_CLAIMS,
    dataset_kind=DatasetKind.CARRIER_CLAIMS,
    filename=filename,
    url=f'{DOWNLOADS_ROOT}{filename}',
    carrier_part=carrier_part,
  )


def _build_inpatient_artifact(sample: SampleId) -> SourceArtifact:
  filename = f'de1_0_2008_to_2010_inpatient_claims_sample_{sample.value}.zip'
  path = LEGACY_CMS_PATH if sample.value == 20 else STANDARD_CMS_PATH
  return SourceArtifact(
    sample_id=sample,
    file_kind=FileKind.INPATIENT_CLAIMS,
    dataset_kind=DatasetKind.INPATIENT_CLAIMS,
    filename=filename,
    url=f'{CMS_ROOT}{path}{filename}',
  )


def _build_outpatient_artifact(sample: SampleId) -> SourceArtifact:
  filename = f'de1_0_2008_to_2010_outpatient_claims_sample_{sample.value}.zip'
  return SourceArtifact(
    sample_id=sample,
    file_kind=FileKind.OUTPATIENT_CLAIMS,
    dataset_kind=DatasetKind.OUTPATIENT_CLAIMS,
    filename=filename,
    url=f'{CMS_ROOT}{STANDARD_CMS_PATH}{filename}',
  )


def _build_prescription_artifact(sample: SampleId) -> SourceArtifact:
  filename = f'DE1_0_2008_to_2010_Prescription_Drug_Events_Sample_{sample.value}.zip'
  return SourceArtifact(
    sample_id=sample,
    file_kind=FileKind.PRESCRIPTION_DRUG_EVENTS,
    dataset_kind=DatasetKind.PRESCRIPTION_DRUG_EVENTS,
    filename=filename,
    url=f'{DOWNLOADS_ROOT}{filename}',
  )


def _beneficiary_filename(sample: SampleId, year: int) -> str:
  if sample.value == 1 and year == 2010:
    return f'DE1_0_{year}_Beneficiary_Summary_File_Sample_{sample.value}.zip'
  return f'de1_0_{year}_beneficiary_summary_file_sample_{sample.value}.zip'


def _beneficiary_path(sample: SampleId, year: int) -> str:
  if sample.value == 1 and year == 2010:
    return SAMPLE_1_2010_PATH
  if sample.value == 20 and year == 2008:
    return LEGACY_CMS_PATH
  return STANDARD_CMS_PATH


def _carrier_filename(sample: SampleId, carrier_part: CarrierPart) -> str:
  if sample.value == 11 and carrier_part == CarrierPart.A:
    return f'DE1_0_2008_to_2010_Carrier_Claims_Sample_{sample.value}{carrier_part.value}.csv.zip'
  return f'DE1_0_2008_to_2010_Carrier_Claims_Sample_{sample.value}{carrier_part.value}.zip'
