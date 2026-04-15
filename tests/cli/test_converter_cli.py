from __future__ import annotations

import sys
from pathlib import Path

from pytest import CaptureFixture, MonkeyPatch

from synpuf_downloader.cli import converter as converter_cli
from synpuf_downloader.domain import ConversionResult, ConversionStatus, DatasetKind


def test_converter_cli_uses_input_dir_override(
  monkeypatch: MonkeyPatch,
  tmp_path: Path,
  capsys: CaptureFixture[str],
) -> None:
  monkeypatch.setattr(
    converter_cli,
    'run_conversion',
    lambda *args, **kwargs: (
      ConversionResult(
        dataset_kind=DatasetKind.BENEFICIARY_2008,
        status=ConversionStatus.WRITTEN,
        output_path=tmp_path / 'parquets' / 'DE1_0_2008_Beneficiary_Summary_File.parquet',
        row_count=1,
        partition_count=1,
        column_count=2,
      ),
    ),
  )
  monkeypatch.setattr(sys, 'argv', ['converter.py', '--input-dir', str(tmp_path)])

  exit_code = converter_cli.main()
  output = capsys.readouterr().out

  assert exit_code == 0
  assert 'SynPUF CSV to Parquet Converter' in output


def test_converter_cli_returns_failure_code_when_conversion_fails(
  monkeypatch: MonkeyPatch,
  tmp_path: Path,
) -> None:
  monkeypatch.setattr(
    converter_cli,
    'run_conversion',
    lambda *args, **kwargs: (
      ConversionResult(
        dataset_kind=DatasetKind.BENEFICIARY_2008,
        status=ConversionStatus.FAILED,
        detail='broken',
      ),
    ),
  )
  monkeypatch.setattr(sys, 'argv', ['converter.py', '--input-dir', str(tmp_path)])

  assert converter_cli.main() == 1
