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


def _load_browser_mode_overrides() -> dict[str, str]:
    overrides: dict[str, str] = {}
    suffix = "_BROWSER_MODE"
    for key, value in os.environ.items():
        if key == "BROWSER_MODE" or not key.endswith(suffix):
            continue
        if not value:
            continue
        biller = key[: -len(suffix)].lower()
        overrides[biller] = value
    return overrides


def _load_user_data_dir_overrides(base_dir: Path) -> dict[str, Path]:
    overrides: dict[str, Path] = {}
    suffix = "_USER_DATA_DIR"
    for key, value in os.environ.items():
        if not key.endswith(suffix) or not value:
            continue
        biller = key[: -len(suffix)].lower()
        user_data_dir = Path(value)
        if not user_data_dir.is_absolute():
            user_data_dir = base_dir / user_data_dir
        overrides[biller] = user_data_dir
    return overrides


def _load_cdp_url_overrides() -> dict[str, str]:
    overrides: dict[str, str] = {}
    suffix = "_CDP_URL"
    for key, value in os.environ.items():
        if not key.endswith(suffix) or not value:
            continue
        biller = key[: -len(suffix)].lower()
        overrides[biller] = value
    return overrides


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
    browser_mode_overrides: dict[str, str]
    browser_user_data_dirs: dict[str, Path]
    browser_cdp_urls: dict[str, str]
    real_chrome_executable: str | None
    mpay_username: str | None
    mpay_password: str | None
    mpay_fetch_servu: bool
    lotus_username: str | None
    lotus_password: str | None
    lotus_secret_code: str | None
    lotus_fetch_servu: bool
    lotus_manual_login: bool
    lotus_tims_username: str | None
    lotus_tims_password: str | None
    baac_username: str | None
    baac_password: str | None
    baac_fetch_servu: bool
    true_username: str | None
    true_password: str | None
    true_fetch_servu: bool
    counter_service_username: str | None
    counter_service_password: str | None
    counter_service_fetch_servu: bool
    servu_host: str | None
    servu_port: int
    servu_username: str | None
    servu_password: str | None
    mpay_servu_path: str
    lotus_servu_path: str
    baac_servu_path: str
    true_servu_path: str
    counter_service_servu_path: str

    def resolve_browser_mode(self, biller: str) -> str:
        normalized = biller.replace("-", "_").lower()
        return self.browser_mode_overrides.get(normalized, self.browser_mode)

    def resolve_user_data_dir(self, biller: str) -> Path | None:
        normalized = biller.replace("-", "_").lower()
        return self.browser_user_data_dirs.get(normalized)

    def resolve_cdp_url(self, biller: str) -> str | None:
        normalized = biller.replace("-", "_").lower()
        return self.browser_cdp_urls.get(normalized)

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
            browser_mode_overrides=_load_browser_mode_overrides(),
            browser_user_data_dirs=_load_user_data_dir_overrides(base_dir),
            browser_cdp_urls=_load_cdp_url_overrides(),
            real_chrome_executable=os.getenv("REAL_CHROME_EXECUTABLE") or None,
            mpay_username=os.getenv("MPAY_USERNAME") or None,
            mpay_password=os.getenv("MPAY_PASSWORD") or None,
            mpay_fetch_servu=_to_bool(os.getenv("MPAY_FETCH_SERVU"), default=False),
            lotus_username=os.getenv("LOTUS_USERNAME") or None,
            lotus_password=os.getenv("LOTUS_PASSWORD") or None,
            lotus_secret_code=os.getenv("LOTUS_SECRET_CODE") or None,
            lotus_fetch_servu=_to_bool(os.getenv("LOTUS_FETCH_SERVU"), default=True),
            lotus_manual_login=_to_bool(os.getenv("LOTUS_MANUAL_LOGIN"), default=False),
            lotus_tims_username=os.getenv("LOTUS_TIMS_USERNAME") or None,
            lotus_tims_password=os.getenv("LOTUS_TIMS_PASSWORD") or None,
            baac_username=os.getenv("BAAC_USERNAME") or None,
            baac_password=os.getenv("BAAC_PASSWORD") or None,
            baac_fetch_servu=_to_bool(os.getenv("BAAC_FETCH_SERVU"), default=True),
            true_username=os.getenv("TRUE_USERNAME") or None,
            true_password=os.getenv("TRUE_PASSWORD") or None,
            true_fetch_servu=_to_bool(os.getenv("TRUE_FETCH_SERVU"), default=True),
            counter_service_username=os.getenv("COUNTER_SERVICE_USERNAME") or None,
            counter_service_password=os.getenv("COUNTER_SERVICE_PASSWORD") or None,
            counter_service_fetch_servu=_to_bool(os.getenv("COUNTER_SERVICE_FETCH_SERVU"), default=True),
            servu_host=os.getenv("SERVU_HOST") or None,
            servu_port=int(os.getenv("SERVU_PORT", "22")),
            servu_username=os.getenv("SERVU_USERNAME") or None,
            servu_password=os.getenv("SERVU_PASSWORD") or None,
            mpay_servu_path=os.getenv("MPAY_SERVU_PATH", "/DCR/AMP/IN/"),
            lotus_servu_path=os.getenv("LOTUS_SERVU_PATH", "/DCR/TESCO/IN/"),
            baac_servu_path=os.getenv("BAAC_SERVU_PATH", "/DCR/BAAC/IN/"),
            true_servu_path=os.getenv("TRUE_SERVU_PATH", "/DCR/TRUE/IN/"),
            counter_service_servu_path=os.getenv("COUNTER_SERVICE_SERVU_PATH", "/DCR/CST/IN/"),
        )
