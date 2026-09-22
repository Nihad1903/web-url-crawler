from __future__ import annotations

from dataclasses import dataclass

from bs4 import BeautifulSoup

BOILERPLATE_TAGS = ("script", "style", "noscript", "template", "nav", "header", "footer", "aside")


@dataclass(frozen=True, slots=True)
class ParsedPage:
    links: tuple[str, ...]
    canonical: str | None
    title: str
    text: str


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
    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else ""
    text = _extract_text(soup)
    return ParsedPage(links=links, canonical=canonical, title=title, text=text)


def _extract_text(soup: BeautifulSoup) -> str:
    for tag in soup(BOILERPLATE_TAGS):
        tag.decompose()
    container = soup.find("main") or soup.find("article") or soup.body or soup
    return " ".join(container.get_text(separator=" ", strip=True).split())
