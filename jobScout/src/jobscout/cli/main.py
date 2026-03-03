from __future__ import annotations

import json
from pathlib import Path
import typer

from jobscout.services.pipeline import run_once as pipeline_run_once

app = typer.Typer(help="JobScout CLI", add_completion=False)


def _to_dict(job) -> dict:
    # Adjust field names to match your Job model
    return {
        "title": getattr(job, "title", None),
        "company": getattr(job, "company", None),
        "location": getattr(job, "location", None),
        "url": getattr(job, "url", None),
        "source": getattr(job, "source", None),
        "external_id": getattr(job, "external_id", None),
    }


@app.callback(invoke_without_command=False)
def cli() -> None:
    return


@app.command("ping")
def ping() -> None:
    typer.echo("JobScout is alive ✅")


@app.command("run-once")
def run_once(
    sources: str = typer.Option(
        "src/jobscout/config/sources.yaml",
        "--sources",
        help="Path to sources.yaml",
    ),
    db: str = typer.Option(
        "data/sqlite/jobscout.db",
        "--db",
        help="Path to SQLite DB",
    ),
    limit: int = typer.Option(
        20,
        "--limit",
        help="Max number of jobs to print",
    ),
    fmt: str = typer.Option(
        "table",
        "--format",
        help="Output format: table or json",
    ),
    fail_on_empty: bool = typer.Option(
        False,
        "--fail-on-empty",
        help="Exit non-zero if no jobs discovered",
    ),
    debug: bool = typer.Option(False, "--debug", help="Print debug diagnostics"),
) -> None:
    result = pipeline_run_once(Path(sources), db_path=Path(db), debug=debug)

    jobs = result.jobs[: max(limit, 0)]

    if fmt.lower() == "json":
        payload = {
            "counts": {
                "discovered": len(result.jobs),
                "inserted": result.inserted,
                "updated": result.updated,
                "skipped_sources": result.skipped_sources,
                "errors": len(result.source_errors),
                "duration_ms": result.duration_ms,
            },
            "jobs": [_to_dict(j) for j in jobs],
            "source_errors": result.source_errors,
        }
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(
            f"Discovered {len(result.jobs)} jobs | New: {result.inserted} | Updated: {result.updated} "
            f"| Skipped sources: {result.skipped_sources} | Errors: {len(result.source_errors)} "
            f"| {result.duration_ms}ms\n"
        )
        for j in jobs:
            title = getattr(j, "title", "")
            company = getattr(j, "company", "")
            location = getattr(j, "location", "")
            url = getattr(j, "url", "")
            typer.echo(f"- {company} | {title} | {location} | {url}")

        if result.source_errors:
            typer.echo("\nSource errors:")
            for e in result.source_errors:
                typer.echo(f"  - {e}")

    if fail_on_empty and len(result.jobs) == 0:
        raise typer.Exit(code=2)
    
if __name__ == "__main__":
    app()