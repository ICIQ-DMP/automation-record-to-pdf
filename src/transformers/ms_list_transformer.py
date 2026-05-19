"""
Transformer for MS List CSV rows → AutomationRecord.

Handles all field-type variations produced by the MS List CSV export:
  - JSON arrays  (e.g. Motiu del canvi, Tipus d'automatització)
  - HTML strings (e.g. Descripció del procés actual, Riscos)
  - Semicolon-separated plain text (e.g. Propietari, Unitats)
  - Boolean strings ('True' / 'False')
  - MS-format datetime strings ('M/D/YYYY H:MM AM/PM')
  - Plain numeric / text values
"""

import json
from datetime import datetime
from typing import Any

from .base import Transformer
from ..models.automation_record import AutomationRecord
from ..utils.html_utils import html_to_text


_EMPTY = "—"

# MS List datetime formats to try when parsing date fields
_DATE_FORMATS = [
    "%m/%d/%Y %I:%M %p",   # 12/9/2025 1:12 AM
    "%m/%d/%Y %I:%M%p",    # 12/9/2025 1:12AM
    "%m/%d/%Y",             # 9/4/2025
]


class MSListTransformer(Transformer):
    """Transforms a raw MS List CSV row dict into an AutomationRecord."""

    def transform(self, raw: dict[str, Any]) -> AutomationRecord:
        g = raw.get  # shorthand

        # Resolve developer list: deduplicate vs. architect
        architect = self._text(g("Arquitecte de software (software arquitect)"))
        devs_raw = self._semicolon_list(g("Desenvolupadors (developers)"))
        # If architects and developers are the same person, show once
        if devs_raw and devs_raw != _EMPTY and architect and architect != _EMPTY:
            dev_names = {n.strip() for n in devs_raw.splitlines()}
            arch_names = {n.strip() for n in architect.splitlines()}
            if dev_names == arch_names:
                developers = architect
            else:
                developers = devs_raw
        else:
            developers = devs_raw if devs_raw != _EMPTY else architect

        return AutomationRecord(
            # Section 1
            process_name=self._text(g("Nom del procés a automatitzar")),
            automation_name=self._text(g("Nom de l´automatització")),
            internal_id=self._text(g("ID intern")),
            version=self._text(g("Version")),
            repository=self._text(g("Repositori")),
            creation_date=self._date(g("Data de creació")),
            last_update_date=self._date(g("Data última actualització")),
            current_process_description=self._field(g("Descripció del procés actual")),
            # Section 2
            automated_process_description=self._field(g("Descripció del procés automatitzat")),
            change_reason=self._json_list(g("Motiu del canvi")),
            # Section 3
            product_owner=self._text(g("Propietari de l'automatització (product owner)")),
            process_owner=self._semicolon_list(g("Propietari del procés de negoci (process owner)")),
            software_architect=architect,
            manager=self._text(g("Manager")),
            developers=developers,
            user_units=self._semicolon_list(g("Unitats i persones usuàries del procés de negoci")),
            benefits=self._field(g("Beneficis")),
            # Section 4
            automation_type=self._json_list(g("Tipus d´automatització")),
            technology=self._json_list(g("Llenguatge i tecnologia")),
            data_sources=self._field(g("Fonts de dades")),
            expected_output=self._field(g("Output esperat")),
            execution_frequency=self._json_list(g("Freqüència execució")),
            dependencies=self._field(g("Dependències")),
            # Section 5
            time_saved=self._hours_per_year(g("Temps estalviat (hores/any)")),
            economic_impact=self._economic(g("Impacte econòmic estimat (€ / any)")),
            # Section 6
            current_status=self._json_list(g("Estat actual")),
            estimated_dev_time=self._hours(g("Temps estimat desenvolupament (hores totals)")),
            actual_dev_time=self._hours(g("Temps real invertit (hores totals)")),
            implementation_deadline=self._date(g("Data final prevista implementació")),
            future_improvements=self._field(g("Millores Futures")),
            # Section 7
            credentials_permissions=self._json_list(g("Credencials i permisos")),
            risks=self._field(g("Riscos")),
            data_protection=self._boolean(g("Protecció de dades")),
            logs_traceability=self._boolean(g("Logs i traçabilitat")),
        )

    # ------------------------------------------------------------------
    # Field-type helpers
    # ------------------------------------------------------------------

    def _empty(self, value) -> bool:
        return value is None or str(value).strip() == ""

    def _text(self, value) -> str:
        """Plain text field — strip whitespace, return _EMPTY if blank."""
        if self._empty(value):
            return _EMPTY
        return str(value).strip()

    def _field(self, value) -> str:
        """Auto-detect HTML vs. plain text and return clean plain text."""
        if self._empty(value):
            return _EMPTY
        v = str(value).strip()
        if "<" in v:
            result = html_to_text(v)
        else:
            result = v
        return result if result else _EMPTY

    def _json_list(self, value) -> str:
        """Parse a JSON array field and join items with '; '."""
        if self._empty(value):
            return _EMPTY
        v = str(value).strip()
        try:
            items = json.loads(v)
            if isinstance(items, list):
                joined = "; ".join(str(i).strip() for i in items if str(i).strip())
                return joined if joined else _EMPTY
            return str(items)
        except (json.JSONDecodeError, TypeError):
            return self._text(value)

    def _semicolon_list(self, value) -> str:
        """Semicolon-separated list → one item per line."""
        if self._empty(value):
            return _EMPTY
        items = [i.strip() for i in str(value).split(";") if i.strip()]
        return "\n".join(items) if items else _EMPTY

    def _boolean(self, value) -> str:
        """Convert 'True'/'False' string to 'Sí'/'No'."""
        if self._empty(value):
            return _EMPTY
        v = str(value).strip().lower()
        if v == "true":
            return "Sí"
        if v == "false":
            return "No"
        return self._text(value)

    def _date(self, value) -> str:
        """Parse MS List datetime string and return DD/MM/YYYY."""
        if self._empty(value):
            return _EMPTY
        v = str(value).strip()
        for fmt in _DATE_FORMATS:
            try:
                dt = datetime.strptime(v, fmt)
                return dt.strftime("%d/%m/%Y")
            except ValueError:
                continue
        return v  # return as-is if no format matched

    def _hours(self, value) -> str:
        """Numeric hours value → 'N hores'."""
        if self._empty(value):
            return _EMPTY
        v = str(value).strip()
        try:
            float(v.replace(",", "."))
            return f"{v} hores"
        except ValueError:
            return v if v else _EMPTY

    def _hours_per_year(self, value) -> str:
        """Numeric hours/year → 'N h/any'."""
        if self._empty(value):
            return _EMPTY
        v = str(value).strip()
        try:
            float(v.replace(",", "."))
            return f"{v} h/any"
        except ValueError:
            return v if v else _EMPTY

    def _economic(self, value) -> str:
        """Numeric economic impact → 'N €/any'."""
        if self._empty(value):
            return _EMPTY
        v = str(value).strip()
        try:
            float(v.replace(",", "."))
            return f"{v} €/any"
        except ValueError:
            return v if v else _EMPTY
