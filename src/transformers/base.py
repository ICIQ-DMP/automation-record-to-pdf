"""Abstract base class for raw-record → AutomationRecord transformers."""

from abc import ABC, abstractmethod
from typing import Any

from ..models.automation_record import AutomationRecord


class Transformer(ABC):
    """
    Transforms a raw dict (from a DataSource) into an AutomationRecord.

    Responsibilities:
    - Parse JSON array fields into human-readable strings
    - Strip HTML from rich-text fields
    - Convert booleans to localised Sí/No strings
    - Format dates to DD/MM/YYYY
    - Replace missing/empty values with '—'
    """

    @abstractmethod
    def transform(self, raw: dict[str, Any]) -> AutomationRecord:
        raise NotImplementedError
