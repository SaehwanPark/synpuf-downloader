from __future__ import annotations

from pathlib import Path

import pytest

from synpuf_downloader.domain import (
  CarrierPart,
  DownloadRequest,
  DownloadResult,
  DownloadStatus,
  FileKind,
  OutputLayout,
  SampleId,
  SourceArtifact,
  build_source_artifacts,
  plan_download,
  summarize_downloads,
)


def test_sample_id_rejects_invalid_range() -> None:
  with pytest.raises(ValueError):
    SampleId(0)
  with pytest.raises(ValueError):
    SampleId(21)


def test_build_source_artifacts_preserves_known_cms_edge_cases() -> None:
  artifacts = build_source_artifacts((SampleId(1), SampleId(11), SampleId(20)))
  sample_1_2010 = _artifact_for(artifacts, 1, FileKind.BENEFICIARY_2010)
  sample_11_carrier_a = _artifact_for(artifacts, 11, FileKind.CARRIER_CLAIMS, CarrierPart.A)
  sample_20_2008 = _artifact_for(artifacts, 20, FileKind.BENEFICIARY_2008)
  sample_20_inpatient = _artifact_for(artifacts, 20, FileKind.INPATIENT_CLAIMS)

  assert sample_1_2010.filename == 'DE1_0_2010_Beneficiary_Summary_File_Sample_1.zip'
  assert 'sites/default/files/2020-09/' in sample_1_2010.url
  assert sample_11_carrier_a.filename.endswith('.csv.zip')
  assert 'statistics-trends-and-reports/synpufs/downloads/' in sample_20_2008.url
  assert 'statistics-trends-and-reports/synpufs/downloads/' in sample_20_inpatient.url


def test_plan_download_skips_existing_archives(tmp_path: Path) -> None:
  layout = OutputLayout.from_base_dir(tmp_path)
  request = DownloadRequest(output_layout=layout, samples=(SampleId(1),), skip_existing=True)
  planned = plan_download(
    request,
    frozenset({'de1_0_2008_beneficiary_summary_file_sample_1.zip'}),
  )

  assert len(planned) == 7
  assert all(
    artifact.filename != 'de1_0_2008_beneficiary_summary_file_sample_1.zip' for artifact in planned
  )


def test_summarize_downloads_counts_outcomes() -> None:
  artifact = build_source_artifacts((SampleId(1),))[0]
  summary = summarize_downloads(
    (
      DownloadResult(artifact=artifact, status=DownloadStatus.SKIPPED),
      DownloadResult(artifact=artifact, status=DownloadStatus.EXTRACTED, bytes_downloaded=1),
      DownloadResult(artifact=artifact, status=DownloadStatus.EXTRACT_FAILED, bytes_downloaded=1),
      DownloadResult(artifact=artifact, status=DownloadStatus.DOWNLOAD_FAILED),
      DownloadResult(artifact=artifact, status=DownloadStatus.VALIDATED),
    )
  )

  assert summary.total_files == 5
  assert summary.skipped_files == 1
  assert summary.attempted_files == 4
  assert summary.successful_downloads == 2
  assert summary.failed_downloads == 1
  assert summary.successful_extractions == 1
  assert summary.failed_extractions == 1
  assert summary.validated_files == 1


def _artifact_for(
  artifacts: tuple[SourceArtifact, ...],
  sample_id: int,
  file_kind: FileKind,
  carrier_part: CarrierPart | None = None,
) -> SourceArtifact:
  return next(
    artifact
    for artifact in artifacts
    if artifact.sample_id.value == sample_id
    and artifact.file_kind == file_kind
    and artifact.carrier_part == carrier_part
  )
