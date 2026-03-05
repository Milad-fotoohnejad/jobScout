from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import time
import yaml

from jobscout.connectors.ats.greenhouse import fetch_greenhouse_jobs
from jobscout.connectors.ats.lever import fetch_lever_jobs
from jobscout.domain.job import Job
from jobscout.storage.db import connect_sqlite, init_db
from jobscout.storage.repositories.jobs_repo import JobsRepo


@dataclass
class PipelineResult:
    jobs: list[Job] = field(default_factory=list)
    inserted: int = 0
    updated: int = 0
    skipped_sources: int = 0
    source_errors: list[str] = field(default_factory=list)
    duration_ms: int = 0


def load_sources(path: str | Path) -> list[dict[str, Any]]:
    p = Path(path)
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    sources = data.get("sources", [])
    return sources if isinstance(sources, list) else []


def run_once(
    sources_path: str | Path,
    db_path: str | Path = "data/sqlite/jobscout.db",
    debug: bool = False,
) -> PipelineResult:
    t0 = time.time()

    sources = load_sources(sources_path)
    if debug:
        print(f"[Pipeline] Loaded {len(sources)} sources from {sources_path}")

    all_jobs: list[Job] = []
    skipped_sources = 0
    source_errors: list[str] = []

    for s in sources:
        stype = (s.get("type") or "").strip().lower()
        name = (s.get("name") or "Unknown").strip()
        board_url = (s.get("board_url") or "").strip()

        if debug:
            print(f"[Pipeline] Source: type={stype} name={name} url={board_url}")

        if not stype or not board_url:
            skipped_sources += 1
            continue

        try:
            if stype == "greenhouse":
                jobs = fetch_greenhouse_jobs(
                    board_url=board_url,
                    company_name=name,
                    debug=debug,
                )
                all_jobs.extend(jobs)

            elif stype == "lever":
                jobs = fetch_lever_jobs(
                    board_url=board_url,
                    company_name=name,
                    debug=debug,
                )
                all_jobs.extend(jobs)

            else:
                skipped_sources += 1
        except Exception as e:
            msg = f"{name} ({stype}) failed: {e}"
            source_errors.append(msg)
            if debug:
                print(f"[Pipeline][ERROR] {msg}")

    conn = connect_sqlite(db_path)
    init_db(conn)
    repo = JobsRepo(conn)
    inserted, updated = repo.upsert_jobs(all_jobs)
    conn.close()

    duration_ms = int((time.time() - t0) * 1000)

    return PipelineResult(
        jobs=all_jobs,
        inserted=inserted,
        updated=updated,
        skipped_sources=skipped_sources,
        source_errors=source_errors,
        duration_ms=duration_ms,
    )