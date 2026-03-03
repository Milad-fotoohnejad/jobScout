from __future__ import annotations

import sqlite3
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS jobs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  url TEXT NOT NULL UNIQUE,
  source TEXT NOT NULL,
  company TEXT NOT NULL,
  title TEXT NOT NULL,
  location TEXT,
  external_id TEXT,
  job_key TEXT,
  first_seen_utc TEXT NOT NULL,
  last_seen_utc TEXT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_jobs_url ON jobs(url);
CREATE UNIQUE INDEX IF NOT EXISTS idx_jobs_job_key ON jobs(job_key);

CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company);
CREATE INDEX IF NOT EXISTS idx_jobs_last_seen ON jobs(last_seen_utc);
"""


def connect_sqlite(db_path: str | Path) -> sqlite3.Connection:
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def _has_column(conn: sqlite3.Connection, table: str, col: str) -> bool:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return any(r["name"] == col for r in rows)


def _canonicalize_url(url: str) -> str:
    # Strip query/fragment to avoid duplicate URLs caused by tracking params
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


def _backfill_job_key(conn: sqlite3.Connection) -> None:
    """
    Backfill job_key for existing rows using a conservative fallback:
    source + company + title + location (lowercased, trimmed).
    This is not as strong as external_id, but gives you stable dedupe immediately.
    """
    # Only backfill rows where job_key is NULL or empty
    rows = conn.execute(
        """
        SELECT id, url, source, company, title, location
        FROM jobs
        WHERE job_key IS NULL OR job_key = ''
        """
    ).fetchall()

    import hashlib
    import re

    def norm(s: str | None) -> str:
        if not s:
            return ""
        s = s.strip().lower()
        s = re.sub(r"\s+", " ", s)
        return s

    for r in rows:
        # also normalize url to reduce duplicates caused by tracking parameters
        canonical_url = _canonicalize_url(r["url"])
        if canonical_url != r["url"]:
            conn.execute("UPDATE jobs SET url = ? WHERE id = ?", (canonical_url, r["id"]))

        raw = f"{norm(r['source'])}|{norm(r['company'])}|{norm(r['title'])}|{norm(r['location'])}"
        job_key = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        conn.execute("UPDATE jobs SET job_key = ? WHERE id = ?", (job_key, r["id"]))


def init_db(conn: sqlite3.Connection) -> None:
    # Ensure base schema exists (for new DBs)
    conn.executescript(SCHEMA_SQL)

    # Migrate existing DBs safely (no-op if already migrated)
    if not _has_column(conn, "jobs", "external_id"):
        conn.execute("ALTER TABLE jobs ADD COLUMN external_id TEXT")
    if not _has_column(conn, "jobs", "job_key"):
        conn.execute("ALTER TABLE jobs ADD COLUMN job_key TEXT")

    # Backfill job_key for existing rows so unique index can work meaningfully
    _backfill_job_key(conn)

    # Create indexes (safe to run repeatedly)
    conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_jobs_job_key ON jobs(job_key)")
    conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_jobs_url ON jobs(url)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_last_seen ON jobs(last_seen_utc)")

    conn.commit()