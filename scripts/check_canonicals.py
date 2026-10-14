#!/usr/bin/env python3
"""Check that every sitemap URL has a matching canonical (and og:url) tag.

Usage: python3 scripts/check_canonicals.py          # check local files
       python3 scripts/check_canonicals.py --live   # also fetch each URL from the live site
"""
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOST = "https://brianplescher.com"
NS = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}


def local_file(url):
    path = url[len(HOST):] or "/"
    return ROOT / (path.lstrip("/") + "index.html" if path.endswith("/") else path.lstrip("/"))


def tag(html, pattern):
    m = re.search(pattern, html)
    return m.group(1) if m else None


def check_html(url, html, where):
    errors = []
    canonical = tag(html, r'<link rel="canonical" href="([^"]*)"')
    og_url = tag(html, r'<meta property="og:url" content="([^"]*)"')
    if canonical != url:
        errors.append(f"{where}: canonical {canonical!r} != {url!r}")
    if og_url is not None and og_url != url:
        errors.append(f"{where}: og:url {og_url!r} != {url!r}")
    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        try:
            json.loads(block)
        except json.JSONDecodeError as exc:
            errors.append(f"{where}: invalid JSON-LD ({exc})")
    return errors


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def main():
    live = "--live" in sys.argv
    urls = [loc.text.strip() for loc in ET.parse(ROOT / "sitemap.xml").findall(".//s:loc", NS)]
    errors = []
    for url in urls:
        f = local_file(url)
        if not f.exists():
            errors.append(f"{url}: no local file {f.relative_to(ROOT)}")
            continue
        errors += check_html(url, f.read_text(), str(f.relative_to(ROOT)))
        if live:
            opener = urllib.request.build_opener(NoRedirect)
            try:
                with opener.open(url, timeout=15) as resp:
                    errors += check_html(url, resp.read().decode(), f"live {url}")
            except urllib.error.HTTPError as exc:
                errors.append(f"live {url}: HTTP {exc.code} {exc.headers.get('Location', '')}".rstrip())

    listed = {local_file(u).resolve() for u in urls}
    tracked = subprocess.check_output(["git", "ls-files", "*.html"], cwd=ROOT, text=True).split()
    for name in tracked:
        if name.startswith("."):
            continue
        p = (ROOT / name).resolve()
        if p not in listed and 'name="robots" content="noindex' not in p.read_text():
            errors.append(f"{name}: indexable page missing from sitemap.xml")

    for e in errors:
        print("FAIL", e)
    print(f"{len(urls)} sitemap URLs checked{' (live)' if live else ''}, {len(errors)} problem(s)")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
