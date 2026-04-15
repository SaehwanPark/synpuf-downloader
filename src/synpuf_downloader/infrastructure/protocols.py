from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Protocol

import pyarrow as pa

from synpuf_downloader.domain.models import DatasetInspection, OutputLayout


class EnsureLayout(Protocol):
  def __call__(self, layout: OutputLayout) -> None: ...


class ExistingZipFilenames(Protocol):
  def __call__(self, layout: OutputLayout) -> frozenset[str]: ...


class ListCsvPaths(Protocol):
  def __call__(self, layout: OutputLayout) -> tuple[Path, ...]: ...


class RemovePath(Protocol):
  def __call__(self, path: Path) -> None: ...


class HeadUrl(Protocol):
  def __call__(
    self,
    url: str,
    timeout_seconds: int = 10,
  ) -> tuple[int, Mapping[str, str]]: ...


class DownloadFile(Protocol):
  def __call__(
    self,
    url: str,
    destination: Path,
    timeout_seconds: int = 30,
    chunk_size: int = 8192,
    progress_label: str | None = None,
  ) -> int: ...


class ExtractZip(Protocol):
  def __call__(
    self,
    zip_path: Path,
    destination: Path,
    progress_label: str | None = None,
  ) -> tuple[str, ...]: ...


class ReadCsvHeader(Protocol):
  def __call__(self, csv_path: Path) -> tuple[str, ...]: ...


class InferSchema(Protocol):
  def __call__(self, csv_path: Path) -> pa.Schema: ...


class ReadTable(Protocol):
  def __call__(self, csv_path: Path, schema: pa.Schema) -> pa.Table: ...


class WriteDataset(Protocol):
  def __call__(self, table: pa.Table, destination: Path, max_rows_per_file: int) -> None: ...


class InspectDataset(Protocol):
  def __call__(self, destination: Path) -> DatasetInspection: ...
