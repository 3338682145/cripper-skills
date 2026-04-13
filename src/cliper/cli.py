from __future__ import annotations

from pathlib import Path

import typer

from cliper.service import IngestService, ValidationService
from cliper_source_intake.cron_drain_queue import DEFAULT_QUEUE_PATH, drain_queue
from cliper_source_intake.intake_url import intake_url
from cliper_source_intake.wizard import run_wizard

app = typer.Typer(help="Cliper contract-first ingestion CLI.")
registry_app = typer.Typer(help="Registry commands.")
ingest_app = typer.Typer(help="Ingestion commands.")
validate_app = typer.Typer(help="Validation commands.")
source_intake_app = typer.Typer(help="Source-intake optional skill commands.")

app.add_typer(registry_app, name="registry")
app.add_typer(ingest_app, name="ingest")
app.add_typer(validate_app, name="validate")
app.add_typer(source_intake_app, name="source-intake")


def _root_option(root: Path) -> Path:
    return root.resolve()


@registry_app.command("validate")
def registry_validate(
    root: Path = typer.Option(Path("."), "--root", exists=True, file_okay=False, dir_okay=True, callback=_root_option),
) -> None:
    issues = ValidationService(root).validate_registry()
    if issues:
        for issue in issues:
            typer.echo(f"[FAIL] {issue.location}: {issue.message}")
        raise typer.Exit(code=1)
    typer.echo("Registry validation passed.")


@ingest_app.command("run")
def ingest_run(
    source: str = typer.Option(..., "--source"),
    job: str | None = typer.Option(None, "--job"),
    root: Path = typer.Option(Path("."), "--root", exists=True, file_okay=False, dir_okay=True, callback=_root_option),
) -> None:
    manifest = IngestService(root).run(source, job)
    typer.echo(f"Run: {manifest.run_id}")
    typer.echo(f"Created assets: {len(manifest.created_assets)}")
    typer.echo(f"Deduped assets: {len(manifest.deduped_assets)}")
    typer.echo(f"Manifest path: state/runs/{manifest.run_id}.json")


@validate_app.command("all")
def validate_all(
    root: Path = typer.Option(Path("."), "--root", exists=True, file_okay=False, dir_okay=True, callback=_root_option),
) -> None:
    issues = ValidationService(root).validate_all()
    if issues:
        for issue in issues:
            typer.echo(f"[FAIL] {issue.location}: {issue.message}")
        raise typer.Exit(code=1)
    typer.echo("All validation gates passed.")


@source_intake_app.command("run")
def source_intake_run(
    url: str,
    raw_dir: Path = typer.Option(..., "--raw-dir", file_okay=False, dir_okay=True),
    review_dir: Path = typer.Option(..., "--review-dir", file_okay=False, dir_okay=True),
    archive_dir: Path = typer.Option(..., "--archive-dir", file_okay=False, dir_okay=True),
    verdict: str | None = typer.Option(None, "--verdict"),
    confidence: float | None = typer.Option(None, "--confidence"),
    signal_level: str | None = typer.Option(None, "--signal-level"),
    reason_codes: list[str] | None = typer.Option(None, "--reason-code"),
    suggested_topic: str | None = typer.Option(None, "--suggested-topic"),
    suggested_kind: str | None = typer.Option(None, "--suggested-kind"),
) -> None:
    destination = intake_url(
        url,
        raw_dir=raw_dir,
        review_dir=review_dir,
        archive_dir=archive_dir,
        verdict=verdict,
        confidence=confidence,
        signal_level=signal_level,
        reason_codes=reason_codes,
        suggested_topic=suggested_topic,
        suggested_kind=suggested_kind,
    )
    typer.echo(destination)


@source_intake_app.command("cron")
def source_intake_cron(
    raw_dir: Path = typer.Option(..., "--raw-dir", file_okay=False, dir_okay=True),
    review_dir: Path = typer.Option(..., "--review-dir", file_okay=False, dir_okay=True),
    archive_dir: Path = typer.Option(..., "--archive-dir", file_okay=False, dir_okay=True),
    queue_path: Path = typer.Option(DEFAULT_QUEUE_PATH, "--queue-path", file_okay=True, dir_okay=False),
) -> None:
    typer.echo(
        drain_queue(
            raw_dir=raw_dir,
            review_dir=review_dir,
            archive_dir=archive_dir,
            queue_path=queue_path,
        )
    )


@source_intake_app.command("wizard")
def source_intake_wizard(
    print_only: bool = typer.Option(False, "--print-only", help="Print the generated command without executing it."),
) -> None:
    typer.echo(run_wizard(print_only=print_only))


def main() -> None:
    app()
