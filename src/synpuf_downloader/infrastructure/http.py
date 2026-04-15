from __future__ import annotations

from pathlib import Path

import requests
from tqdm import tqdm


def head_url(
  url: str,
  timeout_seconds: int = 10,
) -> tuple[int, dict[str, str]]:
  response = requests.head(url, allow_redirects=True, timeout=timeout_seconds)
  return response.status_code, dict(response.headers)


def download_file(
  url: str,
  destination: Path,
  timeout_seconds: int = 30,
  chunk_size: int = 8192,
  progress_label: str | None = None,
) -> int:
  destination.parent.mkdir(parents=True, exist_ok=True)
  with requests.get(url, stream=True, allow_redirects=True, timeout=timeout_seconds) as response:
    response.raise_for_status()
    total_size = int(response.headers.get('content-length', 0))
    with (
      destination.open('wb') as output_handle,
      tqdm(
        desc=progress_label or destination.name,
        total=total_size,
        unit='B',
        unit_scale=True,
        unit_divisor=1024,
        leave=False,
      ) as progress_bar,
    ):
      for chunk in response.iter_content(chunk_size=chunk_size):
        if not chunk:
          continue
        written = output_handle.write(chunk)
        progress_bar.update(written)
  return destination.stat().st_size
