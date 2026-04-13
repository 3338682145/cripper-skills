"""Interactive wizard for source-intake operators."""

from __future__ import annotations

import argparse
from pathlib import Path

from .cron_drain_queue import DEFAULT_QUEUE_PATH, drain_queue
from .intake_url import intake_url


def _prompt_required(label: str) -> str:
    while True:
        value = input(f"{label}: ").strip()
        if value:
            return value
        print("This field is required. Please enter a value.")


def _prompt_optional(label: str, default: str | None = None) -> str | None:
    suffix = f" [{default}]" if default else ""
    value = input(f"{label}{suffix}: ").strip()
    if value:
        return value
    return default


def _prompt_mode() -> str:
    while True:
        value = input("Mode [run/cron] [run]: ").strip().lower()
        if not value:
            return "run"
        if value in {"run", "cron"}:
            return value
        print("Please enter 'run' or 'cron'.")


def _prompt_float(label: str) -> float | None:
    while True:
        value = input(f"{label} (optional): ").strip()
        if not value:
            return None
        try:
            return float(value)
        except ValueError:
            print("Please enter a number or leave it blank.")


def _prompt_reason_codes() -> list[str] | None:
    value = input("Reason codes (comma-separated, optional): ").strip()
    if not value:
        return None
    codes = [part.strip() for part in value.split(",") if part.strip()]
    return codes or None


def _build_run_command(
    *,
    url: str,
    raw_dir: Path,
    review_dir: Path,
    archive_dir: Path,
    verdict: str | None,
    confidence: float | None,
    signal_level: str | None,
    reason_codes: list[str] | None,
    suggested_topic: str | None,
    suggested_kind: str | None,
) -> str:
    parts = [
        "source-intake",
        f"\"{url}\"",
        f"--raw-dir \"{raw_dir}\"",
        f"--review-dir \"{review_dir}\"",
        f"--archive-dir \"{archive_dir}\"",
    ]
    if verdict:
        parts.append(f"--verdict {verdict}")
    if confidence is not None:
        parts.append(f"--confidence {confidence}")
    if signal_level:
        parts.append(f"--signal-level {signal_level}")
    for code in reason_codes or []:
        parts.append(f"--reason-code {code}")
    if suggested_topic:
        parts.append(f"--suggested-topic \"{suggested_topic}\"")
    if suggested_kind:
        parts.append(f"--suggested-kind {suggested_kind}")
    return " ".join(parts)


def _build_cron_command(
    *,
    raw_dir: Path,
    review_dir: Path,
    archive_dir: Path,
    queue_path: Path,
) -> str:
    return " ".join(
        [
            "source-intake-cron",
            f"--raw-dir \"{raw_dir}\"",
            f"--review-dir \"{review_dir}\"",
            f"--archive-dir \"{archive_dir}\"",
            f"--queue-path \"{queue_path}\"",
        ]
    )


def run_wizard(*, print_only: bool = False) -> str:
    print("Source Intake Wizard")
    print("Required fields must be filled. Optional fields can be left blank.")
    print("")

    mode = _prompt_mode()
    raw_dir = Path(_prompt_required("Raw directory")).expanduser()
    review_dir = Path(_prompt_required("Review directory")).expanduser()
    archive_dir = Path(_prompt_required("Archive directory")).expanduser()

    if mode == "run":
        url = _prompt_required("URL")
        verdict = _prompt_optional("Verdict")
        confidence = _prompt_float("Confidence")
        signal_level = _prompt_optional("Signal level")
        reason_codes = _prompt_reason_codes()
        suggested_topic = _prompt_optional("Suggested topic")
        suggested_kind = _prompt_optional("Suggested kind")
        command = _build_run_command(
            url=url,
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
        print("")
        print("Command")
        print(command)
        if print_only:
            return command
        should_run = input("Run now? [Y/n]: ").strip().lower()
        if should_run not in {"", "y", "yes"}:
            return command
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
        print("")
        print(destination)
        return str(destination)

    queue_raw = _prompt_optional("Queue file", str(DEFAULT_QUEUE_PATH))
    queue_path = Path(queue_raw or str(DEFAULT_QUEUE_PATH)).expanduser()
    command = _build_cron_command(
        raw_dir=raw_dir,
        review_dir=review_dir,
        archive_dir=archive_dir,
        queue_path=queue_path,
    )
    print("")
    print("Command")
    print(command)
    if print_only:
        return command
    should_run = input("Run now? [Y/n]: ").strip().lower()
    if should_run not in {"", "y", "yes"}:
        return command
    result = drain_queue(
        raw_dir=raw_dir,
        review_dir=review_dir,
        archive_dir=archive_dir,
        queue_path=queue_path,
    )
    print("")
    print(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Interactive wizard for source-intake commands.")
    parser.add_argument(
        "--print-only",
        action="store_true",
        help="Collect parameters and print the equivalent command without executing it.",
    )
    args = parser.parse_args()
    run_wizard(print_only=args.print_only)


if __name__ == "__main__":
    main()
