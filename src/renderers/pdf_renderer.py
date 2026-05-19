"""
PDF renderer for AutomationRecord.

Reproduces the styling from the manual DOCX template:
  - Dark navy  (#1F3864): section headers background, label text colour
  - Medium blue (#2E5FA3): document subtitle
  - Light blue  (#D6E4F7): label cell backgrounds
  - Light grey  (#F5F7FA): alternating value cell backgrounds
  - White       (#FFFFFF): primary value cell background

Uses Liberation Sans (metrically identical to Arial) via ReportLab + TTFont.
"""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from .base import Renderer
from ..models.automation_record import AutomationRecord

# ---------------------------------------------------------------------------
# Fonts
# ---------------------------------------------------------------------------

_FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
_REGULAR = "DejaVuSans"
_BOLD = "DejaVuSans-Bold"

def _register_fonts():
    try:
        pdfmetrics.registerFont(TTFont(_REGULAR, _FONT_DIR + "DejaVuSans.ttf"))
        pdfmetrics.registerFont(TTFont(_BOLD, _FONT_DIR + "DejaVuSans-Bold.ttf"))
        pdfmetrics.registerFontFamily(_REGULAR, normal=_REGULAR, bold=_BOLD)
    except Exception:
        pass  # fall back to Helvetica if fonts are unavailable


_register_fonts()

# ---------------------------------------------------------------------------
# Colour palette
# ---------------------------------------------------------------------------

DARK_BLUE = HexColor("#1F3864")
MEDIUM_BLUE = HexColor("#2E5FA3")
LABEL_BG = HexColor("#D6E4F7")
ROW_ALT_BG = HexColor("#F5F7FA")
BORDER_COLOUR = HexColor("#BCC8D8")

# ---------------------------------------------------------------------------
# Page geometry
# ---------------------------------------------------------------------------

PAGE_W, PAGE_H = A4
MARGIN = 2.0 * cm
CONTENT_W = PAGE_W - 2 * MARGIN

LABEL_COL_W = CONTENT_W * 0.33
VALUE_COL_W = CONTENT_W - LABEL_COL_W

# Signature block: 4 equal columns
SIG_COL_W = CONTENT_W / 4

# ---------------------------------------------------------------------------
# Paragraph styles
# ---------------------------------------------------------------------------

_TITLE_STYLE = ParagraphStyle(
    "AutoTitle",
    fontName=_BOLD,
    fontSize=18,
    leading=22,
    textColor=DARK_BLUE,
    spaceAfter=4,
)

_SUBTITLE_STYLE = ParagraphStyle(
    "AutoSubtitle",
    fontName=_REGULAR,
    fontSize=12,
    leading=16,
    textColor=MEDIUM_BLUE,
    spaceAfter=0,
)

_SECTION_HEADER_STYLE = ParagraphStyle(
    "SectionHeader",
    fontName=_BOLD,
    fontSize=11,
    leading=14,
    textColor=colors.white,
    leftPadding=6,
    rightPadding=6,
    topPadding=4,
    bottomPadding=4,
)

_LABEL_STYLE = ParagraphStyle(
    "FieldLabel",
    fontName=_BOLD,
    fontSize=9,
    leading=12,
    textColor=DARK_BLUE,
)

_VALUE_STYLE = ParagraphStyle(
    "FieldValue",
    fontName=_REGULAR,
    fontSize=9,
    leading=12,
    textColor=colors.black,
)

_SIG_HEADER_STYLE = ParagraphStyle(
    "SigHeader",
    fontName=_BOLD,
    fontSize=9,
    leading=12,
    textColor=colors.white,
    alignment=1,  # centre
)

_SIG_NAME_STYLE = ParagraphStyle(
    "SigName",
    fontName=_REGULAR,
    fontSize=9,
    leading=12,
    textColor=colors.black,
    alignment=1,
)

_SIG_DATE_STYLE = ParagraphStyle(
    "SigDate",
    fontName=_REGULAR,
    fontSize=8,
    leading=11,
    textColor=HexColor("#666666"),
    alignment=1,
)

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _escape(text: str) -> str:
    """Escape characters that ReportLab Paragraph treats as XML markup."""
    return (
        text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _para(text: str, style: ParagraphStyle) -> Paragraph:
    """Build a Paragraph, converting newlines to <br/> tags."""
    safe = _escape(text).replace("\n", "<br/>")
    return Paragraph(safe, style)


def _label(text: str) -> Paragraph:
    return _para(text, _LABEL_STYLE)


def _value(text: str) -> Paragraph:
    return _para(text, _VALUE_STYLE)


# ---------------------------------------------------------------------------
# Section builder
# ---------------------------------------------------------------------------

_SECTION_PADDING = dict(
    leftPadding=6,
    rightPadding=6,
    topPadding=4,
    bottomPadding=4,
)


def _build_section(title: str, rows: list[tuple[str, str]]) -> Table:
    """
    Build a section table:
      row 0  — full-width dark-blue header with white title text
      row 1+ — label (light-blue bg) | value (alternating white/light-grey)
    """
    header_cell = _para(title, _SECTION_HEADER_STYLE)
    data = [[header_cell, ""]]
    for label_text, value_text in rows:
        data.append([_label(label_text), _value(value_text)])

    n = len(data)  # total rows

    style_cmds = [
        # Header row: span + dark blue background
        ("SPAN", (0, 0), (1, 0)),
        ("BACKGROUND", (0, 0), (1, 0), DARK_BLUE),
        ("ALIGN", (0, 0), (1, 0), "LEFT"),
        # Label column (col 0, rows 1+)
        ("BACKGROUND", (0, 1), (0, n - 1), LABEL_BG),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        # Borders
        ("BOX", (0, 0), (-1, -1), 0.5, BORDER_COLOUR),
        ("INNERGRID", (0, 1), (-1, -1), 0.25, BORDER_COLOUR),
        ("LINEBELOW", (0, 0), (1, 0), 0, colors.white),
        # Padding
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]

    # Alternating value cell backgrounds
    for i in range(1, n):
        bg = colors.white if i % 2 == 1 else ROW_ALT_BG
        style_cmds.append(("BACKGROUND", (1, i), (1, i), bg))

    table = Table(
        data,
        colWidths=[LABEL_COL_W, VALUE_COL_W],
        repeatRows=0,
        hAlign="LEFT",
    )
    table.setStyle(TableStyle(style_cmds))
    return table


def _build_signature_block(
    created_by: str,
    responsible: str,
    manager: str,
    process_owner: str,
) -> Table:
    """Build the 4-column signature table."""
    headers = ["Propietari de l'automatització", "Responsable automatització", "Manager", "Propietari procés"]
    names = [created_by, responsible, manager, process_owner]
    date_line = "Data: _______________"

    data = [
        [_para(h, _SIG_HEADER_STYLE) for h in headers],
        [_para(n, _SIG_NAME_STYLE) for n in names],
        [_para(date_line, _SIG_DATE_STYLE) for _ in range(4)],
    ]

    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), DARK_BLUE),
        ("BOX", (0, 0), (-1, -1), 0.5, BORDER_COLOUR),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, BORDER_COLOUR),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("BACKGROUND", (0, 1), (-1, 1), colors.white),
        ("BACKGROUND", (0, 2), (-1, 2), ROW_ALT_BG),
    ]

    table = Table(
        data,
        colWidths=[SIG_COL_W] * 4,
        hAlign="LEFT",
    )
    table.setStyle(TableStyle(style_cmds))
    return table


# ---------------------------------------------------------------------------
# Renderer class
# ---------------------------------------------------------------------------

class PDFRenderer(Renderer):
    """Renders an AutomationRecord to a styled A4 PDF."""

    def render(self, record: AutomationRecord, output_path: Path) -> Path:
        output_path = Path(output_path).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)

        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            leftMargin=MARGIN,
            rightMargin=MARGIN,
            topMargin=MARGIN,
            bottomMargin=MARGIN,
            title=f"{record.automation_name} – {record.process_name}",
            author="Automatitzacions ICIQ",
        )

        story = self._build_story(record)
        doc.build(story)
        return output_path

    # ------------------------------------------------------------------

    def _build_story(self, r: AutomationRecord) -> list:
        sp8 = Spacer(1, 8)
        sp4 = Spacer(1, 4)

        # Determine the process owner's first name for the signature block
        # (take the first entry if it's a multi-line semicolon list)
        sig_owner = r.process_owner.splitlines()[0] if r.process_owner != "—" else r.process_owner

        return [
            # ── Title block ──────────────────────────────────────────────
            _para(f"{r.automation_name} – {r.process_name}", _TITLE_STYLE),
            _para(r.automation_name, _SUBTITLE_STYLE),
            Spacer(1, 14),

            # ── Section 1 — Identificació ────────────────────────────────
            _build_section("Secció 1 — Identificació", [
                ("1.1 Nom del procés", r.process_name),
                ("1.2 Nom de l'automatització", r.automation_name),
                ("1.3 ID intern", r.internal_id),
                ("1.4 Versió", r.version),
                ("1.5 Repositori", r.repository),
                ("1.6 Data de creació", r.creation_date),
                ("1.7 Data última actualització", r.last_update_date),
                ("1.8 Descripció del procés actual", r.current_process_description),
            ]),
            sp8,

            # ── Section 2 — Context ──────────────────────────────────────
            _build_section("Secció 2 — Context", [
                ("2.1 Descripció del procés automatitzat", r.automated_process_description),
                ("2.2 Motiu del canvi", r.change_reason),
            ]),
            sp8,

            # ── Section 3 — Responsabilitats ─────────────────────────────
            _build_section("Secció 3 — Responsabilitats", [
                ("3.1 Propietari del procés de negoci", r.process_owner),
                ("3.2 Responsable de l'automatització", r.software_architect),
                ("3.3 Manager", r.manager),
                ("3.4 Equip / Propietari de l'automatització", r.product_owner),
                ("3.5 Desenvolupadors", r.developers),
                ("3.6 Unitats i persones usuàries", r.user_units),
            ]),
            sp8,

            # ── Section 4 — Detalls Tècnics ──────────────────────────────
            _build_section("Secció 4 — Detalls Tècnics", [
                ("4.1 Tipus d'automatització", r.automation_type),
                ("4.2 Llenguatge / Tecnologia", r.technology),
                ("4.3 Fonts de dades", r.data_sources),
                ("4.4 Output esperat", r.expected_output),
                ("4.5 Freqüència d'execució", r.execution_frequency),
                ("4.6 Dependències", r.dependencies),
            ]),
            sp8,

            # ── Section 5 — Beneficis ─────────────────────────────────────
            _build_section("Secció 5 — Beneficis", [
                ("5.1 Temps estalviat", r.time_saved),
                ("5.2 Impacte econòmic estimat", r.economic_impact),
                ("5.3 Beneficis i KPI", r.benefits),
            ]),
            sp8,

            # ── Section 6 — Estat i Roadmap ───────────────────────────────
            _build_section("Secció 6 — Estat i Roadmap", [
                ("6.1 Estat actual", r.current_status),
                ("6.2 Temps estimat de desenvolupament", r.estimated_dev_time),
                ("6.3 Temps real invertit", r.actual_dev_time),
                ("6.4 Data final prevista d'implementació", r.implementation_deadline),
                ("6.5 Millores futures", r.future_improvements),
            ]),
            sp8,

            # ── Section 7 — Seguretat i Compliance ───────────────────────
            _build_section("Secció 7 — Seguretat i Compliance", [
                ("7.1 Credencials i permisos", r.credentials_permissions),
                ("7.2 Identificació de riscos", r.risks),
                ("7.3 Protecció de dades", r.data_protection),
                ("7.4 Logs i traçabilitat", r.logs_traceability),
            ]),
            sp8,

            # ── Signature block ───────────────────────────────────────────
            _build_section("Signatures i Validació", []),
            sp4,
            _build_signature_block(
                created_by=r.product_owner,
                responsible=r.software_architect,
                manager=r.manager,
                process_owner=sig_owner,
            ),
        ]
