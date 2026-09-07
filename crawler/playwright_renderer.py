from __future__ import annotations

from typing import Any


class PlaywrightRenderer:
    """Lazy optional renderer; Playwright is imported only when enabled."""

    def __init__(self, timeout_seconds: float, user_agent: str) -> None:
        self.timeout_ms = int(timeout_seconds * 1000)
        self.user_agent = user_agent
        self._playwright: Any = None
        self._browser: Any = None

    async def __aenter__(self) -> "PlaywrightRenderer":
        try:
            from playwright.async_api import async_playwright
        except ImportError as exc:
            raise RuntimeError(
                "ENABLE_PLAYWRIGHT=true, but Playwright is not installed. "
                "Run: pip install playwright && playwright install chromium"
            ) from exc
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=True)
        return self

    async def __aexit__(self, *_: object) -> None:
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

    async def render(self, url: str) -> str:
        context = await self._browser.new_context(user_agent=self.user_agent)
        page = await context.new_page()
        try:
            await page.goto(url, wait_until="networkidle", timeout=self.timeout_ms)
            return await page.content()
        finally:
            await context.close()
