from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from app.core.models import BrowserMode


load_dotenv()


def _to_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(slots=True)
class AppSettings:
    app_name: str
    base_dir: Path
    output_root: Path
    run_root: Path
    browser_mode: BrowserMode
    headless: bool
    playwright_slow_mo_ms: int
    real_chrome_executable: str | None
    mpay_username: str | None
    mpay_password: str | None

    @classmethod
    def load(cls) -> "AppSettings":
        base_dir = Path(__file__).resolve().parents[2]
        output_name = os.getenv("DEFAULT_DOWNLOAD_ROOT", "output")
        run_name = os.getenv("JOB_RUN_ROOT", "runs")
        browser_mode = BrowserMode(os.getenv("BROWSER_MODE", BrowserMode.MANAGED.value))
        return cls(
            app_name=os.getenv("APP_NAME", "DI Prototype V2"),
            base_dir=base_dir,
            output_root=base_dir / output_name,
            run_root=base_dir / run_name,
            browser_mode=browser_mode,
            headless=_to_bool(os.getenv("HEADLESS"), default=False),
            playwright_slow_mo_ms=int(os.getenv("PLAYWRIGHT_SLOW_MO_MS", "0")),
            real_chrome_executable=os.getenv("REAL_CHROME_EXECUTABLE") or None,
            mpay_username=os.getenv("MPAY_USERNAME") or None,
            mpay_password=os.getenv("MPAY_PASSWORD") or None,
        )
