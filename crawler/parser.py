from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from bs4 import BeautifulSoup

BOILERPLATE_TAGS = ("script", "style", "noscript", "template", "nav", "header", "footer", "aside")
MIN_PARAGRAPH_CHARS = 20


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
    for tag in soup(BOILERPLATE_TAGS):
        tag.decompose()
    title = _extract_title(soup)
    text = _extract_text(soup)
    return ParsedPage(links=links, canonical=canonical, title=title, text=text)


def _extract_title(soup: BeautifulSoup) -> str:
    # Many CMS-driven sites set <title> to a fixed brand name and put the
    # actual page heading in the first <h1>; prefer that when it's present.
    heading = soup.find("h1")
    if heading:
        text = heading.get_text(strip=True)
        if text:
            return text
    title_tag = soup.find("title")
    return title_tag.get_text(strip=True) if title_tag else ""


def _extract_text(soup: BeautifulSoup) -> str:
    # Semantic containers are the most reliable signal when present.
    for tag_name in ("main", "article"):
        container = soup.find(tag_name)
        if container and container.get_text(strip=True):
            return _clean_text(container)

    # Otherwise, pick the element holding the largest cluster of substantial
    # <p> text: a lightweight stand-in for the page's main content block on
    # sites that build layout from generic <div>s instead of semantic tags.
    scores: Counter = Counter()
    for paragraph in soup.find_all("p"):
        length = len(paragraph.get_text(strip=True))
        if length >= MIN_PARAGRAPH_CHARS and paragraph.parent is not None:
            scores[paragraph.parent] += length
    if scores:
        return _clean_text(scores.most_common(1)[0][0])

    container = soup.body or soup
    return _clean_text(container)


def _clean_text(container) -> str:
    return " ".join(container.get_text(separator=" ", strip=True).split())
