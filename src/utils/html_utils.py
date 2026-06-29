"""Utilities for stripping HTML from MS List field values."""

from html.parser import HTMLParser


class _HTMLToText(HTMLParser):
    """Converts HTML to plain text, preserving list items as bullet points."""

    def __init__(self):
        super().__init__()
        self._parts: list[str] = []
        self._pending_bullet = False

    def handle_starttag(self, tag: str, attrs):
        tag = tag.lower()
        if tag == "li":
            self._pending_bullet = True
        elif tag in ("br",):
            self._parts.append("\n")
        elif tag in ("p", "div", "ul", "ol") and self._parts:
            last = self._parts[-1] if self._parts else ""
            if last and not last.endswith("\n"):
                self._parts.append("\n")

    def handle_endtag(self, tag: str):
        tag = tag.lower()
        if tag == "li":
            last = self._parts[-1] if self._parts else ""
            if last and not last.endswith("\n"):
                self._parts.append("\n")
        elif tag in ("p", "div") and self._parts:
            last = self._parts[-1] if self._parts else ""
            if last and not last.endswith("\n"):
                self._parts.append("\n")

    def handle_data(self, data: str):
        # Collapse internal whitespace (including newlines from HTML source formatting)
        data = " ".join(data.split())
        if not data:
            return
        if self._pending_bullet:
            self._parts.append("• " + data)
            self._pending_bullet = False
        else:
            self._parts.append(data)

    def get_text(self) -> str:
        raw = "".join(self._parts)
        lines = [line.strip() for line in raw.splitlines()]
        lines = [line for line in lines if line]
        return "\n".join(lines)


def html_to_text(html: str) -> str:
    """
    Strip HTML tags from a field value, converting structure to plain text.

    - <li> items become '• item' bullet lines
    - <div>, <p>, <br> become line breaks
    - HTML entities like &#58; and &#39; are decoded
    """
    if not html or not html.strip():
        return ""
    # Decode common SharePoint-encoded HTML entities before parsing
    html = html.replace("&#58;", ":").replace("&#39;", "'").replace("&amp;", "&")
    parser = _HTMLToText()
    parser.feed(html)
    return parser.get_text()
