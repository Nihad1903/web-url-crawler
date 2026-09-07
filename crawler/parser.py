from __future__ import annotations

from dataclasses import dataclass

from bs4 import BeautifulSoup


@dataclass(frozen=True, slots=True)
class ParsedPage:
    links: tuple[str, ...]
    canonical: str | None


def parse_html(html: str | bytes) -> ParsedPage:
    # BeautifulSoup can inspect byte-order marks, XML declarations and meta charset.
    soup = BeautifulSoup(html, "lxml")
    links = tuple(str(tag["href"]) for tag in soup.find_all("a", href=True))
    canonical = None
    for tag in soup.find_all("link", href=True):
        rel = tag.get("rel", [])
        values = rel if isinstance(rel, list) else str(rel).split()
        if "canonical" in {str(value).lower() for value in values}:
            canonical = str(tag["href"])
            break
    return ParsedPage(links=links, canonical=canonical)
