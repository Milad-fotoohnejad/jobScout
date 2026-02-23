from __future__ import annotations

from pathlib import Path
import yaml

from jobscout.domain.job import Job
from jobscout.connectors.ats.greenhouse import fetch_greenhouse_jobs
from jobscout.storage.db import connect_sqlite, init_db
from jobscout.storage.repositories.jobs_repo import JobsRepo


def load_sources(path: str | Path) -> list[dict]:
    p = Path(path)
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    return data.get("sources", [])


def run_once(
    sources_path: str | Path,
    db_path: str | Path = "data/sqlite/jobscout.db",
    debug: bool = False,
) -> tuple[list[Job], int, int]:
    sources = load_sources(sources_path)
    if debug:
        print(f"[Pipeline] Loaded {len(sources)} sources from {sources_path}")

    all_jobs: list[Job] = []

    for s in sources:
        stype = (s.get("type") or "").strip().lower()
        name = (s.get("name") or "Unknown").strip()
        board_url = (s.get("board_url") or "").strip()

        if debug:
            print(f"[Pipeline] Source: type={stype} name={name} url={board_url}")

        if not stype or not board_url:
            continue

        if stype == "greenhouse":
            jobs = fetch_greenhouse_jobs(board_url=board_url, company_name=name, debug=debug)
            all_jobs.extend(jobs)

    # Persist
    conn = connect_sqlite(db_path)
    init_db(conn)
    repo = JobsRepo(conn)
    inserted, updated = repo.upsert_jobs(all_jobs)
    conn.close()

    return all_jobs, inserted, updated