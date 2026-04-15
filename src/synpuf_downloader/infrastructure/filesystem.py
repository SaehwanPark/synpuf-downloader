from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

from tqdm import tqdm

from synpuf_downloader.domain.models import OutputLayout


def ensure_layout(layout: OutputLayout) -> None:
  for directory in (
    layout.base_dir,
    layout.zip_dir,
    layout.csv_dir,
    layout.parquet_dir,
    layout.log_dir,
  ):
    directory.mkdir(parents=True, exist_ok=True)


def existing_zip_filenames(layout: OutputLayout) -> frozenset[str]:
  if not layout.zip_dir.exists():
    return frozenset()
  return frozenset(path.name for path in layout.zip_dir.glob('*.zip'))


def list_csv_paths(layout: OutputLayout) -> tuple[Path, ...]:
  if not layout.csv_dir.exists():
    return ()
  return tuple(sorted(layout.csv_dir.glob('*.csv')))


def remove_path(path: Path) -> None:
  if path.is_dir():
    shutil.rmtree(path, ignore_errors=True)
    return
  if path.exists():
    path.unlink()


def extract_zip(
  zip_path: Path,
  destination: Path,
  progress_label: str | None = None,
) -> tuple[str, ...]:
  destination.mkdir(parents=True, exist_ok=True)
  with zipfile.ZipFile(zip_path, 'r') as archive:
    members = tuple(archive.namelist())
    for member in tqdm(
      members,
      desc=progress_label or f'Extracting {zip_path.name}',
      leave=False,
    ):
      archive.extract(member, destination)
  return members
