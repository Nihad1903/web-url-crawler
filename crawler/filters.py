from __future__ import annotations

from pathlib import PurePosixPath
from urllib.parse import urlsplit

HTML_CONTENT_TYPES = {"text/html", "application/xhtml+xml"}
FILE_EXTENSIONS = {
    ".7z", ".avi", ".bmp", ".csv", ".doc", ".docx", ".dmg", ".epub",
    ".gif", ".gz", ".ico", ".iso", ".jpeg", ".jpg", ".json", ".m4a",
    ".mkv", ".mov", ".mp3", ".mp4", ".mpeg", ".ods", ".odt", ".pdf",
    ".png", ".ppt", ".pptx", ".rar", ".rss", ".svg", ".tar", ".tgz",
    ".tif", ".tiff", ".txt", ".wav", ".webm", ".webp", ".woff", ".woff2",
    ".xls", ".xlsx", ".xml", ".zip",
}


def hostname(url: str) -> str:
    return (urlsplit(url).hostname or "").lower().rstrip(".")


def is_internal(url: str, start_url: str, allow_subdomains: bool) -> bool:
    target = hostname(url)
    root = hostname(start_url)
    return target == root or (allow_subdomains and target.endswith(f".{root}"))


def content_type(value: str | None) -> str:
    return (value or "").split(";", 1)[0].strip().lower()


def is_html(value: str | None) -> bool:
    return content_type(value) in HTML_CONTENT_TYPES


def looks_like_file(url: str) -> bool:
    return PurePosixPath(urlsplit(url).path.lower()).suffix in FILE_EXTENSIONS
