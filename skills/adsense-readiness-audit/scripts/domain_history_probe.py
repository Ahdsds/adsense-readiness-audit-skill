#!/usr/bin/env python3
"""Collect bounded, read-only evidence about a domain's current state and archived use."""

from __future__ import annotations

import argparse
import json
import socket
import ssl
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from html.parser import HTMLParser
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener, urlopen


USER_AGENT = "AdSenseReadinessDomainHistoryProbe/1.1 (+read-only audit)"
MAX_RESPONSE_BYTES = 2_000_000
IANA_RDAP_BOOTSTRAP = "https://data.iana.org/rdap/dns.json"
WAYBACK_CDX = "https://web.archive.org/cdx/search/cdx"
SPECIAL_USE_NAMES = {
    "alt",
    "example",
    "example.com",
    "example.net",
    "example.org",
    "home.arpa",
    "invalid",
    "local",
    "localhost",
    "onion",
    "test",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def normalize_domain(value: str) -> str:
    candidate = value.strip()
    if not candidate:
        raise ValueError("domain is empty")
    parsed = urlsplit(candidate if "://" in candidate else "//" + candidate)
    hostname = parsed.hostname
    if not hostname:
        raise ValueError("could not parse a hostname")
    hostname = hostname.rstrip(".").casefold()
    try:
        ascii_name = hostname.encode("idna").decode("ascii")
    except UnicodeError as exc:
        raise ValueError(f"invalid internationalized domain: {exc}") from exc
    if "." not in ascii_name or any(not label for label in ascii_name.split(".")):
        raise ValueError("provide a fully qualified domain name")
    return ascii_name


def special_use_classification(domain: str) -> dict[str, Any]:
    for name in sorted(SPECIAL_USE_NAMES, key=len, reverse=True):
        if domain == name or domain.endswith("." + name):
            example_domain = name in {"example.com", "example.net", "example.org"}
            return {
                "is_special_use": True,
                "matched_name": name,
                "production_ownership_blocker": True if example_domain else None,
                "note": (
                    "IANA says example domains are maintained for documentation, are unavailable for registration or transfer, and are not designed for production applications."
                    if example_domain
                    else "This name or a parent is in IANA's Special-Use Domain Names registry; read its referenced RFC before deciding whether it can be a public production site."
                ),
                "source": "https://www.iana.org/assignments/special-use-domain-names/special-use-domain-names.xhtml",
            }
    return {"is_special_use": False, "matched_name": None, "production_ownership_blocker": False}


def read_url(url: str, timeout: float, max_bytes: int = MAX_RESPONSE_BYTES) -> dict[str, Any]:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json,text/html,*/*;q=0.8"})
    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read(max_bytes + 1)
            truncated = len(body) > max_bytes
            body = body[:max_bytes]
            content_type = response.headers.get_content_type()
            charset = response.headers.get_content_charset() or "utf-8"
            try:
                text = body.decode(charset, errors="replace")
            except LookupError:
                text = body.decode("utf-8", errors="replace")
            return {
                "url": url,
                "final_url": response.geturl(),
                "status": response.status,
                "content_type": content_type,
                "text": text,
                "truncated": truncated,
                "error": None,
            }
    except HTTPError as exc:
        return {"url": url, "final_url": exc.geturl(), "status": exc.code, "content_type": None, "text": "", "truncated": False, "error": str(exc)}
    except (URLError, TimeoutError, OSError) as exc:
        return {"url": url, "final_url": url, "status": None, "content_type": None, "text": "", "truncated": False, "error": str(exc)}


class RecordingRedirectHandler(HTTPRedirectHandler):
    def __init__(self) -> None:
        super().__init__()
        self.history: list[dict[str, Any]] = []

    def redirect_request(self, req: Request, fp: Any, code: int, msg: str, headers: Any, newurl: str) -> Request | None:
        self.history.append({"status": code, "from": req.full_url, "to": newurl})
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def http_probe(url: str, timeout: float) -> dict[str, Any]:
    redirects = RecordingRedirectHandler()
    opener = build_opener(redirects)
    request = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with opener.open(request, timeout=timeout) as response:
            response.read(1024)
            return {"url": url, "status": response.status, "final_url": response.geturl(), "redirects": redirects.history, "error": None}
    except HTTPError as exc:
        return {"url": url, "status": exc.code, "final_url": exc.geturl(), "redirects": redirects.history, "error": str(exc)}
    except (URLError, TimeoutError, OSError) as exc:
        return {"url": url, "status": None, "final_url": url, "redirects": redirects.history, "error": str(exc)}


def resolve_addresses(domain: str) -> dict[str, Any]:
    try:
        records = socket.getaddrinfo(domain, 443, type=socket.SOCK_STREAM)
        addresses = sorted({item[4][0] for item in records})
        return {"addresses": addresses, "error": None}
    except OSError as exc:
        return {"addresses": [], "error": str(exc)}


def tls_probe(domain: str, timeout: float) -> dict[str, Any]:
    context = ssl.create_default_context()
    try:
        with socket.create_connection((domain, 443), timeout=timeout) as raw:
            with context.wrap_socket(raw, server_hostname=domain) as secure:
                cert = secure.getpeercert()
                subject = {key: value for group in cert.get("subject", ()) for key, value in group}
                issuer = {key: value for group in cert.get("issuer", ()) for key, value in group}
                sans = [value for kind, value in cert.get("subjectAltName", ()) if kind == "DNS"]
                return {
                    "valid_now_and_hostname_matched": True,
                    "protocol": secure.version(),
                    "subject_common_name": subject.get("commonName"),
                    "issuer_common_name": issuer.get("commonName"),
                    "not_before": cert.get("notBefore"),
                    "not_after": cert.get("notAfter"),
                    "dns_names_sample": sans[:20],
                    "error": None,
                }
    except (ssl.SSLError, socket.timeout, OSError) as exc:
        return {"valid_now_and_hostname_matched": False, "error": str(exc)}


def rdap_candidates(domain: str) -> list[str]:
    labels = domain.split(".")
    return [".".join(labels[index:]) for index in range(max(0, len(labels) - 5), len(labels) - 1)]


def compact_rdap(data: dict[str, Any], queried_domain: str, endpoint: str) -> dict[str, Any]:
    events = [
        {"action": item.get("eventAction"), "date": item.get("eventDate")}
        for item in data.get("events", [])
        if isinstance(item, dict)
    ]
    nameservers = [item.get("ldhName") or item.get("unicodeName") for item in data.get("nameservers", []) if isinstance(item, dict)]
    registrar_handles = [
        entity.get("handle")
        for entity in data.get("entities", [])
        if isinstance(entity, dict) and "registrar" in entity.get("roles", [])
    ]
    return {
        "queried_domain": queried_domain,
        "endpoint": endpoint,
        "ldh_name": data.get("ldhName"),
        "unicode_name": data.get("unicodeName"),
        "handle": data.get("handle"),
        "status": data.get("status", []),
        "events": events,
        "nameservers": sorted(item for item in nameservers if item),
        "registrar_entity_handles": [item for item in registrar_handles if item],
        "secure_dns": data.get("secureDNS"),
        "notices": [item.get("title") for item in data.get("notices", []) if isinstance(item, dict) and item.get("title")],
        "interpretation_warning": "Current public RDAP data is not complete ownership history; registration dates can reflect the current lifecycle and redacted fields vary.",
    }


def rdap_probe(domain: str, timeout: float) -> dict[str, Any]:
    bootstrap_response = read_url(IANA_RDAP_BOOTSTRAP, timeout)
    if bootstrap_response["status"] != 200:
        return {"status": bootstrap_response["status"], "error": bootstrap_response["error"] or "IANA bootstrap unavailable"}
    try:
        bootstrap = json.loads(bootstrap_response["text"])
    except json.JSONDecodeError as exc:
        return {"status": None, "error": f"invalid IANA bootstrap JSON: {exc}"}

    tld = domain.rsplit(".", 1)[-1]
    services = bootstrap.get("services", [])
    bases: list[str] = []
    for entry in services:
        if isinstance(entry, list) and len(entry) == 2 and tld in [str(item).casefold() for item in entry[0]]:
            bases.extend(str(item) for item in entry[1])
    if not bases:
        return {"status": None, "error": f"no RDAP bootstrap service for .{tld}"}

    attempts: list[dict[str, Any]] = []
    for candidate in rdap_candidates(domain):
        for base in bases:
            endpoint = base.rstrip("/") + "/domain/" + quote(candidate, safe=".-")
            response = read_url(endpoint, timeout)
            attempts.append({"domain": candidate, "endpoint": endpoint, "status": response["status"]})
            if response["status"] == 200:
                try:
                    data = json.loads(response["text"])
                except json.JSONDecodeError as exc:
                    return {"status": 200, "error": f"invalid RDAP JSON: {exc}", "attempts": attempts}
                return {"status": 200, "result": compact_rdap(data, candidate, endpoint), "attempts": attempts}
    return {"status": None, "error": "no successful RDAP domain response", "attempts": attempts}


class SnapshotParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title_parts: list[str] = []
        self.text_parts: list[str] = []
        self.lang = ""
        self.description = ""
        self._title = 0
        self._hidden = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.casefold(): value or "" for key, value in attrs}
        tag = tag.casefold()
        if tag == "html":
            self.lang = values.get("lang", "")
        elif tag == "title":
            self._title += 1
        elif tag in {"script", "style", "noscript", "svg", "template"}:
            self._hidden += 1
        elif tag == "meta" and values.get("name", "").casefold() == "description":
            self.description = " ".join(values.get("content", "").split())

    def handle_endtag(self, tag: str) -> None:
        tag = tag.casefold()
        if tag == "title" and self._title:
            self._title -= 1
        elif tag in {"script", "style", "noscript", "svg", "template"} and self._hidden:
            self._hidden -= 1

    def handle_data(self, data: str) -> None:
        cleaned = " ".join(data.split())
        if not cleaned:
            return
        if self._title:
            self.title_parts.append(cleaned)
        if not self._hidden:
            self.text_parts.append(cleaned)


def evenly_sample(rows: list[list[str]], count: int) -> list[list[str]]:
    if count <= 0 or not rows:
        return []
    if len(rows) <= count:
        return rows
    indexes = sorted({round(index * (len(rows) - 1) / (count - 1)) for index in range(count)}) if count > 1 else {len(rows) - 1}
    return [rows[index] for index in indexes]


def wayback_probe(domain: str, count: int, timeout: float) -> dict[str, Any]:
    params = {
        "url": domain + "/",
        "matchType": "exact",
        "output": "json",
        "fl": "timestamp,original,statuscode,mimetype,digest",
        "filter": ["statuscode:200", "mimetype:text/html"],
        "collapse": "timestamp:6",
        "limit": "5000",
    }
    query_items: list[tuple[str, str]] = []
    for key, value in params.items():
        if isinstance(value, list):
            query_items.extend((key, item) for item in value)
        else:
            query_items.append((key, value))
    cdx_url = WAYBACK_CDX + "?" + urlencode(query_items)
    response = read_url(cdx_url, timeout)
    if response["status"] != 200:
        return {"cdx_url": cdx_url, "status": response["status"], "error": response["error"] or "CDX unavailable", "snapshots": []}
    try:
        payload = json.loads(response["text"])
    except json.JSONDecodeError as exc:
        return {"cdx_url": cdx_url, "status": 200, "error": f"invalid CDX JSON: {exc}", "snapshots": []}
    if not isinstance(payload, list) or len(payload) < 2:
        return {"cdx_url": cdx_url, "status": 200, "captures_returned": 0, "error": None, "snapshots": []}
    header = payload[0]
    rows = [row for row in payload[1:] if isinstance(row, list) and len(row) == len(header)]
    sampled = evenly_sample(rows, count)
    def fetch_snapshot(row: list[str]) -> dict[str, Any]:
        item = dict(zip(header, row))
        archive_url = f"https://web.archive.org/web/{item['timestamp']}id_/{item['original']}"
        archived = read_url(archive_url, timeout)
        record: dict[str, Any] = {
            "timestamp": item["timestamp"],
            "original_url": item["original"],
            "archive_url": archive_url,
            "fetch_status": archived["status"],
            "fetch_error": archived["error"],
        }
        if archived["status"] == 200 and archived["content_type"] in {"text/html", "application/xhtml+xml"}:
            parser = SnapshotParser()
            try:
                parser.feed(archived["text"])
            except Exception as exc:
                record["parse_warning"] = str(exc)
            visible = " ".join(parser.text_parts)
            record.update({
                "title": " ".join(parser.title_parts).strip(),
                "html_lang": parser.lang,
                "meta_description": parser.description[:300],
                "visible_text_sample": visible[:500],
            })
        return record

    if sampled:
        with ThreadPoolExecutor(max_workers=min(4, len(sampled))) as executor:
            snapshots = list(executor.map(fetch_snapshot, sampled))
    else:
        snapshots = []
    return {
        "cdx_url": cdx_url,
        "status": 200,
        "captures_returned": len(rows),
        "first_capture": rows[0][0] if rows else None,
        "last_capture": rows[-1][0] if rows else None,
        "sample_method": "evenly spaced across monthly-collapsed exact homepage captures",
        "snapshots": snapshots,
        "error": None,
    }


def audit_domain(domain: str, snapshots: int, timeout: float) -> dict[str, Any]:
    return {
        "generated_at": utc_now(),
        "input_domain": domain,
        "domain_classification": special_use_classification(domain),
        "dns_resolution": resolve_addresses(domain),
        "http": http_probe("http://" + domain + "/", timeout),
        "https": http_probe("https://" + domain + "/", timeout),
        "tls": tls_probe(domain, timeout),
        "rdap": rdap_probe(domain, timeout),
        "wayback": wayback_probe(domain, snapshots, timeout),
        "manual_checks": {
            "google_safe_browsing": "https://transparencyreport.google.com/safe-browsing/search?url=" + quote(domain, safe=""),
            "google_search_site_query": "https://www.google.com/search?q=" + quote("site:" + domain, safe=""),
            "search_console": ["Security issues", "Manual actions", "Pages and URL Inspection", "Links and Performance"],
        },
        "limitations": [
            "Domain age, a topic change, privacy protection, or a previous owner is not by itself an AdSense blocker.",
            "RDAP exposes current public registration data, not complete ownership or registration history.",
            "Wayback captures are incomplete and may be missing, excluded, broken, or redirected to a nearby capture; absence is not proof of no prior use.",
            "Archived content does not identify the current owner. Snapshot titles and text samples require human classification and corroboration.",
            "The probe does not query private reputation databases, prove safety, inspect Google account state, or predict approval.",
        ],
    }


def md(value: Any) -> str:
    if value is None:
        return "unknown"
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_markdown(audit: dict[str, Any]) -> str:
    http = audit["http"]
    https = audit["https"]
    tls = audit["tls"]
    rdap = audit["rdap"]
    rdap_result = rdap.get("result", {})
    wayback = audit["wayback"]
    classification = audit["domain_classification"]
    lines = [
        "# Domain history evidence probe",
        "",
        f"Generated: {audit['generated_at']}",
        f"Domain: {audit['input_domain']}",
        "",
        "## Current technical and registration signals",
        "",
        "| Signal | Value |",
        "|---|---|",
        f"| Resolved addresses | {md(', '.join(audit['dns_resolution'].get('addresses', [])) or audit['dns_resolution'].get('error'))} |",
        f"| IANA special-use match | {md(classification.get('matched_name') if classification.get('is_special_use') else False)} |",
        f"| Special-use note | {md(classification.get('note'))} |",
        f"| HTTP status / final URL | {md(http.get('status'))} / {md(http.get('final_url'))} |",
        f"| HTTP probe error | {md(http.get('error'))} |",
        f"| HTTPS status / final URL | {md(https.get('status'))} / {md(https.get('final_url'))} |",
        f"| HTTPS probe error | {md(https.get('error'))} |",
        f"| TLS valid now and hostname matched | {md(tls.get('valid_now_and_hostname_matched'))} |",
        f"| TLS issuer / expiry | {md(tls.get('issuer_common_name'))} / {md(tls.get('not_after'))} |",
        f"| TLS probe error | {md(tls.get('error'))} |",
        f"| RDAP queried domain | {md(rdap_result.get('queried_domain'))} |",
        f"| RDAP status values | {md(', '.join(rdap_result.get('status', [])))} |",
        f"| RDAP nameservers | {md(', '.join(rdap_result.get('nameservers', [])))} |",
        "",
        "### RDAP events",
        "",
    ]
    events = rdap_result.get("events", [])
    lines.extend(f"- {md(item.get('action'))}: {md(item.get('date'))}" for item in events)
    if not events:
        lines.append(f"- unavailable: {md(rdap.get('error'))}")

    lines.extend([
        "",
        "## Archived-use samples",
        "",
        f"Exact-homepage CDX captures returned after monthly collapse: {md(wayback.get('captures_returned'))}; first: {md(wayback.get('first_capture'))}; last: {md(wayback.get('last_capture'))}",
        "",
        "| Timestamp | Original URL | Title | Lang | Visible-text sample | Archive |",
        "|---|---|---|---|---|---|",
    ])
    for item in wayback.get("snapshots", []):
        sample = item.get("meta_description") or item.get("visible_text_sample") or item.get("fetch_error")
        lines.append(f"| {md(item.get('timestamp'))} | {md(item.get('original_url'))} | {md(item.get('title'))} | {md(item.get('html_lang'))} | {md(sample)} | {md(item.get('archive_url'))} |")
    if not wayback.get("snapshots"):
        lines.append(f"| unavailable | | | | {md(wayback.get('error') or 'No captures returned; this does not prove no prior use.')} | |")

    lines.extend(["", "## Manual checks still required", ""])
    lines.append(f"- Google Safe Browsing: {audit['manual_checks']['google_safe_browsing']}")
    lines.append(f"- Google site query: {audit['manual_checks']['google_search_site_query']}")
    lines.append("- Search Console: " + ", ".join(audit["manual_checks"]["search_console"]))
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in audit["limitations"])
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect bounded domain-history evidence for an AdSense readiness audit.")
    parser.add_argument("domain", help="Domain or URL to inspect")
    parser.add_argument("--wayback-snapshots", type=int, default=4, help="Archived pages to sample (0-12; default: 4)")
    parser.add_argument("--timeout", type=float, default=15.0, help="Per-request timeout in seconds (3-60; default: 15)")
    parser.add_argument("--format", choices=("json", "markdown"), default="json", help="Output format")
    args = parser.parse_args(argv)
    if not 0 <= args.wayback_snapshots <= 12:
        parser.error("--wayback-snapshots must be between 0 and 12")
    if not 3 <= args.timeout <= 60:
        parser.error("--timeout must be between 3 and 60")
    return args


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = parse_args(argv or sys.argv[1:])
    try:
        domain = normalize_domain(args.domain)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    audit = audit_domain(domain, args.wayback_snapshots, args.timeout)
    if args.format == "markdown":
        sys.stdout.write(render_markdown(audit))
    else:
        json.dump(audit, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
