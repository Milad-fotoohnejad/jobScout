from __future__ import annotations
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/sqlite/jobscout.db")
REQUESTS_PER_MINUTE = int(os.getenv("REQUESTS_PER_MINUTE", "30"))
