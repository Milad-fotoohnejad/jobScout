#!/usr/bin/env python3
"""
Scaffold JobScout project structure.

- Creates directories + placeholder files under ./jobScout
- Skips any paths that already exist (no overwrite)
"""

from __future__ import annotations

from pathlib import Path
from datetime import date


ROOT = Path("jobScout")  # matches your current repo folder name


DIRS = [
    "docs/diagrams",
    "docs/decisions",
    "docs/notes",
    "assets",
    "docker",
    "scripts",
    "tests/unit",
    "tests/integration",
    "tests/fixtures/html",
    "data/sqlite",
    "data/cache",
    "data/raw_pages",
    "data/exports",
    "src/jobscout/config",
    "src/jobscout/domain",
    "src/jobscout/core",
    "src/jobscout/connectors/ats",
    "src/jobscout/connectors/company_sites",
    "src/jobscout/connectors/aggregators",
    "src/jobscout/storage/repositories",
    "src/jobscout/storage/migrations",
    "src/jobscout/services",
    "src/jobscout/api/routes",
    "src/jobscout/api/schemas",
    "src/jobscout/cli",
    "src/jobscout/ai/prompts",
    "src/jobscout/auto_apply",
]

FILES = [
    # Root-level (you already have README.md and LICENSE.txt; we will skip if present)
    ".env.example",
    ".gitignore",
    "pyproject.toml",
    "ruff.toml",
    "pytest.ini",

    # Docs placeholders
    "docs/decisions/0001-tech-stack.md",
    "docs/decisions/0002-data-model.md",
    "docs/notes/scraping-guidelines.md",

    # Package init files
    "src/jobscout/__init__.py",
    "src/jobscout/config/__init__.py",
    "src/jobscout/domain/__init__.py",
    "src/jobscout/core/__init__.py",
    "src/jobscout/connectors/__init__.py",
    "src/jobscout/connectors/ats/__init__.py",
    "src/jobscout/connectors/company_sites/__init__.py",
    "src/jobscout/connectors/aggregators/__init__.py",
    "src/jobscout/storage/__init__.py",
    "src/jobscout/storage/repositories/__init__.py",
    "src/jobscout/services/__init__.py",
    "src/jobscout/api/__init__.py",
    "src/jobscout/api/routes/__init__.py",
    "src/jobscout/api/schemas/__init__.py",
    "src/jobscout/cli/__init__.py",
    "src/jobscout/ai/__init__.py",
    "src/jobscout/ai/prompts/__init__.py",
    "src/jobscout/auto_apply/__init__.py",

    # Config
    "src/jobscout/config/settings.py",
    "src/jobscout/config/sources.yaml",
    "src/jobscout/config/rubric.yaml",
    "src/jobscout/config/logging.yaml",

    # Domain
    "src/jobscout/domain/job.py",
    "src/jobscout/domain/enums.py",

    # Core
    "src/jobscout/core/fetch.py",
    "src/jobscout/core/browser.py",
    "src/jobscout/core/parse.py",
    "src/jobscout/core/normalize.py",
    "src/jobscout/core/enrich.py",
    "src/jobscout/core/score.py",
    "src/jobscout/core/dedupe.py",
    "src/jobscout/core/validate.py",

    # Connectors
    "src/jobscout/connectors/base.py",
    "src/jobscout/connectors/ats/greenhouse.py",
    "src/jobscout/connectors/ats/lever.py",
    "src/jobscout/connectors/company_sites/example_company.py",
    "src/jobscout/connectors/aggregators/indeed.py",
    "src/jobscout/connectors/aggregators/glassdoor.py",

    # Storage
    "src/jobscout/storage/db.py",
    "src/jobscout/storage/models.py",
    "src/jobscout/storage/repositories/jobs_repo.py",
    "src/jobscout/storage/repositories/runs_repo.py",

    # Services
    "src/jobscout/services/pipeline.py",
    "src/jobscout/services/health.py",
    "src/jobscout/services/notify.py",
    "src/jobscout/services/export.py",
    "src/jobscout/services/scheduler.py",

    # API (optional; placeholder)
    "src/jobscout/api/main.py",
    "src/jobscout/api/routes/jobs.py",
    "src/jobscout/api/routes/health.py",
    "src/jobscout/api/schemas/jobs.py",

    # CLI
    "src/jobscout/cli/main.py",

    # AI (future)
    "src/jobscout/ai/tailoring.py",
    "src/jobscout/ai/guardrails.py",
    "src/jobscout/ai/prompts/resume_tailor.md",
    "src/jobscout/ai/prompts/cover_letter_tailor.md",

    # Auto-apply (future)
    "src/jobscout/auto_apply/runner.py",
    "src/jobscout/auto_apply/form_filler.py",
    "src/jobscout/auto_apply/artifacts.py",
    "src/jobscout/auto_apply/approvals.py",

    # Scripts
    "scripts/init_db.py",
    "scripts/run_once.py",
    "scripts/smoke_test_sources.py",
    "scripts/export_matches.py",

    # Tests
    "tests/unit/test_scoring.py",
    "tests/unit/test_dedupe.py",
    "tests/unit/test_parsing.py",
    "tests/integration/test_pipeline_run.py",
    "tests/integration/test_greenhouse_connector.py",
]


def safe_mkdir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def safe_write(path: Path, content: str = "") -> None:
    if path.exists():
        print(f"SKIP (exists): {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"CREATE: {path}")


def main() -> None:
    if not ROOT.exists():
        print(f"Root folder '{ROOT}' does not exist. Creating it.")
        ROOT.mkdir(parents=True, exist_ok=True)

    # Directories
    for d in DIRS:
        p = ROOT / d
        if not p.exists():
            safe_mkdir(p)
            print(f"MKDIR: {p}")
        else:
            print(f"SKIP (dir exists): {p}")

    # Minimal starter contents for a few files
    year = date.today().year
    gitignore_content = """\
# Python
__pycache__/
*.py[cod]
*.pyo
*.pyd
*.egg-info/
dist/
build/
.venv/
.env

# Editors/OS
.DS_Store
.vscode/
.idea/

# Local data (do not commit)
data/
"""

    env_example_content = """\
# Database (SQLite by default)
DATABASE_URL=sqlite:///data/sqlite/jobscout.db

# Rate limiting
REQUESTS_PER_MINUTE=30

# Optional: Notifications
# TELEGRAM_BOT_TOKEN=
# TELEGRAM_CHAT_ID=
# SLACK_WEBHOOK_URL=
"""

    pyproject_content = """\
[project]
name = "jobscout"
version = "0.0.1"
description = "Job discovery and fit scoring pipeline"
requires-python = ">=3.11"
dependencies = []

[tool.pytest.ini_options]
testpaths = ["tests"]
"""

    settings_content = """\
from __future__ import annotations
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/sqlite/jobscout.db")
REQUESTS_PER_MINUTE = int(os.getenv("REQUESTS_PER_MINUTE", "30"))
"""

    sources_yaml_content = """\
sources: []
"""

    rubric_yaml_content = """\
rubric:
  target_keywords: ["frontend", "react", "next.js"]
  must_haves: ["remote"]
  nice_to_haves: ["typescript", "graphql", "postgres"]
  red_flags: ["unpaid", "10+ years", "on-site only"]
"""

    license_note_content = f"""\
NOTE:
You currently have LICENSE.txt. GitHub detects licenses best if the file is named exactly: LICENSE (no extension).

If you want, rename:
  LICENSE.txt -> LICENSE

(Do this after committing if you prefer.)
"""

    # Create files (some with content)
    for f in FILES:
        path = ROOT / f
        if f == ".gitignore":
            safe_write(path, gitignore_content)
        elif f == ".env.example":
            safe_write(path, env_example_content)
        elif f == "pyproject.toml":
            safe_write(path, pyproject_content)
        elif f == "src/jobscout/config/settings.py":
            safe_write(path, settings_content)
        elif f == "src/jobscout/config/sources.yaml":
            safe_write(path, sources_yaml_content)
        elif f == "src/jobscout/config/rubric.yaml":
            safe_write(path, rubric_yaml_content)
        else:
            safe_write(path, "")

    # Helpful note (won't overwrite)
    safe_write(ROOT / "docs/notes/license-file-name.md", license_note_content)

    print("\nDone. Next steps:")
    print(f"1) Review created files under: {ROOT}")
    print("2) (Recommended) Rename LICENSE.txt -> LICENSE so GitHub detects it.")
    print("3) Create a virtualenv and start implementing connectors + pipeline.")


if __name__ == "__main__":
    main()