"""Google Docs publishing helpers."""

from __future__ import annotations

from typing import Any

GOOGLE_DOC_MIME_TYPE = "application/vnd.google-apps.document"
GOOGLE_DOCS_URL_TEMPLATE = "https://docs.google.com/document/d/{document_id}/edit"
GOOGLE_DOCS_SCOPE = "https://www.googleapis.com/auth/documents"
GOOGLE_DRIVE_FILE_SCOPE = "https://www.googleapis.com/auth/drive.file"


def publish_markdown(
    *,
    content: str,
    title: str,
    folder_id: str | None = None,
    docs_service: Any | None = None,
    drive_service: Any | None = None,
) -> str:
    """Create a Google Doc and write markdown content as readable plain text."""
    credentials: Any | None = None
    if docs_service is None:
        credentials = _build_google_credentials(include_drive=folder_id is not None)
        docs_service = _build_docs_service(credentials=credentials)
    if folder_id and drive_service is None:
        if credentials is None:
            credentials = _build_google_credentials(include_drive=True)
        drive_service = _build_drive_service(credentials=credentials)

    document_id = _create_document(
        title=title,
        folder_id=folder_id,
        docs_service=docs_service,
        drive_service=drive_service,
    )

    if content:
        docs_service.documents().batchUpdate(
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


def _create_document(
    *,
    title: str,
    folder_id: str | None,
    docs_service: Any,
    drive_service: Any | None,
) -> str:
    if folder_id is None:
        document = docs_service.documents().create(body={"title": title}).execute()
        return str(document["documentId"])

    if drive_service is None:
        raise ValueError("drive_service is required when folder_id is provided")

    file = (
        drive_service.files()
        .create(
            body={
                "name": title,
                "mimeType": GOOGLE_DOC_MIME_TYPE,
                "parents": [folder_id],
            },
            fields="id",
        )
        .execute()
    )
    return str(file["id"])


def _build_google_credentials(*, include_drive: bool) -> Any:
    try:
        import google.auth
    except ImportError as exc:
        raise RuntimeError(
            "Google API dependencies are not installed. Install ka-destinations with "
            "its package dependencies before publishing to Google Docs."
        ) from exc

    scopes = [GOOGLE_DOCS_SCOPE]
    if include_drive:
        scopes.append(GOOGLE_DRIVE_FILE_SCOPE)

    credentials, _project_id = google.auth.default(scopes=scopes)
    return credentials


def _google_api_build() -> Any:
    try:
        from googleapiclient.discovery import build  # type: ignore[import-untyped]
    except ImportError as exc:
        raise RuntimeError(
            "Google API dependencies are not installed. Install ka-destinations with "
            "its package dependencies before publishing to Google Docs."
        ) from exc

    return build


def _build_docs_service(*, credentials: Any | None = None) -> Any:
    build = _google_api_build()

    if credentials is None:
        credentials = _build_google_credentials(include_drive=False)
    return build("docs", "v1", credentials=credentials)


def _build_drive_service(*, credentials: Any | None = None) -> Any:
    build = _google_api_build()

    if credentials is None:
        credentials = _build_google_credentials(include_drive=True)
    return build("drive", "v3", credentials=credentials)
