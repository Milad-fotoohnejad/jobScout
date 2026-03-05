from __future__ import annotations

import re
from jobscout.domain.job import Job


def _norm_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()


# Block only senior+ / management
SENIORITY_EXCLUDE_WORDS = re.compile(
    r"\b("
    r"senior|sr|lead|staff|principal|architect|manager|head|director|vp|chief"
    r")\b"
)
VICE_PRESIDENT = re.compile(r"\bvice president\b")

# Mid-level signals (boost, NOT exclude)
MID_LEVEL_HINTS = re.compile(
    r"\b("
    r"intermediate|mid|midlevel|mid-level|level\s*2|l2|ii\b"
    r")\b"
)

JUNIOR_HINTS = re.compile(
    r"\b("
    r"junior|jr|entry|entry-level|associate|new grad|newgrad|graduate"
    r")\b"
)

NON_DEV_EXCLUDE = re.compile(
    r"\b("
    r"customer care|customer support|support specialist|payroll|accounting|finance|hr|recruiter|"
    r"sales|marketing|success manager|operations|employee relations"
    r")\b",
    re.IGNORECASE,
)

ROLE_BUCKETS: dict[str, list[str]] = {
    "frontend": [
        r"\bfrontend\b", r"\bfront[- ]end\b", r"\bui engineer\b", r"\bui developer\b",
        r"\breact\b", r"\bnext\.?js\b", r"\btypescript\b", r"\bjavascript\b",
    ],
    "fullstack": [
        r"\bfull[- ]stack\b", r"\bfullstack\b",
        r"\bbackend\b", r"\bapi\b", r"\brest\b",
        r"\bnode\.?js\b", r"\bexpress\b", r"\bfirebase\b",
    ],
    "mobile": [
        r"\bflutter\b", r"\breact native\b", r"\bexpo\b",
        r"\bios\b", r"\bandroid\b",
    ],
    "data": [
        r"\bdata analyst\b", r"\banalytics\b", r"\bbusiness intelligence\b", r"\bbi\b",
        r"\bsql\b", r"\bpython\b", r"\bpower bi\b", r"\btableau\b",
    ],
    "webdev": [
        r"\bweb developer\b", r"\bsoftware developer\b", r"\bsoftware engineer\b",
        r"\bjavascript\b", r"\btypescript\b", r"\breact\b",
    ],
}

BOOSTS: list[tuple[str, int]] = [
    # Your strongest stack
    (r"\breact\b", 6),
    (r"\bnext\.?js\b", 6),
    (r"\btypescript\b", 5),

    # Mobile
    (r"\bflutter\b", 4),
    (r"\breact native\b|\bexpo\b", 4),

    # Data
    (r"\bsql\b", 2),
    (r"\bpython\b", 2),
    (r"\bpower bi\b|\btableau\b", 2),

    # General dev signals
    (r"\bapi\b|\brest\b", 2),
    (r"\bnode\.?js\b|\bexpress\b", 2),
]


def score_and_tag(job: Job) -> tuple[int, list[str], bool, list[str]]:
    title = (job.title or "").strip()
    title_norm = _norm_title(title)
    text = f"{title} {job.location or ''} {job.description or ''}".lower()

    # Hard exclude senior+ / management
    if SENIORITY_EXCLUDE_WORDS.search(title_norm) or VICE_PRESIDENT.search(title_norm):
        return (-999, [], True, ["seniority_exclude"])

    # Hard exclude non-dev roles
    if NON_DEV_EXCLUDE.search(text):
        return (-999, [], True, ["non_dev_exclude"])

    score = 0
    tags: list[str] = []
    reasons: list[str] = []

    # Bucket tagging
    for tag, patterns in ROLE_BUCKETS.items():
        if any(re.search(p, text) for p in patterns):
            tags.append(tag)
            score += 8
            reasons.append(f"tag:{tag}")

    # Boost for junior/mid indicators (allowed)
    if MID_LEVEL_HINTS.search(title_norm):
        score += 4
        reasons.append("mid_level:+4")
    if JUNIOR_HINTS.search(title_norm):
        score += 4
        reasons.append("junior:+4")

    # Skill boosts
    for pattern, pts in BOOSTS:
        if re.search(pattern, text):
            score += pts
            reasons.append(f"+{pts}:{pattern}")

    # If no target buckets matched, hide from dev-only view
    if not tags:
        return (-50, [], True, ["no_target_bucket_match"])

    return (score, sorted(set(tags)), False, reasons)