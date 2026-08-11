#!/usr/bin/env python3
"""Collect technical evidence for an AdSense readiness audit.

This script intentionally does not score or approve a site. Its output is a bounded,
same-origin crawl that a human or agent must interpret against current Google policy.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import deque
from datetime import datetime, timezone
from html.parser import HTMLParser
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urldefrag, urljoin, urlsplit, urlunsplit
from urllib.request import Request, urlopen
from urllib.robotparser import RobotFileParser


USER_AGENT = "Mozilla/5.0 (compatible; AdSenseReadinessAudit/1.0; local-policy-audit)"
MAX_RESPONSE_BYTES = 2_000_000
CLOUDFLARE_ERROR_STATUSES = frozenset(range(520, 527))
SELECTED_RESPONSE_HEADERS = (
    "server",
    "cf-ray",
    "cf-cache-status",
    "cf-mitigated",
    "content-security-policy",
    "x-robots-tag",
    "retry-after",
)
SKIP_EXTENSIONS = {
    ".7z", ".avi", ".css", ".csv", ".doc", ".docx", ".epub", ".gif",
    ".gz", ".ico", ".jpeg", ".jpg", ".js", ".json", ".m4a", ".mkv",
    ".mov", ".mp3", ".mp4", ".mpeg", ".pdf", ".png", ".ppt", ".pptx",
    ".rar", ".rss", ".svg", ".tar", ".tsv", ".txt", ".wav", ".webm",
    ".webp", ".woff", ".woff2", ".xls", ".xlsx", ".xml", ".zip",
}


def selected_headers(headers: Any) -> dict[str, str]:
    return {
        name: value
        for name in SELECTED_RESPONSE_HEADERS
        if (value := headers.get(name)) is not None
    }
TRUST_PATTERNS = {
    "privacy": ("privacy", "隐私", "私隱", "プライバシー"),
    "about": ("about", "关于", "關於", "简介", "簡介", "私たち"),
    "contact": ("contact", "联系", "聯絡", "联系我们", "聯繫我們", "お問い合わせ"),
    "terms": ("terms", "tos", "条款", "條款", "利用規約"),
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def normalize_input_url(value: str) -> str:
    value = value.strip()
    if not re.match(r"^https?://", value, re.I):
        value = "https://" + value
    parts = urlsplit(value)
    if not parts.hostname:
        raise ValueError("URL must include a hostname")
    return urlunsplit((parts.scheme.lower(), parts.netloc, parts.path or "/", parts.query, ""))


def normalize_link(base_url: str, href: str) -> str | None:
    href = (href or "").strip()
    if not href or href.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
        return None
    joined = urldefrag(urljoin(base_url, href))[0]
    parts = urlsplit(joined)
    if parts.scheme.lower() not in {"http", "https"} or not parts.hostname:
        return None
    path = parts.path or "/"
    return urlunsplit((parts.scheme.lower(), parts.netloc, path, parts.query, ""))


def looks_like_page(url: str) -> bool:
    path = urlsplit(url).path.lower()
    return not any(path.endswith(ext) for ext in SKIP_EXTENSIONS)


def fetch(url: str, timeout: float) -> dict[str, Any]:
    request = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,text/plain;q=0.9,*/*;q=0.2",
        },
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read(MAX_RESPONSE_BYTES + 1)
            truncated = len(body) > MAX_RESPONSE_BYTES
            if truncated:
                body = body[:MAX_RESPONSE_BYTES]
            content_type = response.headers.get_content_type()
            charset = response.headers.get_content_charset() or "utf-8"
            try:
                text = body.decode(charset, errors="replace")
            except LookupError:
                text = body.decode("utf-8", errors="replace")
            return {
                "requested_url": url,
                "final_url": response.geturl(),
                "status": response.status,
                "content_type": content_type,
                "headers": selected_headers(response.headers),
                "text": text,
                "truncated": truncated,
                "error": None,
            }
    except HTTPError as exc:
        body = exc.read(100_000)
        charset = exc.headers.get_content_charset() or "utf-8"
        try:
            text = body.decode(charset, errors="replace")
        except LookupError:
            text = body.decode("utf-8", errors="replace")
        return {
            "requested_url": url,
            "final_url": exc.geturl(),
            "status": exc.code,
            "content_type": exc.headers.get_content_type(),
            "headers": selected_headers(exc.headers),
            "text": text,
            "truncated": False,
            "error": f"HTTP {exc.code}",
        }
    except (URLError, TimeoutError, OSError) as exc:
        return {
            "requested_url": url,
            "final_url": url,
            "status": None,
            "content_type": None,
            "headers": {},
            "text": "",
            "truncated": False,
            "error": str(getattr(exc, "reason", exc)),
        }


def cloudflare_response_evidence(response: dict[str, Any]) -> dict[str, Any]:
    headers = response.get("headers", {})
    status = response.get("status")
    server = headers.get("server", "")
    cf_ray = headers.get("cf-ray", "")
    cf_cache_status = headers.get("cf-cache-status", "")
    cf_mitigated = headers.get("cf-mitigated", "")
    markers: list[str] = []
    if "cloudflare" in server.casefold():
        markers.append("server=cloudflare")
    if cf_ray:
        markers.append("cf-ray")
    if cf_cache_status:
        markers.append("cf-cache-status")
    if cf_mitigated:
        markers.append("cf-mitigated")
    if status in CLOUDFLARE_ERROR_STATUSES:
        markers.append(f"cloudflare-52x-status={status}")
    csp = headers.get("content-security-policy", "")
    return {
        "detected": bool(markers),
        "detection_markers": markers,
        "server": server or None,
        "cf_ray": cf_ray or None,
        "cf_cache_status": cf_cache_status or None,
        "cf_mitigated": cf_mitigated or None,
        "challenge_detected": cf_mitigated.casefold() == "challenge",
        "cloudflare_error_status": status if status in CLOUDFLARE_ERROR_STATUSES else None,
        "content_security_policy": csp[:4000] or None,
        "interpretation_note": (
            "Cloudflare use is not an AdSense issue by itself. Challenge, error, cache, CSP, WAF, bot, redirect, and origin findings require outcome-based review."
        ),
    }


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title_parts: list[str] = []
        self.text_parts: list[str] = []
        self.links: list[dict[str, str]] = []
        self.scripts: list[str] = []
        self.lang = ""
        self.canonical = ""
        self.robots = ""
        self.h1_count = 0
        self.main_count = 0
        self.article_count = 0
        self._title_depth = 0
        self._hidden_depth = 0
        self._anchor_href: str | None = None
        self._anchor_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        values = {key.lower(): value or "" for key, value in attrs}
        if tag == "script":
            self.scripts.append(values.get("src", ""))
        if tag == "html":
            self.lang = values.get("lang", "")
        elif tag == "title":
            self._title_depth += 1
        elif tag in {"script", "style", "noscript", "svg", "template"}:
            self._hidden_depth += 1
        elif tag == "h1":
            self.h1_count += 1
        elif tag == "main":
            self.main_count += 1
        elif tag == "article":
            self.article_count += 1
        elif tag == "meta" and values.get("name", "").lower() in {"robots", "googlebot"}:
            self.robots = " ".join(filter(None, (self.robots, values.get("content", ""))))
        elif tag == "link" and "canonical" in values.get("rel", "").lower().split():
            self.canonical = values.get("href", "")
        if tag == "a":
            self._anchor_href = values.get("href", "")
            self._anchor_text = []

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "title" and self._title_depth:
            self._title_depth -= 1
        elif tag in {"script", "style", "noscript", "svg", "template"} and self._hidden_depth:
            self._hidden_depth -= 1
        if tag == "a" and self._anchor_href is not None:
            self.links.append({"href": self._anchor_href, "text": " ".join(self._anchor_text).strip()})
            self._anchor_href = None
            self._anchor_text = []

    def handle_data(self, data: str) -> None:
        cleaned = " ".join(data.split())
        if not cleaned:
            return
        if self._title_depth:
            self.title_parts.append(cleaned)
        if self._anchor_href is not None:
            self._anchor_text.append(cleaned)
        if not self._hidden_depth:
            self.text_parts.append(cleaned)


def approximate_content_units(text: str) -> int:
    latin_tokens = re.findall(r"[A-Za-z0-9]+(?:['’-][A-Za-z0-9]+)*", text)
    cjk_chars = re.findall(r"[\u3400-\u4dbf\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af]", text)
    return len(latin_tokens) + len(cjk_chars)


def classify_trust_link(url: str, label: str) -> list[str]:
    haystack = (urlsplit(url).path + " " + label).casefold()
    return [kind for kind, patterns in TRUST_PATTERNS.items() if any(p.casefold() in haystack for p in patterns)]


def page_record(response: dict[str, Any], parser: PageParser | None) -> dict[str, Any]:
    record: dict[str, Any] = {
        "url": response["requested_url"],
        "final_url": response["final_url"],
        "status": response["status"],
        "content_type": response["content_type"],
        "error": response["error"],
        "truncated": response["truncated"],
        "cloudflare": cloudflare_response_evidence(response),
    }
    if parser is None:
        return record
    visible_text = " ".join(parser.text_parts)
    record.update(
        {
            "title": " ".join(parser.title_parts).strip(),
            "html_lang": parser.lang,
            "robots_meta": parser.robots,
            "noindex": "noindex" in parser.robots.casefold(),
            "canonical": normalize_link(response["final_url"], parser.canonical) if parser.canonical else None,
            "approx_content_units": approximate_content_units(visible_text),
            "h1_count": parser.h1_count,
            "main_elements": parser.main_count,
            "article_elements": parser.article_count,
            "link_count": len(parser.links),
            "adsense_script_detected": any(
                "pagead2.googlesyndication.com/pagead/js/adsbygoogle.js" in src for src in parser.scripts
            ) or "adsbygoogle" in response["text"],
        }
    )
    return record


def robots_evidence(origin: str, start_url: str, timeout: float) -> dict[str, Any]:
    url = origin + "/robots.txt"
    response = fetch(url, timeout)
    result: dict[str, Any] = {
        "url": url,
        "status": response["status"],
        "error": response["error"],
        "star_allows_start": None,
        "mediapartners_google_allows_start": None,
        "google_display_ads_bot_allows_start": None,
        "cloudflare": cloudflare_response_evidence(response),
    }
    if response["status"] == 200:
        parser = RobotFileParser()
        parser.set_url(url)
        parser.parse(response["text"].splitlines())
        result["star_allows_start"] = parser.can_fetch("*", start_url)
        result["mediapartners_google_allows_start"] = parser.can_fetch("Mediapartners-Google", start_url)
        result["google_display_ads_bot_allows_start"] = parser.can_fetch("Google-Display-Ads-Bot", start_url)
    elif response["status"] == 404:
        result["star_allows_start"] = True
        result["mediapartners_google_allows_start"] = True
        result["google_display_ads_bot_allows_start"] = True
    return result


def ads_txt_evidence(origin: str, timeout: float) -> dict[str, Any]:
    url = origin + "/ads.txt"
    response = fetch(url, timeout)
    google_entries: list[str] = []
    if response["status"] == 200:
        for line in response["text"].splitlines():
            stripped = line.strip()
            if re.match(r"^google\.com\s*,", stripped, re.I):
                google_entries.append(stripped)
    return {
        "url": url,
        "status": response["status"],
        "content_type": response["content_type"],
        "error": response["error"],
        "google_entries": google_entries,
        "cloudflare": cloudflare_response_evidence(response),
        "policy_note": "ads.txt is not universally mandatory, but Google strongly recommends it; existing files must authorize the publisher.",
    }


def audit_site(start_url: str, max_pages: int, timeout: float) -> dict[str, Any]:
    first = fetch(start_url, timeout)
    final_start = first["final_url"]
    parts = urlsplit(final_start)
    origin = urlunsplit((parts.scheme, parts.netloc, "", "", "")) if parts.hostname else ""
    root_netloc = parts.netloc.casefold()

    audit: dict[str, Any] = {
        "generated_at": utc_now(),
        "input_url": start_url,
        "final_start_url": final_start,
        "scope": {
            "same_origin_only": True,
            "max_pages": max_pages,
            "user_agent": USER_AGENT,
            "max_response_bytes": MAX_RESPONSE_BYTES,
        },
        "technical": {},
        "pages": [],
        "trust_link_candidates": {key: [] for key in TRUST_PATTERNS},
        "broken_or_failed_internal_urls": [],
        "limitations": [
            "This is a bounded HTTP crawl, not a Google approval prediction.",
            "JavaScript-rendered content, consent states, mobile layout, originality, legality, copyright, traffic quality, and account data require separate review.",
            "Approximate content units combine Latin-like tokens and CJK characters and are not a Google threshold.",
        ],
    }

    if not parts.hostname:
        audit["technical"]["start"] = page_record(first, None)
        return audit

    audit["technical"]["start"] = {
        "requested_url": start_url,
        "final_url": final_start,
        "status": first["status"],
        "content_type": first["content_type"],
        "error": first["error"],
        "https_final": parts.scheme.lower() == "https",
    }
    audit["technical"]["cloudflare"] = {
        "first_response": cloudflare_response_evidence(first),
        "challenge_urls": [],
        "cloudflare_error_urls": [],
        "manual_checks": [
            "Review actual Mediapartners-Google and Google-Display-Ads-Bot requests in AdSense crawler reports and Cloudflare Security Events or logs; do not trust a spoofed user-agent test as proof.",
            "Review DNS, SSL/TLS mode, WAF and bot rules, rate limiting, Access, geographic or IP rules, Workers, redirects, cache rules, and origin health when Cloudflare is detected or declared.",
        ],
    }
    audit["technical"]["robots"] = robots_evidence(origin, final_start, timeout)
    audit["technical"]["ads_txt"] = ads_txt_evidence(origin, timeout)

    if parts.scheme.lower() == "https":
        http_origin = urlunsplit(("http", parts.netloc, "/", "", ""))
        http_probe = fetch(http_origin, timeout)
        audit["technical"]["http_to_https"] = {
            "requested_url": http_origin,
            "status": http_probe["status"],
            "final_url": http_probe["final_url"],
            "redirects_to_https": urlsplit(http_probe["final_url"]).scheme.lower() == "https",
            "error": http_probe["error"],
        }

    queue: deque[str] = deque([final_start])
    queued = {final_start}
    visited: set[str] = set()
    prefetched = {final_start: first}
    trust_seen = {key: set() for key in TRUST_PATTERNS}

    while queue and len(visited) < max_pages:
        current = queue.popleft()
        if current in visited:
            continue
        visited.add(current)
        response = prefetched.pop(current, None) or fetch(current, timeout)
        parser: PageParser | None = None
        is_html = response["content_type"] in {"text/html", "application/xhtml+xml"}
        if response["status"] == 200 and is_html:
            parser = PageParser()
            try:
                parser.feed(response["text"])
            except Exception as exc:  # HTMLParser should be forgiving; retain partial evidence.
                response["error"] = f"HTML parse warning: {exc}"

        record = page_record(response, parser)
        audit["pages"].append(record)
        if response["status"] is None or (isinstance(response["status"], int) and response["status"] >= 400):
            audit["broken_or_failed_internal_urls"].append(
                {"url": current, "status": response["status"], "error": response["error"]}
            )

        if parser is None:
            continue
        base = response["final_url"]
        for raw_link in parser.links:
            normalized = normalize_link(base, raw_link["href"])
            if not normalized or urlsplit(normalized).netloc.casefold() != root_netloc:
                continue
            for kind in classify_trust_link(normalized, raw_link["text"]):
                if normalized not in trust_seen[kind]:
                    trust_seen[kind].add(normalized)
                    audit["trust_link_candidates"][kind].append(normalized)
            if looks_like_page(normalized) and normalized not in queued and len(queued) < max_pages * 8:
                queued.add(normalized)
                queue.append(normalized)

    audit["scope"].update(
        {
            "pages_fetched": len(audit["pages"]),
            "same_origin_page_urls_discovered": len(queued),
            "crawl_truncated_by_page_limit": bool(queue),
        }
    )
    audit["technical"]["adsense_script_pages"] = sum(
        1 for page in audit["pages"] if page.get("adsense_script_detected")
    )
    audit["technical"]["cloudflare"]["challenge_urls"] = [
        page.get("final_url") or page.get("url")
        for page in audit["pages"]
        if page.get("cloudflare", {}).get("challenge_detected")
    ]
    audit["technical"]["cloudflare"]["cloudflare_error_urls"] = [
        {
            "url": page.get("final_url") or page.get("url"),
            "status": page.get("cloudflare", {}).get("cloudflare_error_status"),
        }
        for page in audit["pages"]
        if page.get("cloudflare", {}).get("cloudflare_error_status") is not None
    ]
    return audit


def md_escape(value: Any) -> str:
    if value is None:
        return "unknown"
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_markdown(audit: dict[str, Any]) -> str:
    technical = audit.get("technical", {})
    start = technical.get("start", {})
    robots = technical.get("robots", {})
    ads_txt = technical.get("ads_txt", {})
    http_probe = technical.get("http_to_https", {})
    cloudflare = technical.get("cloudflare", {})
    first_cloudflare = cloudflare.get("first_response", {})
    scope = audit.get("scope", {})
    lines = [
        "# AdSense technical site probe",
        "",
        f"Generated: {audit.get('generated_at')}",
        f"Input: {audit.get('input_url')}",
        f"Final start URL: {audit.get('final_start_url')}",
        f"Coverage: {scope.get('pages_fetched', 0)} fetched / {scope.get('same_origin_page_urls_discovered', 0)} discovered; page-limit truncated: {scope.get('crawl_truncated_by_page_limit', False)}",
        "",
        "## Technical signals",
        "",
        "| Signal | Value |",
        "|---|---|",
        f"| Start status | {md_escape(start.get('status'))} |",
        f"| Final HTTPS | {md_escape(start.get('https_final'))} |",
        f"| HTTP redirects to HTTPS | {md_escape(http_probe.get('redirects_to_https'))} |",
        f"| robots.txt status | {md_escape(robots.get('status'))} |",
        f"| `*` allowed on start URL | {md_escape(robots.get('star_allows_start'))} |",
        f"| `Mediapartners-Google` allowed on start URL | {md_escape(robots.get('mediapartners_google_allows_start'))} |",
        f"| `Google-Display-Ads-Bot` allowed on start URL | {md_escape(robots.get('google_display_ads_bot_allows_start'))} |",
        f"| ads.txt status | {md_escape(ads_txt.get('status'))} |",
        f"| Google ads.txt entries | {len(ads_txt.get('google_entries', []))} |",
        f"| Pages with AdSense script signal | {technical.get('adsense_script_pages', 0)} |",
        "",
        "## Cloudflare/CDN signals",
        "",
        "| Signal | Value |",
        "|---|---|",
        f"| Cloudflare detected on first response | {md_escape(first_cloudflare.get('detected'))} |",
        f"| Detection markers | {md_escape(', '.join(first_cloudflare.get('detection_markers', [])))} |",
        f"| CF-Ray | {md_escape(first_cloudflare.get('cf_ray'))} |",
        f"| CF-Cache-Status | {md_escape(first_cloudflare.get('cf_cache_status'))} |",
        f"| Challenge on first response | {md_escape(first_cloudflare.get('challenge_detected'))} |",
        f"| Cloudflare error status on first response | {md_escape(first_cloudflare.get('cloudflare_error_status'))} |",
        f"| Challenged fetched URLs | {len(cloudflare.get('challenge_urls', []))} |",
        f"| Fetched URLs with Cloudflare 520-526 | {len(cloudflare.get('cloudflare_error_urls', []))} |",
        "",
        "## Fetched pages",
        "",
        "| Status | URL | Title | Lang | Approx. content units | H1 | Noindex | AdSense signal |",
        "|---:|---|---|---|---:|---:|---|---|",
    ]
    for page in audit.get("pages", []):
        lines.append(
            "| {status} | {url} | {title} | {lang} | {units} | {h1} | {noindex} | {adsense} |".format(
                status=md_escape(page.get("status")),
                url=md_escape(page.get("final_url") or page.get("url")),
                title=md_escape(page.get("title", "")),
                lang=md_escape(page.get("html_lang", "")),
                units=md_escape(page.get("approx_content_units")),
                h1=md_escape(page.get("h1_count")),
                noindex=md_escape(page.get("noindex")),
                adsense=md_escape(page.get("adsense_script_detected")),
            )
        )

    lines.extend(["", "## Trust-page link candidates", ""])
    for kind, urls in audit.get("trust_link_candidates", {}).items():
        lines.append(f"- {kind}: {', '.join(urls) if urls else 'none detected'}")

    failed = audit.get("broken_or_failed_internal_urls", [])
    lines.extend(["", "## Broken or failed fetched internal URLs", ""])
    if failed:
        for item in failed:
            lines.append(f"- {item.get('status') or 'failed'} — {item.get('url')} — {item.get('error') or ''}")
    else:
        lines.append("- None among fetched URLs.")

    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in audit.get("limitations", []))
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect bounded technical evidence for an AdSense site-readiness audit.")
    parser.add_argument("url", help="Site URL, with or without https://")
    parser.add_argument("--max-pages", type=int, default=30, help="Maximum same-origin pages to fetch (1-100; default: 30)")
    parser.add_argument("--timeout", type=float, default=12.0, help="Per-request timeout in seconds (3-60; default: 12)")
    parser.add_argument("--format", choices=("json", "markdown"), default="json", help="Output format (default: json)")
    args = parser.parse_args(argv)
    if not 1 <= args.max_pages <= 100:
        parser.error("--max-pages must be between 1 and 100")
    if not 3 <= args.timeout <= 60:
        parser.error("--timeout must be between 3 and 60")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        start_url = normalize_input_url(args.url)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    audit = audit_site(start_url, args.max_pages, args.timeout)
    if args.format == "markdown":
        sys.stdout.write(render_markdown(audit))
    else:
        json.dump(audit, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
