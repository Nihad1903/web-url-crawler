from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.robotparser import RobotFileParser

_SITEMAP_RE = re.compile(r"^\s*sitemap\s*:\s*(\S+)\s*$", re.IGNORECASE | re.MULTILINE)


@dataclass(slots=True)
class RobotsPolicy:
    parser: RobotFileParser | None
    sitemap_urls: tuple[str, ...]

    def allowed(self, user_agent: str, url: str) -> bool:
        return self.parser is None or self.parser.can_fetch(user_agent, url)


def parse_robots(url: str, text: str, respect_rules: bool) -> RobotsPolicy:
    parser: RobotFileParser | None = None
    if respect_rules:
        parser = RobotFileParser()
        parser.set_url(url)
        parser.parse(text.splitlines())
    return RobotsPolicy(parser=parser, sitemap_urls=tuple(_SITEMAP_RE.findall(text)))
