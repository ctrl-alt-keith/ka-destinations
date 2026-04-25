"""Google Docs publishing helpers."""

from __future__ import annotations

from typing import Any

GOOGLE_DOCS_URL_TEMPLATE = "https://docs.google.com/document/d/{document_id}/edit"
GOOGLE_DOCS_SCOPES = ("https://www.googleapis.com/auth/documents",)


def publish_markdown(*, content: str, title: str, service: Any | None = None) -> str:
    """Create a Google Doc and write markdown content as readable plain text."""
    service = service or _build_docs_service()
    document = service.documents().create(body={"title": title}).execute()
    document_id = str(document["documentId"])

    if content:
        service.documents().batchUpdate(
            documentId=document_id,
            body={
                "requests": [
                    {
                        "insertText": {
                            "location": {"index": 1},
                            "text": content,
                        }
                    }
                ]
            },
        ).execute()

    return GOOGLE_DOCS_URL_TEMPLATE.format(document_id=document_id)


def _build_docs_service() -> Any:
    try:
        import google.auth
        from googleapiclient.discovery import build  # type: ignore[import-untyped]
    except ImportError as exc:
        raise RuntimeError(
            "Google API dependencies are not installed. Install ka-destinations with "
            "its package dependencies before publishing to Google Docs."
        ) from exc

    credentials, _project_id = google.auth.default(scopes=list(GOOGLE_DOCS_SCOPES))
    return build("docs", "v1", credentials=credentials)
