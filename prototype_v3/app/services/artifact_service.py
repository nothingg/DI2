from __future__ import annotations

from pathlib import Path

from playwright.sync_api import Page


def save_page_artifacts(
    page: Page | None,
    artifact_dir: Path,
    prefix: str,
    log,
    extra_meta_lines: list[str] | None = None,
) -> None:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    meta_path = artifact_dir / f"{prefix}-meta.txt"
    meta_lines = list(extra_meta_lines or [])

    if page is None:
        meta_lines.append("url=<page_not_created>")
        meta_path.write_text("\n".join(meta_lines), encoding="utf-8")
        log(f"Saved page metadata: {meta_path}")
        return

    screenshot_path = artifact_dir / f"{prefix}-screenshot.png"
    html_path = artifact_dir / f"{prefix}-page.html"

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
        meta_lines.append(f"url={page.url}")
        meta_path.write_text("\n".join(meta_lines), encoding="utf-8")
        log(f"Saved page metadata: {meta_path}")
    except Exception as exc:
        log(f"Failed to save page metadata: {exc}")


def save_failure_artifacts(
    page: Page | None,
    artifact_dir: Path,
    job_id: str,
    biller: str,
    run_date: str,
    log_file: Path | None,
    log,
) -> None:
    save_page_artifacts(
        page=page,
        artifact_dir=artifact_dir,
        prefix="failure",
        log=log,
        extra_meta_lines=[
            f"job_id={job_id}",
            f"biller={biller}",
            f"run_date={run_date}",
            f"log_file={log_file}" if log_file else "log_file=<not_set>",
        ],
    )
