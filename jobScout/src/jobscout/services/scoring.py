import re
from jobscout.domain.job import Job

ROLE_BUCKETS = {
    "frontend": [r"\bfrontend\b", r"\bfront-end\b", r"\breact\b", r"\bui\b"],
    "fullstack": [r"\bfull\s*stack\b", r"\bfull-stack\b", r"\bbackend\b", r"\bapi\b"],
    "mobile": [r"\bmobile\b", r"\breact\s*native\b", r"\bflutter\b", r"\bios\b", r"\bandroid\b"],
    "data": [r"\bdata\s*analyst\b", r"\banalytics\b", r"\bsql\b", r"\bpython\b", r"\bbi\b"],
    "webdev": [r"\bweb\b", r"\bjavascript\b", r"\btypescript\b", r"\bnext\.?js\b"],
}

EXCLUDE_HINTS = [r"\bstaff\b", r"\bprincipal\b", r"\bdirector\b", r"\bvp\b"]

def score_and_tag(job: Job) -> tuple[int, list[str]]:
    text = f"{job.title} {job.location or ''} {job.description or ''}".lower()
    score = 0
    tags: list[str] = []

    for tag, patterns in ROLE_BUCKETS.items():
        if any(re.search(p, text) for p in patterns):
            tags.append(tag)
            score += 3

    # light seniority penalty (optional)
    if re.search(r"\bsenior\b", text):
        score -= 2
    if any(re.search(p, text) for p in EXCLUDE_HINTS):
        score -= 5

    return score, sorted(set(tags))