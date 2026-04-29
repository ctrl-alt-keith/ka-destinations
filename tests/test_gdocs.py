"""Unit tests for Google Docs publishing."""

from __future__ import annotations

from unittest.mock import Mock

import pytest

from ka_destinations import gdocs


def test_gdocs_publish_uses_docs_api_service() -> None:
    docs_service = Mock()
    documents = docs_service.documents.return_value
    documents.create.return_value.execute.return_value = {"documentId": "doc-id"}

    url = gdocs.publish_markdown(
        content="# Bundle\n",
        title="Example",
        docs_service=docs_service,
    )

    assert url == "https://docs.google.com/document/d/doc-id/edit"
    documents.create.assert_called_once_with(body={"title": "Example"})
    documents.batchUpdate.assert_called_once_with(
        documentId="doc-id",
        body={
            "requests": [
                {
                    "insertText": {
                        "location": {"index": 1},
                        "text": "# Bundle\n",
                    }
                }
            ]
        },
    )


def test_gdocs_publish_empty_content_skips_batch_update() -> None:
    docs_service = Mock()
    documents = docs_service.documents.return_value
    documents.create.return_value.execute.return_value = {"documentId": "doc-id"}

    url = gdocs.publish_markdown(
        content="",
        title="Example",
        docs_service=docs_service,
    )

    assert url == "https://docs.google.com/document/d/doc-id/edit"
    documents.create.assert_called_once_with(body={"title": "Example"})
    documents.batchUpdate.assert_not_called()


def test_gdocs_publish_creates_document_in_folder() -> None:
    docs_service = Mock()
    drive_service = Mock()
    documents = docs_service.documents.return_value
    drive_service.files.return_value.create.return_value.execute.return_value = {"id": "doc-id"}

    url = gdocs.publish_markdown(
        content="# Bundle\n",
        title="Example",
        folder_id="folder-123",
        docs_service=docs_service,
        drive_service=drive_service,
    )

    assert url == "https://docs.google.com/document/d/doc-id/edit"
    drive_service.files.return_value.create.assert_called_once_with(
        body={
            "name": "Example",
            "mimeType": "application/vnd.google-apps.document",
            "parents": ["folder-123"],
        },
        fields="id",
    )
    documents.create.assert_not_called()
    documents.batchUpdate.assert_called_once_with(
        documentId="doc-id",
        body={
            "requests": [
                {
                    "insertText": {
                        "location": {"index": 1},
                        "text": "# Bundle\n",
                    }
                }
            ]
        },
    )


def test_build_google_credentials_uses_docs_scope_only(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured_scopes: list[list[str]] = []

    def fake_default(*, scopes: list[str]) -> tuple[object, None]:
        captured_scopes.append(scopes)
        return object(), None

    import google.auth

    monkeypatch.setattr(google.auth, "default", fake_default)

    gdocs._build_google_credentials(include_drive=False)

    assert captured_scopes == [[gdocs.GOOGLE_DOCS_SCOPE]]


def test_build_google_credentials_adds_drive_scope_when_needed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured_scopes: list[list[str]] = []

    def fake_default(*, scopes: list[str]) -> tuple[object, None]:
        captured_scopes.append(scopes)
        return object(), None

    import google.auth

    monkeypatch.setattr(google.auth, "default", fake_default)

    gdocs._build_google_credentials(include_drive=True)

    assert captured_scopes == [
        [gdocs.GOOGLE_DOCS_SCOPE, gdocs.GOOGLE_DRIVE_FILE_SCOPE]
    ]
