from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path
from typing import Iterable

from .models import ExternalRecord, RedirectRecord, URLRecord


def export_results(
    output_dir: str | Path,
    *,
    internal_urls: Iterable[str],
    pages: Iterable[URLRecord],
    files: Iterable[URLRecord],
    external_urls: Iterable[ExternalRecord],
    broken_urls: Iterable[URLRecord],
    redirects: Iterable[RedirectRecord],
    stats: dict[str, object],
) -> None:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    _write_lines(directory / "urls.txt", sorted(set(internal_urls)))
    _write_csv(
        directory / "pages.csv",
        (asdict(record) for record in pages),
        ["url", "status_code", "content_type", "source_url", "depth", "final_url"],
    )
    detail_fields = [
        "url", "status_code", "content_type", "source_url", "depth", "final_url",
        "discovered_at", "response_time_ms", "error",
    ]
    _write_csv(directory / "files.csv", (asdict(record) for record in files), detail_fields)
    _write_csv(
        directory / "external_urls.csv",
        (asdict(record) for record in external_urls),
        ["url", "source_url", "discovered_at"],
    )
    _write_csv(directory / "broken_urls.csv", (asdict(record) for record in broken_urls), detail_fields)
    _write_csv(
        directory / "redirects.csv",
        (asdict(record) for record in redirects),
        ["source_url", "status_code", "destination_url"],
    )
    with (directory / "stats.json").open("w", encoding="utf-8") as handle:
        json.dump(stats, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def _write_lines(path: Path, lines: Iterable[str]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for line in lines:
            handle.write(f"{line}\n")


def _write_csv(path: Path, rows: Iterable[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
