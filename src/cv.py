from __future__ import annotations

from io import BytesIO

from docx import Document
from pypdf import PdfReader


def extract_cv_text(uploaded_file) -> str:
    data = uploaded_file.getvalue()
    name = uploaded_file.name.lower()
    if name.endswith(".pdf"):
        return "\n".join(page.extract_text() or "" for page in PdfReader(BytesIO(data)).pages)
    if name.endswith(".docx"):
        return "\n".join(p.text for p in Document(BytesIO(data)).paragraphs)
    return data.decode("utf-8", errors="replace")

