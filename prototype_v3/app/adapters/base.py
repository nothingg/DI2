from __future__ import annotations

from abc import ABC, abstractmethod

from app.core.models import JobContext


class BillerAdapter(ABC):
    biller_name: str

    @abstractmethod
    def run(self, context: JobContext, log) -> None:
        raise NotImplementedError
