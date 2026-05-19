"""Abstract base class for automation record data sources."""

from abc import ABC, abstractmethod
from typing import Any


class DataSource(ABC):
    """
    Abstract interface for fetching raw automation records.

    Implementations exist for CSV (current) and SharePoint API (future).
    Raw records are returned as plain dicts keyed by CSV column name,
    exactly as they come from the source — no transformation applied here.
    """

    @abstractmethod
    def fetch_all(self) -> list[dict[str, Any]]:
        """Return all automation records as raw dicts."""
        raise NotImplementedError

    @abstractmethod
    def fetch_by_id(self, internal_id: str) -> dict[str, Any]:
        """Return the record whose 'ID intern' matches internal_id."""
        raise NotImplementedError

    @abstractmethod
    def fetch_by_index(self, index: int) -> dict[str, Any]:
        """Return the record at the given 0-based position in the list."""
        raise NotImplementedError
