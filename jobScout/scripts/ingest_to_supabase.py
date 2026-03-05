from __future__ import annotations

import jobscout.services.scoring as scoring
print("[DEBUG] scoring.py path:", scoring.__file__)

import hashlib
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client

from jobscout.domain.job import Job
from jobscout.services.pipeline import run_once as pipeline_run_once
from jobscout.services.scoring import score_and_tag


# Load env vars from jobScout/.env.local if present, otherwise fallback to repo-root .env.local / .env
load_dotenv("jobScout/.env.local")
load_dotenv(".env.local")
load_dotenv(".env")


def _norm(s: str | None) -> str:
    if not s:
        return ""
    s = s.strip().lower()
    s = re.sub(r"\s+", " ", s)
    return s


def build_job_key(j: Job) -> str:
    ext = getattr(j, "external_id", None)
    if not ext:
        # fallback only if no external id exists
        raw = f"{_norm(j.source)}|{_norm(j.company)}|{_norm(j.title)}|{_norm(j.location)}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    # stable ID-based key (preferred)
    return f"{_norm(j.source)}|{_norm(j.company)}|{ext}"


def main() -> None:
    supabase_url = os.environ["SUPABASE_URL"]
    service_key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    sb = create_client(supabase_url, service_key)

    sources = Path("jobScout/src/jobscout/config/sources.yaml")
    result = pipeline_run_once(sources_path=sources, debug=True)

    rows: list[dict] = []

    for j in result.jobs:
        score, tags, excluded, reasons = score_and_tag(j)
        job_key = build_job_key(j)

        rows.append(
            {
                "job_key": job_key,
                "source": j.source,
                "company": j.company,
                "title": j.title,
                "location": j.location,
                "url": str(j.url),
                "external_id": getattr(j, "external_id", None),
                "posted_at": j.posted_at,
                "description": j.description,
                "score": int(score),
                "tags": tags,
                "excluded": bool(excluded),
                # Optional: store reasons as a readable string
                "reasons": ",".join(reasons) if reasons else None,
            }
        )

    if rows:
        sb.table("jobs").upsert(rows, on_conflict="job_key").execute()
        print(f"[Supabase] Upserted {len(rows)} jobs")
    else:
        print("[Supabase] No jobs to upsert")


if __name__ == "__main__":
    main()