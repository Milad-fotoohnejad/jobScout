from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from typing import Iterable

from jobscout.domain.job import Job


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class JobsRepo:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def upsert_jobs(self, jobs: Iterable[Job]) -> tuple[int, int]:
        """
        Insert new jobs and update last_seen for existing ones.

        Returns:
          (inserted_count, updated_count)
        """
        inserted = 0
        updated = 0
        now = utc_now_iso()

        for j in jobs:
            # Try insert first
            try:
                self.conn.execute(
                    """
                    INSERT INTO jobs (url, source, company, title, location, first_seen_utc, last_seen_utc)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (str(j.url), j.source, j.company, j.title, j.location, now, now),
                )
                inserted += 1
            except sqlite3.IntegrityError:
                # URL already exists -> update last_seen + optionally refresh title/location
                cur = self.conn.execute(
                    """
                    UPDATE jobs
                    SET last_seen_utc = ?,
                        title = ?,
                        location = ?
                    WHERE url = ?
                    """,
                    (now, j.title, j.location, str(j.url)),
                )
                if cur.rowcount:
                    updated += 1

        self.conn.commit()
        return inserted, updated

    def get_new_jobs_since(self, since_iso: str) -> list[sqlite3.Row]:
        cur = self.conn.execute(
            """
            SELECT url, source, company, title, location, first_seen_utc, last_seen_utc
            FROM jobs
            WHERE first_seen_utc >= ?
            ORDER BY first_seen_utc DESC
            """,
            (since_iso,),
        )
        return list(cur.fetchall())