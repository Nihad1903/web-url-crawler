from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from dataclasses import replace

from crawler.config import Settings, SettingsError
from crawler.crawler import WebsiteCrawler


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Discover internal URLs, files, redirects and broken links on a website."
    )
    parser.add_argument("url", nargs="?", help="Start URL (overrides START_URL in .env)")
    parser.add_argument("--max-pages", type=int, help="Maximum number of HTTP URLs to request")
    parser.add_argument("--depth", type=int, help="Maximum link depth")
    parser.add_argument("--concurrency", type=int, help="Maximum concurrent requests")
    parser.add_argument("--output", help="Output directory")
    return parser


async def async_main() -> int:
    args = build_parser().parse_args()
    try:
        settings = Settings.from_env()
        updates: dict[str, object] = {}
        if args.url:
            updates["start_url"] = args.url
        if args.max_pages is not None:
            updates["max_pages"] = args.max_pages
        if args.depth is not None:
            updates["max_depth"] = args.depth
        if args.concurrency is not None:
            updates["max_concurrency"] = args.concurrency
        if args.output:
            updates["output_dir"] = args.output
        settings = replace(settings, **updates)
        settings.validate()
        crawler = WebsiteCrawler(settings)
    except (SettingsError, ValueError) as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2

    try:
        await crawler.run()
        return 0
    except RuntimeError as exc:
        print(f"Crawler error: {exc}", file=sys.stderr)
        return 1


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
    try:
        return asyncio.run(async_main())
    except KeyboardInterrupt:
        print("\nCrawler stopped.")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
