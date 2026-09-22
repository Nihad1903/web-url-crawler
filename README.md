# Website URL Crawler

Production-oriented, asynchronous Python crawler that discovers a site's internal
pages through HTML links, `robots.txt`, regular sitemaps, sitemap indexes, nested
sitemaps, and gzip-compressed sitemaps. It records pages, files, external links,
broken URLs, and redirects as separate machine-readable outputs.

## Architecture

The CLI loads validated settings and starts `WebsiteCrawler`. URL normalization
and domain/file filters are pure helper modules. Robots, HTML, and sitemap parsers
only parse their respective formats. The crawler owns the bounded-concurrency
queue, retries, rate limiting, and crawl state; the exporter owns all filesystem
output. Playwright is isolated behind a lazy optional renderer.

```text
main.py
  -> config.py
  -> crawler.py
       -> normalizer.py / filters.py
       -> robots.py / sitemap.py / parser.py
       -> playwright_renderer.py (optional)
       -> exporter.py
```

## Features

- Async crawling with configurable concurrency, timeout, retries, exponential backoff, and delay
- Internal-domain boundary with optional subdomain crawling
- Relative/absolute URL resolution, fragment removal, trailing-slash deduplication, and optional query retention
- `robots.txt` rules and `Sitemap:` directive support
- `<urlset>`, `<sitemapindex>`, nested sitemap, and `.xml.gz` support
- Redirect chains, canonical links, HTTP errors, request errors, and response-time capture
- HTML-only link extraction; known files are recorded without being downloaded
- Configurable response-size guard and SSL verification enabled by default
- Optional Playwright fallback when an HTML response contains no ordinary links
- Partial-result export during graceful shutdown

## Requirements

- Python 3.11 or newer
- Network access to the target website
- Playwright and Chromium only when JavaScript rendering is enabled

## Installation

```bash
git clone <repository-url>
cd website-url-crawler

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Windows PowerShell activation and environment-file copy:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` if desired, then run:

```bash
python main.py https://example.com
```

## Usage

The positional CLI URL overrides `START_URL` from `.env`. Without a positional
argument, `START_URL` is required.

```bash
python main.py
python main.py https://example.com
python main.py https://example.com --max-pages 500
python main.py https://example.com --depth 5
python main.py https://example.com --concurrency 3 --output output/example
python main.py --help
```

Run the included unit and local integration tests without contacting a public site:

```bash
python -m unittest discover -v
```

## Output files

Every run rewrites the configured output files:

```text
output/
├── urls.txt             # all unique discovered internal URLs
├── pages.csv            # HTML response metadata (incl. page title)
├── content.jsonl        # one JSON object per crawled page: url, title, content
├── files.csv            # file/non-HTML URLs and available metadata
├── external_urls.csv    # links outside the allowed domain boundary
├── broken_urls.csv      # HTTP 400+ and request failures
├── redirects.csv        # every unique redirect hop
└── stats.json           # aggregate crawl statistics
```

`pages.csv` contains `url`, `title`, `status_code`, `content_type`, `source_url`,
`depth`, and `final_url`. Detail outputs also retain discovery timestamps, response
times, and error messages where relevant.

`content.jsonl` holds the readable content of every successfully crawled HTML page,
one JSON object per line (`{"url": ..., "title": ..., "content": ...}`) — a
convenient format for indexing, search, or feeding into other tools. `<script>`,
`<style>`, `<nav>`, `<header>`, `<footer>`, and `<aside>` tags are stripped before
extraction, and text is taken from `<main>`/`<article>` when present, otherwise
`<body>`. Sites that build menus/boilerplate from plain `<div>`s instead of those
semantic tags may still have some of that text mixed into `content`.

## Configuration

| Variable | Default | Meaning |
|---|---:|---|
| `START_URL` | `https://example.com` | URL used when no CLI URL is supplied |
| `REQUEST_TIMEOUT` | `15` | Total request timeout in seconds |
| `MAX_RETRIES` | `3` | Retries after network or retryable HTTP errors |
| `RETRY_BACKOFF` | `0.5` | Base exponential retry delay in seconds |
| `MAX_PAGES` | `10000` | Maximum URLs scheduled for HTTP requests |
| `MAX_DEPTH` | `20` | Maximum HTML link depth |
| `MAX_CONCURRENCY` | `5` | Concurrent crawler workers/connections |
| `CRAWL_DELAY` | `0.1` | Global minimum interval between requests |
| `USER_AGENT` | `WebsiteURLCrawler/1.0` | HTTP and robots user agent |
| `ALLOW_SUBDOMAINS` | `false` | Allow hosts below the starting hostname |
| `KEEP_QUERY_PARAMS` | `false` | Preserve query strings during normalization |
| `RESPECT_ROBOTS_TXT` | `true` | Apply robots allow/disallow rules |
| `ENABLE_SITEMAP` | `true` | Discover and recursively parse sitemaps |
| `ENABLE_PLAYWRIGHT` | `false` | Render linkless HTML with Chromium |
| `VERIFY_SSL` | `true` | Verify TLS certificates |
| `MAX_RESPONSE_BYTES` | `5000000` | Maximum decompressed body read per response |
| `OUTPUT_DIR` | `output` | Result directory |

The delay is global rather than per worker, keeping aggregate request rate polite.
robots.txt is always checked for sitemap directives; its crawl rules are enforced
only when `RESPECT_ROBOTS_TXT=true`.

## Optional Playwright installation

Playwright is deliberately absent from the core dependencies. Install it only if
the target requires JavaScript rendering:

```bash
pip install "playwright>=1.46,<2.0"
playwright install chromium
```

Then set `ENABLE_PLAYWRIGHT=true`. The fallback runs only on successful HTML pages
where the normal response yields no `<a href>` links.

## Known limitations

- The crawler does not execute forms, click buttons, authenticate, or bypass bot protection.
- Query removal can merge semantically distinct URLs; enable `KEEP_QUERY_PARAMS` when necessary.
- File-like URLs with no recognizable extension require one HTTP request before their content type is known.
- Sitemap loading is sequential and shares the global rate limiter to remain polite.
- robots rules are evaluated using Python's standard `urllib.robotparser`; non-standard directives may differ from a search engine's interpretation.
- Very large pages/sitemaps are rejected by `MAX_RESPONSE_BYTES` and recorded only when they are part of the normal crawl queue.
