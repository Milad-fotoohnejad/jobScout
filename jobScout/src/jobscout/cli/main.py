from __future__ import annotations

from pathlib import Path
import typer

from jobscout.services.pipeline import run_once as pipeline_run_once

app = typer.Typer(help="JobScout CLI", add_completion=False)

@app.callback(invoke_without_command=False)
def cli() -> None:
    """JobScout command-line interface."""
    return

@app.command("ping")
def ping() -> None:
    """Sanity check: confirms the CLI is runnable."""
    typer.echo("JobScout is alive ✅")

@app.command("run-once")
def run_once(
    sources: str = typer.Option(
        "src/jobscout/config/sources.yaml",
        "--sources",
        help="Path to sources.yaml",
    ),
    debug: bool = typer.Option(False, "--debug", help="Print debug diagnostics"),
) -> None:
    """Run a single ingestion pass and print discovered jobs."""
    jobs, inserted, updated = pipeline_run_once(Path(sources), debug=debug)

    typer.echo(f"Discovered {len(jobs)} jobs | New: {inserted} | Updated: {updated}\n")

    if not jobs:
        raise typer.Exit(code=0)

    # For now: print all jobs (next we’ll add --new-only filtering)
    for j in jobs:
        typer.echo(f"- {j.company} | {j.title} | {j.location or 'N/A'}")
        typer.echo(f"  {j.url}\n")

if __name__ == "__main__":
    app(prog_name="jobscout")
