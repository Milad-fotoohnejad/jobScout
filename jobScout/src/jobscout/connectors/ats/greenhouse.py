from __future__ import annotations

import re
import httpx
from selectolax.parser import HTMLParser, Node

from jobscout.domain.job import Job


_JOB_ID_RE = re.compile(r"/jobs/(\d+)")


def _abs_url(base_url: httpx.URL, board_url: str, href: str) -> str:
    href = (href or "").strip()
    if not href:
        return ""
    if href.startswith("/"):
        return f"{base_url.scheme}://{base_url.host}{href}"
    if href.startswith("http"):
        return href
    return board_url.rstrip("/") + "/" + href.lstrip("/")


def _extract_location(anchor: Node) -> str | None:
    """
    Greenhouse job boards usually render location as a sibling element
    near the <a> link, commonly under the parent container.
    """
    container = anchor.parent  # opening wrapper in most layouts
    if not container:
        return None

    # Try a few common patterns
    for sel in (".location", "span.location", "p.location", ".opening-location", "[data-location]"):
        n = container.css_first(sel)
        if n:
            txt = n.text(strip=True)
            if txt:
                return txt

    # Sometimes location is one level up
    if container.parent:
        for sel in (".location", "span.location", "p.location"):
            n = container.parent.css_first(sel)
            if n:
                txt = n.text(strip=True)
                if txt:
                    return txt

    return None


def fetch_greenhouse_jobs(
    board_url: str,
    company_name: str,
    debug: bool = False,
) -> list[Job]:
    headers = {
        "User-Agent": "Mozilla/5.0 (JobScout; +https://github.com/your-repo)",
        "Accept-Language": "en-US,en;q=0.9",
    }

    with httpx.Client(headers=headers, timeout=30, follow_redirects=True) as client:
        r = client.get(board_url)

    if debug:
        print(f"[Greenhouse] GET {board_url} -> {r.status_code}")
        print(f"[Greenhouse] Final URL: {r.url}")

    try:
        r.raise_for_status()
    except httpx.HTTPStatusError as e:
        raise RuntimeError(
            f"[Greenhouse] Failed to fetch board_url={board_url} "
            f"(status={e.response.status_code}). Check the company slug / URL."
        ) from e

    html = HTMLParser(r.text)

    selectors = [
        "a.opening",
        "a[href*='/jobs/']",
        "a[href*='/job/']",
        "a[data-mce-href*='/jobs/']",
    ]

    openings: list[Node] = []
    used = None
    for sel in selectors:
        nodes = html.css(sel)
        if nodes:
            openings = nodes
            used = sel
            break

    if debug:
        print(f"[Greenhouse] Selector used: {used!r} | Found nodes: {len(openings)}")
        snippet = r.text[:400].replace("\n", " ")
        print(f"[Greenhouse] HTML snippet: {snippet}...")

    jobs: list[Job] = []

    for a in openings:
        href = (a.attributes.get("href") or "").strip()
        url = _abs_url(r.url, board_url, href)
        if not url:
            continue

        # Avoid adding non-job links if selector is broad
        if "/jobs/" not in url and "/job/" not in url:
            continue

        title = a.text(separator=" ", strip=True)
        if not title:
            continue

        # Extract external_id from URL if present
        m = _JOB_ID_RE.search(url)
        external_id = m.group(1) if m else None

        # Location is sometimes embedded in the anchor text (e.g., "... Remote-EMEA")
        raw = title
        location = None

        if "Remote-" in raw:
            left, right = raw.rsplit("Remote-", 1)
            title = left.strip()
            location = ("Remote-" + right.strip()).strip()
        else:
            location = _extract_location(a)

        jobs.append(
            Job(
                source="greenhouse",
                company=company_name,
                title=title,
                location=location,
                url=url,
                external_id=external_id,
            )
        )

    # Deduplicate within this run
    unique: dict[str, Job] = {}
    for j in jobs:
        unique[str(j.url)] = j

    return list(unique.values())