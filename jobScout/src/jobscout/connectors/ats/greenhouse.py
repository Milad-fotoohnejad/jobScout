from __future__ import annotations

import httpx
from selectolax.parser import HTMLParser

from jobscout.domain.job import Job


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

    # Try multiple selectors because Greenhouse layouts vary slightly
    selectors = [
        "a.opening",                 # common
        "a[href*='/jobs/']",         # job links
        "a[href*='/job/']",          # alt
        "a[data-mce-href*='/jobs/']",# rare
    ]

    openings = []
    used = None
    for sel in selectors:
        nodes = html.css(sel)
        if nodes:
            openings = nodes
            used = sel
            break

    if debug:
        print(f"[Greenhouse] Selector used: {used!r} | Found nodes: {len(openings)}")
        # Print a tiny snippet for visibility (first 400 chars)
        snippet = r.text[:400].replace("\n", " ")
        print(f"[Greenhouse] HTML snippet: {snippet}...")

    jobs: list[Job] = []

    for a in openings:
        raw_text = a.text(separator=" ", strip=True)

        location = None
        title = raw_text

        # If the text includes a "Remote-..." suffix (as in your output), split it out
        if "Remote-" in raw_text:
            left, right = raw_text.rsplit("Remote-", 1)
            title = left.strip()
            location = ("Remote-" + right.strip()).strip()
        else:
        # fallback: try node-based location if available
            loc_node = a.css_first(".location")
            location = loc_node.text(strip=True) if loc_node else None

        href = (a.attributes.get("href") or "").strip()
        if not href:
            continue

        if href.startswith("/"):
            # Some boards are on boards.greenhouse.io, some on job-boards.greenhouse.io
            base = f"{r.url.scheme}://{r.url.host}"
            url = base + href
        elif href.startswith("http"):
            url = href
        else:
            url = board_url.rstrip("/") + "/" + href.lstrip("/")

        loc_node = a.css_first(".location")
        location = loc_node.text(strip=True) if loc_node else None

        # Avoid adding non-job links if selector is broad
        if "/jobs/" not in url and "/job/" not in url:
            continue

        jobs.append(
            Job(
                source="greenhouse",
                company=company_name,
                title=title,
                location=location,
                url=url,
            )
        )

    # Deduplicate within this run (some selectors may pick duplicates)
    unique = {}
    for j in jobs:
        unique[str(j.url)] = j

    return list(unique.values())