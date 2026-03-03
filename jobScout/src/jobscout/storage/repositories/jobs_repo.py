from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from typing import Iterable
import hashlib
import re

from jobscout.domain.job import Job


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _norm(s: str | None) -> str:
    if not s:
        return ""
    s = s.strip().lower()
    s = re.sub(r"\s+", " ", s)
    return s


def build_job_key(j: Job) -> str:
    # Prefer external_id if present (best key for Greenhouse)
    if getattr(j, "external_id", None):
        raw = f"{_norm(j.source)}|{_norm(j.company)}|ext|{_norm(j.external_id)}"
    else:
        raw = f"{_norm(j.source)}|{_norm(j.company)}|{_norm(j.title)}|{_norm(j.location)}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class JobsRepo:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def upsert_jobs(self, jobs: Iterable[Job]) -> tuple[int, int]:
        inserted = 0
        updated = 0
        now = utc_now_iso()

        for j in jobs:
            url = str(j.url)
            job_key = build_job_key(j)
            external_id = getattr(j, "external_id", None)

            # 1) Migration-safe: if URL already exists, upgrade that row with job_key/external_id
            cur = self.conn.execute(
                """
                UPDATE jobs
                SET last_seen_utc = ?,
                    title = ?,
                    location = ?,
                    external_id = COALESCE(?, external_id),
                    job_key = COALESCE(?, job_key)
                WHERE url = ?
                """,
                (now, j.title, j.location, external_id, job_key, url),
            )
            if cur.rowcount:
                updated += 1
                continue

            # 2) Otherwise insert; if job_key already exists, update that row
            try:
                self.conn.execute(
                    """
                    INSERT INTO jobs (
                        job_key, url, source, company, title, location, external_id,
                        first_seen_utc, last_seen_utc
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(job_key) DO UPDATE SET
                        last_seen_utc = excluded.last_seen_utc,
                        url = excluded.url,
                        title = excluded.title,
                        location = excluded.location,
                        external_id = COALESCE(excluded.external_id, jobs.external_id)
                    """,
                    (job_key, url, j.source, j.company, j.title, j.location, external_id, now, now),
                )
                inserted += 1
            except sqlite3.IntegrityError:
                # 3) Last-resort safety net: if URL uniqueness still collides, update by URL
                cur2 = self.conn.execute(
                    """
                    UPDATE jobs
                    SET last_seen_utc = ?,
                        title = ?,
                        location = ?,
                        external_id = COALESCE(?, external_id),
                        job_key = COALESCE(?, job_key)
                    WHERE url = ?
                    """,
                    (now, j.title, j.location, external_id, job_key, url),
                )
                if cur2.rowcount:
                    updated += 1

        self.conn.commit()
        return inserted, updated