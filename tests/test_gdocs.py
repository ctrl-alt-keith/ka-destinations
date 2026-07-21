"""Unit tests for Google Docs publishing."""

from __future__ import annotations

import sys
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
    documents.batchUpdate.return_value.execute.assert_called_once_with()


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
    documents.batchUpdate.return_value.execute.assert_called_once_with()


def test_gdocs_publish_builds_docs_service_without_drive(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    credentials = object()
    credential_requests: list[bool] = []
    docs_credentials: list[object | None] = []
    docs_service = Mock()
    documents = docs_service.documents.return_value
    documents.create.return_value.execute.return_value = {"documentId": "doc-id"}
    build_drive_service = Mock()

    def fake_build_google_credentials(*, include_drive: bool) -> object:
        credential_requests.append(include_drive)
        return credentials

    def fake_build_docs_service(*, credentials: object | None = None) -> Mock:
        docs_credentials.append(credentials)
        return docs_service

    monkeypatch.setattr(gdocs, "_build_google_credentials", fake_build_google_credentials)
    monkeypatch.setattr(gdocs, "_build_docs_service", fake_build_docs_service)
    monkeypatch.setattr(gdocs, "_build_drive_service", build_drive_service)

    url = gdocs.publish_markdown(content="# Bundle\n", title="Example")

    assert url == "https://docs.google.com/document/d/doc-id/edit"
    assert credential_requests == [False]
    assert docs_credentials == [credentials]
    build_drive_service.assert_not_called()
    documents.create.assert_called_once_with(body={"title": "Example"})
    documents.batchUpdate.assert_called_once()


def test_gdocs_publish_builds_drive_service_for_folder(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    credentials = object()
    credential_requests: list[bool] = []
    docs_credentials: list[object | None] = []
    drive_credentials: list[object | None] = []
    docs_service = Mock()
    drive_service = Mock()
    documents = docs_service.documents.return_value
    drive_service.files.return_value.create.return_value.execute.return_value = {"id": "doc-id"}

    def fake_build_google_credentials(*, include_drive: bool) -> object:
        credential_requests.append(include_drive)
        return credentials

    def fake_build_docs_service(*, credentials: object | None = None) -> Mock:
        docs_credentials.append(credentials)
        return docs_service

    def fake_build_drive_service(*, credentials: object | None = None) -> Mock:
        drive_credentials.append(credentials)
        return drive_service

    monkeypatch.setattr(gdocs, "_build_google_credentials", fake_build_google_credentials)
    monkeypatch.setattr(gdocs, "_build_docs_service", fake_build_docs_service)
    monkeypatch.setattr(gdocs, "_build_drive_service", fake_build_drive_service)

    url = gdocs.publish_markdown(
        content="# Bundle\n",
        title="Example",
        folder_id="folder-123",
    )

    assert url == "https://docs.google.com/document/d/doc-id/edit"
    assert credential_requests == [True]
    assert docs_credentials == [credentials]
    assert drive_credentials == [credentials]
    drive_service.files.return_value.create.assert_called_once_with(
        body={
            "name": "Example",
            "mimeType": "application/vnd.google-apps.document",
            "parents": ["folder-123"],
        },
        fields="id",
    )
    documents.create.assert_not_called()
    documents.batchUpdate.assert_called_once()


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


def test_build_google_credentials_reports_missing_google_auth(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setitem(sys.modules, "google.auth", None)

    with pytest.raises(
        RuntimeError,
        match="Google API dependencies are not installed",
    ) as error:
        gdocs._build_google_credentials(include_drive=False)

    assert isinstance(error.value.__cause__, ImportError)


def test_google_api_build_reports_missing_google_api_client(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setitem(sys.modules, "googleapiclient.discovery", None)

    with pytest.raises(
        RuntimeError,
        match="Google API dependencies are not installed",
    ) as error:
        gdocs._google_api_build()

    assert isinstance(error.value.__cause__, ImportError)
