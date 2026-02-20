from __future__ import annotations

from pydantic import BaseModel, HttpUrl
from typing import Optional


class Job(BaseModel):
    source: str
    company: str
    title: str
    location: Optional[str] = None
    url: HttpUrl
    posted_at: Optional[str] = None
    description: Optional[str] = None