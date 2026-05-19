"""Abstract base class for AutomationRecord renderers."""

from abc import ABC, abstractmethod
from pathlib import Path

from ..models.automation_record import AutomationRecord


class Renderer(ABC):
    """
    Renders an AutomationRecord to a file.

    Subclasses implement specific output formats (PDF, DOCX, HTML, …).
    render() must create any intermediate directories and return the
    resolved absolute path to the file that was written.
    """

    @abstractmethod
    def render(self, record: AutomationRecord, output_path: Path) -> Path:
        """Write record to output_path and return the final resolved path."""
        raise NotImplementedError
