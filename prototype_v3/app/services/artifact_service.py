from __future__ import annotations

from pathlib import Path

from playwright.sync_api import Page


def save_failure_artifacts(
    page: Page | None,
    artifact_dir: Path,
    job_id: str,
    biller: str,
    run_date: str,
    log_file: Path | None,
    log,
) -> None:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    meta_path = artifact_dir / "failure-meta.txt"

    if page is None:
        meta_path.write_text(
            "\n".join(
                [
                    f"job_id={job_id}",
                    f"biller={biller}",
                    f"run_date={run_date}",
                    f"log_file={log_file}" if log_file else "log_file=<not_set>",
                    "url=<page_not_created>",
                ]
            ),
            encoding="utf-8",
        )
        log(f"Saved failure metadata: {meta_path}")
        return

    screenshot_path = artifact_dir / "failure-screenshot.png"
    html_path = artifact_dir / "failure-page.html"

    try:
        page.screenshot(path=str(screenshot_path), full_page=True)
        log(f"Saved screenshot: {screenshot_path}")
    except Exception as exc:
        log(f"Failed to save screenshot: {exc}")

    try:
        html_path.write_text(page.content(), encoding="utf-8")
        log(f"Saved HTML snapshot: {html_path}")
    except Exception as exc:
        log(f"Failed to save HTML snapshot: {exc}")

    try:
        meta_path.write_text(
            "\n".join(
                [
                    f"job_id={job_id}",
                    f"biller={biller}",
                    f"run_date={run_date}",
                    f"log_file={log_file}" if log_file else "log_file=<not_set>",
                    f"url={page.url}",
                ]
            ),
            encoding="utf-8",
        )
        log(f"Saved failure metadata: {meta_path}")
    except Exception as exc:
        log(f"Failed to save failure metadata: {exc}")
