"""Turn a user-supplied paper reference into a Claude API document content block.

Accepts:
  - a local PDF path            (./paper.pdf)
  - a direct URL to a PDF       (https://example.com/paper.pdf)
  - an arXiv ID or arXiv URL    (2301.10226, arXiv:2301.10226, https://arxiv.org/abs/2301.10226)
"""

from __future__ import annotations

import base64
import re
from pathlib import Path

ARXIV_ID_RE = re.compile(r"^(?:arxiv:)?(\d{4}\.\d{4,5}(?:v\d+)?)$", re.IGNORECASE)
ARXIV_URL_RE = re.compile(
    r"^https?://(?:www\.)?arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5}(?:v\d+)?)(?:\.pdf)?/?$",
    re.IGNORECASE,
)

MAX_PDF_BYTES = 32 * 1024 * 1024  # API limit for PDF documents


def resolve_paper(ref: str) -> tuple[dict, str]:
    """Resolve a paper reference into (document_block, human-readable description)."""
    ref = ref.strip()

    arxiv_match = ARXIV_ID_RE.match(ref) or ARXIV_URL_RE.match(ref)
    if arxiv_match:
        arxiv_id = arxiv_match.group(1)
        url = f"https://arxiv.org/pdf/{arxiv_id}"
        return _url_block(url), f"arXiv:{arxiv_id}"

    if ref.startswith(("http://", "https://")):
        return _url_block(ref), ref

    path = Path(ref).expanduser()
    if path.exists():
        if path.suffix.lower() != ".pdf":
            raise ValueError(
                f"Local file must be a PDF, got: {path.name}. "
                "For papers in other formats, export them to PDF first."
            )
        size = path.stat().st_size
        if size > MAX_PDF_BYTES:
            raise ValueError(
                f"{path.name} is {size / 1e6:.0f} MB, above the 32 MB API limit for PDFs."
            )
        data = base64.standard_b64encode(path.read_bytes()).decode("utf-8")
        return _base64_block(data), path.name

    raise ValueError(
        f"Could not resolve {ref!r}. Pass a local PDF path, a URL to a PDF, or an arXiv ID."
    )


def _url_block(url: str) -> dict:
    return {
        "type": "document",
        "source": {"type": "url", "url": url},
        # Cache the paper so interactive follow-up questions reuse it cheaply.
        "cache_control": {"type": "ephemeral"},
    }


def _base64_block(data: str) -> dict:
    return {
        "type": "document",
        "source": {"type": "base64", "media_type": "application/pdf", "data": data},
        "cache_control": {"type": "ephemeral"},
    }
