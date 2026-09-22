from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True, slots=True)
class QueueItem:
    url: str
    source_url: str
    depth: int
    discovery_source: str = "html"
    discovered_at: str = field(default_factory=utc_now)


@dataclass(slots=True)
class URLRecord:
    url: str
    status_code: int | None
    content_type: str
    source_url: str
    depth: int
    final_url: str
    discovered_at: str
    response_time_ms: float | None = None
    error: str = ""
    title: str = ""
    content: str = ""


@dataclass(frozen=True, slots=True)
class ExternalRecord:
    url: str
    source_url: str
    discovered_at: str = field(default_factory=utc_now)


@dataclass(frozen=True, slots=True)
class RedirectRecord:
    source_url: str
    status_code: int
    destination_url: str
