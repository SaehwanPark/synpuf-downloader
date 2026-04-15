from __future__ import annotations

import sys
from pathlib import Path

from pytest import CaptureFixture, MonkeyPatch

from synpuf_downloader.cli import downloader as downloader_cli
from synpuf_downloader.domain import (
  DownloadResult,
  DownloadStatus,
  SampleId,
  build_source_artifacts,
)


def test_downloader_cli_uses_synpuf_dir_from_env(
  monkeypatch: MonkeyPatch,
  tmp_path: Path,
  capsys: CaptureFixture[str],
) -> None:
  artifacts = build_source_artifacts((SampleId(1),))
  monkeypatch.setenv('SYNPUF_DIR', str(tmp_path))
  monkeypatch.setattr(
    downloader_cli,
    'run_download',
    lambda *args, **kwargs: tuple(
      DownloadResult(artifact=artifact, status=DownloadStatus.EXTRACTED, bytes_downloaded=1)
      for artifact in artifacts
    ),
  )
  monkeypatch.setattr(sys, 'argv', ['downloader.py', '--samples', '1'])

  exit_code = downloader_cli.main()
  output = capsys.readouterr().out

  assert exit_code == 0
  assert 'SynPUF Downloader' in output
  assert 'Output directory' in output


def test_downloader_cli_returns_failure_code_on_errors(
  monkeypatch: MonkeyPatch,
  tmp_path: Path,
) -> None:
  artifact = build_source_artifacts((SampleId(1),))[0]
  monkeypatch.setenv('SYNPUF_DIR', str(tmp_path))
  monkeypatch.setattr(
    downloader_cli,
    'run_download',
    lambda *args, **kwargs: (
      DownloadResult(artifact=artifact, status=DownloadStatus.DOWNLOAD_FAILED),
    ),
  )
  monkeypatch.setattr(sys, 'argv', ['downloader.py', '--samples', '1'])

  assert downloader_cli.main() == 1
