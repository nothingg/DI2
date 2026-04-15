from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


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
    browser_mode: str
    headless: bool
    chrome_channel: str
    playwright_slow_mo_ms: int
    step_delay_seconds: int
    keep_browser_open: bool
    real_chrome_executable: str | None
    mpay_username: str | None
    mpay_password: str | None
    mpay_fetch_servu: bool
    servu_host: str | None
    servu_port: int
    servu_username: str | None
    servu_password: str | None
    mpay_servu_path: str

    @classmethod
    def load(cls) -> "AppSettings":
        base_dir = Path(__file__).resolve().parents[2]
        output_name = os.getenv("DEFAULT_OUTPUT_ROOT", "output")
        run_name = os.getenv("JOB_RUN_ROOT", "runs")
        return cls(
            app_name=os.getenv("APP_NAME", "DI Prototype V3"),
            base_dir=base_dir,
            output_root=base_dir / output_name,
            run_root=base_dir / run_name,
            browser_mode=os.getenv("BROWSER_MODE", "managed"),
            headless=_to_bool(os.getenv("HEADLESS"), default=False),
            chrome_channel=os.getenv("CHROME_CHANNEL", "chrome"),
            playwright_slow_mo_ms=int(os.getenv("PLAYWRIGHT_SLOW_MO_MS", "0")),
            step_delay_seconds=int(os.getenv("STEP_DELAY_SECONDS", "5")),
            keep_browser_open=_to_bool(os.getenv("KEEP_BROWSER_OPEN"), default=True),
            real_chrome_executable=os.getenv("REAL_CHROME_EXECUTABLE") or None,
            mpay_username=os.getenv("MPAY_USERNAME") or None,
            mpay_password=os.getenv("MPAY_PASSWORD") or None,
            mpay_fetch_servu=_to_bool(os.getenv("MPAY_FETCH_SERVU"), default=False),
            servu_host=os.getenv("SERVU_HOST") or None,
            servu_port=int(os.getenv("SERVU_PORT", "22")),
            servu_username=os.getenv("SERVU_USERNAME") or None,
            servu_password=os.getenv("SERVU_PASSWORD") or None,
            mpay_servu_path=os.getenv("MPAY_SERVU_PATH", "/DCR/AMP/IN/"),
        )
