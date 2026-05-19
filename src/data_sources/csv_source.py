"""CSV data source — reads records from a manually exported MS List CSV file."""

import csv
from pathlib import Path
from typing import Any

from .base import DataSource


class CSVDataSource(DataSource):
    """
    Reads automation records from a UTF-8-BOM CSV file exported from MS List.

    The CSV is expected to have a header row followed by one row per automation.
    The 'ID intern' column is used for lookup by ID.

    Lazy-loads the file on first access so construction is cheap.
    """

    def __init__(self, file_path: str | Path):
        self._path = Path(file_path)
        self._records: list[dict[str, Any]] = []
        self._loaded = False

    # ------------------------------------------------------------------
    # DataSource interface
    # ------------------------------------------------------------------

    def fetch_all(self) -> list[dict[str, Any]]:
        self._ensure_loaded()
        return list(self._records)

    def fetch_by_id(self, internal_id: str) -> dict[str, Any]:
        self._ensure_loaded()
        target = str(internal_id).strip()
        for record in self._records:
            if record.get("ID intern", "").strip() == target:
                return record
        raise ValueError(
            f"No record found with ID intern '{internal_id}'. "
            f"Available IDs: {[r.get('ID intern') for r in self._records]}"
        )

    def fetch_by_index(self, index: int) -> dict[str, Any]:
        self._ensure_loaded()
        if not 0 <= index < len(self._records):
            raise IndexError(
                f"Row index {index} out of range "
                f"(file has {len(self._records)} data rows, 0-based)"
            )
        return self._records[index]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _ensure_loaded(self):
        if self._loaded:
            return
        if not self._path.exists():
            raise FileNotFoundError(f"CSV file not found: {self._path}")
        with self._path.open(encoding="utf-8-sig", newline="") as fh:
            reader = csv.DictReader(fh)
            self._records = [dict(row) for row in reader]
        self._loaded = True
