from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable

from app.core.models import JobContext


LogFn = Callable[[str], None]


class BillerAdapter(ABC):
    biller_name: str

    @abstractmethod
    def run(self, context: JobContext, log: LogFn) -> None:
        """Execute the end-to-end workflow for a biller."""
