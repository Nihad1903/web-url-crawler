from __future__ import annotations

import gzip
from dataclasses import dataclass
from xml.etree import ElementTree


@dataclass(frozen=True, slots=True)
class SitemapDocument:
    urls: tuple[str, ...]
    sitemaps: tuple[str, ...]


def decode_sitemap(data: bytes, url: str, content_encoding: str = "") -> bytes:
    if url.lower().endswith(".gz") and content_encoding.lower() != "gzip":
        return gzip.decompress(data)
    return data


def parse_sitemap(data: bytes) -> SitemapDocument:
    root = ElementTree.fromstring(data)
    root_name = _local_name(root.tag)
    locations = tuple(
        (element.text or "").strip()
        for element in root.iter()
        if _local_name(element.tag) == "loc" and (element.text or "").strip()
    )
    if root_name == "sitemapindex":
        return SitemapDocument(urls=(), sitemaps=locations)
    if root_name == "urlset":
        return SitemapDocument(urls=locations, sitemaps=())
    raise ValueError(f"Unsupported sitemap root element: {root_name}")


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()
