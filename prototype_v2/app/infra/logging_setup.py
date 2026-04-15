from __future__ import annotations

import logging
from pathlib import Path

from app.infra.files import ensure_dir


def configure_logging(log_dir: Path) -> Path:
    ensure_dir(log_dir)
    log_file = log_dir / "prototype_v2.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(),
        ],
        force=True,
    )
    return log_file
