from __future__ import annotations

import gzip
import unittest

from crawler.filters import is_internal, looks_like_file
from crawler.normalizer import normalize_url
from crawler.robots import parse_robots
from crawler.sitemap import decode_sitemap, parse_sitemap


class URLTests(unittest.TestCase):
    def test_normalization_and_deduplication_form(self) -> None:
        base = "https://Example.COM/docs/page"
        self.assertEqual(
            normalize_url("/about/#team", base, keep_query_params=False),
            "https://example.com/about",
        )
        self.assertEqual(
            normalize_url("/about?ref=1", base, keep_query_params=False),
            "https://example.com/about",
        )
        self.assertEqual(
            normalize_url("/about?ref=1#x", base, keep_query_params=True),
            "https://example.com/about?ref=1",
        )
        self.assertIsNone(normalize_url("mailto:a@example.com", base, keep_query_params=False))

    def test_domain_and_file_filters(self) -> None:
        self.assertTrue(is_internal("https://example.com/a", "https://example.com", False))
        self.assertFalse(is_internal("https://cdn.example.com/a", "https://example.com", False))
        self.assertTrue(is_internal("https://cdn.example.com/a", "https://example.com", True))
        self.assertFalse(is_internal("https://notexample.com/a", "https://example.com", True))
        self.assertTrue(looks_like_file("https://example.com/report.PDF?download=1"))


class DiscoveryDocumentTests(unittest.TestCase):
    def test_robots_rules_and_sitemap_directive(self) -> None:
        policy = parse_robots(
            "https://example.com/robots.txt",
            "User-agent: *\nDisallow: /private\nSitemap: https://example.com/map.xml\n",
            True,
        )
        self.assertFalse(policy.allowed("Crawler/1.0", "https://example.com/private/a"))
        self.assertEqual(policy.sitemap_urls, ("https://example.com/map.xml",))

    def test_nested_and_gzip_sitemap(self) -> None:
        xml = b"<sitemapindex><sitemap><loc>https://example.com/nested.xml</loc></sitemap></sitemapindex>"
        document = parse_sitemap(decode_sitemap(gzip.compress(xml), "https://example.com/index.xml.gz"))
        self.assertEqual(document.sitemaps, ("https://example.com/nested.xml",))


if __name__ == "__main__":
    unittest.main()
