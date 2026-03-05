from __future__ import annotations

import re
from typing import Any

import httpx

from jobscout.domain.job import Job


# Lever returns a stable posting id like a UUID in "id"
_UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE)


def fetch_lever_jobs(
    board_url: str,
    company_name: str,
    debug: bool = False,
) -> list[Job]:
    """
    Lever public boards support JSON via: https://jobs.lever.co/<company>?mode=json
    `board_url` should be the base Lever board URL, e.g. https://jobs.lever.co/minesense
    """
    url = board_url.rstrip("/")
    json_url = f"{url}?mode=json"

    headers = {
        "User-Agent": "Mozilla/5.0 (JobScout; +https://github.com/your-repo)",
        "Accept-Language": "en-US,en;q=0.9",
    }

    with httpx.Client(headers=headers, timeout=30, follow_redirects=True) as client:
        r = client.get(json_url)

    if debug:
        print(f"[Lever] GET {json_url} -> {r.status_code}")
        print(f"[Lever] Final URL: {r.url}")

    try:
        r.raise_for_status()
    except httpx.HTTPStatusError as e:
        raise RuntimeError(
            f"[Lever] Failed to fetch board_url={board_url} "
            f"(status={e.response.status_code}). Check the company slug / URL."
        ) from e

    data: list[dict[str, Any]] = r.json()
    if not isinstance(data, list):
        # Lever should return a list of postings
        return []

    jobs: list[Job] = []

    for item in data:
        title = (item.get("text") or "").strip()
        hosted_url = (item.get("hostedUrl") or "").strip()
        posting_id = (item.get("id") or "").strip()

        if not title or not hosted_url:
            continue

        # Location can be in different places depending on board config
        categories = item.get("categories") or {}
        location = None

        if isinstance(categories, dict):
            location = (categories.get("location") or "").strip() or None

        # Fallbacks
        if not location:
            # Sometimes "workplaceType" / "location" is embedded in additional fields
            location = (item.get("workplaceType") or "").strip() or None

        external_id = posting_id if posting_id and _UUID_RE.match(posting_id) else posting_id or None

        jobs.append(
            Job(
                source="lever",
                company=company_name,
                title=title,
                location=location,
                url=hosted_url,
                external_id=external_id,
                # posted_at/description not included here (you can enrich later)
            )
        )

    # Deduplicate by URL
    unique: dict[str, Job] = {}
    for j in jobs:
        unique[str(j.url)] = j

    return list(unique.values())