"""Shared HTTP + text helpers for all scraper sources."""
import html
import re
import time

import requests

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

_session = requests.Session()
_session.headers["User-Agent"] = UA

_last_call: dict[str, float] = {}


def _throttle(host: str, min_gap: float = 1.0):
    now = time.time()
    wait = _last_call.get(host, 0) + min_gap - now
    if wait > 0:
        time.sleep(wait)
    _last_call[host] = time.time()


def get(url: str, *, min_gap: float = 1.0, timeout: int = 20, **kw) -> requests.Response | None:
    """GET with per-host throttling and one retry. Returns None on failure."""
    host = url.split("/")[2]
    for attempt in (1, 2):
        _throttle(host, min_gap)
        try:
            r = _session.get(url, timeout=timeout, **kw)
            if r.status_code == 200:
                return r
            if r.status_code in (404, 410):
                return None
            if r.status_code == 429:
                time.sleep(10 * attempt)
                continue
            return None
        except requests.RequestException:
            time.sleep(2 * attempt)
    return None


def get_json(url: str, **kw):
    r = get(url, **kw)
    if r is None:
        return None
    try:
        return r.json()
    except ValueError:
        return None


def post_json(url: str, payload: dict, *, timeout: int = 20, headers: dict | None = None):
    host = url.split("/")[2]
    _throttle(host)
    try:
        r = _session.post(url, json=payload, timeout=timeout, headers=headers or {})
        return r.json() if r.status_code == 200 else None
    except (requests.RequestException, ValueError):
        return None


def strip_html(text: str, limit: int = 4000) -> str:
    """HTML → plain text, whitespace-collapsed, truncated."""
    if not text:
        return ""
    text = html.unescape(text)
    text = re.sub(r"<(br|/p|/li|/div|/h[1-6])[^>]*>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text).strip()
    return text[:limit]
