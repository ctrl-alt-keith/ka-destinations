"""Google Docs publishing helpers."""

from __future__ import annotations

import json
import os
import stat
import tempfile
from pathlib import Path
from typing import Any

GOOGLE_DOC_MIME_TYPE = "application/vnd.google-apps.document"
GOOGLE_DOCS_URL_TEMPLATE = "https://docs.google.com/document/d/{document_id}/edit"
GOOGLE_DOCS_SCOPE = "https://www.googleapis.com/auth/documents"
GOOGLE_DRIVE_FILE_SCOPE = "https://www.googleapis.com/auth/drive.file"
_MAX_GOOGLE_ERROR_CONTENT_BYTES = 8192
_SAFE_GOOGLE_403_STATUSES = frozenset({"PERMISSION_DENIED"})
_SAFE_GOOGLE_403_REASONS = frozenset(
    {
        "accessNotConfigured",
        "dailyLimitExceeded",
        "forbidden",
        "insufficientPermissions",
        "quotaExceeded",
        "rateLimitExceeded",
        "serviceDisabled",
        "userRateLimitExceeded",
    }
)


class InstalledAppOAuthError(RuntimeError):
    """Raised when the explicit installed-app OAuth configuration cannot be used."""


def publish_failure_message(error: BaseException) -> str:
    """Return an operator-safe summary for a failed Google publish."""
    error_type = type(error)
    if error_type is InstalledAppOAuthError:
        return "Google installed-app OAuth failed; check the OAuth client and token files"
    if (
        error_type.__module__ == "google.auth.exceptions"
        and error_type.__name__
        in {"DefaultCredentialsError", "RefreshError", "UserAccessTokenError"}
    ):
        return "Google authentication failed; check Application Default Credentials"

    if not (
        error_type.__module__ == "googleapiclient.errors" and error_type.__name__ == "HttpError"
    ):
        return "Google Docs API request was unsuccessful"

    status = getattr(getattr(error, "resp", None), "status", None)
    if not isinstance(status, int):
        return "Google API request failed"
    if status == 401:
        return "Google API authentication failed (HTTP 401); check Application Default Credentials"
    if status == 403:
        details = _safe_google_403_details(error)
        return (
            "Google API request was forbidden (HTTP 403"
            f"{details}); check Google Docs or Drive access"
        )
    if status == 404:
        return "Google API resource was not found (HTTP 404); check the configured resource ID"
    if status == 429:
        return "Google API rate limit reached (HTTP 429); retry later"
    if 500 <= status <= 599:
        return f"Google API service failed (HTTP {status}); retry later"
    return f"Google API request failed (HTTP {status}); check the publish configuration"


def _safe_google_403_details(error: BaseException) -> str:
    """Return allowlisted structured 403 fields without exposing provider content."""
    content = getattr(error, "content", None)
    if not isinstance(content, bytes) or len(content) > _MAX_GOOGLE_ERROR_CONTENT_BYTES:
        return ""

    try:
        payload = json.loads(content.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return ""

    if not isinstance(payload, dict):
        return ""
    provider_error = payload.get("error")
    if not isinstance(provider_error, dict):
        return ""

    details: list[str] = []
    provider_status = provider_error.get("status")
    if provider_status in _SAFE_GOOGLE_403_STATUSES:
        details.append(f"status {provider_status}")

    errors = provider_error.get("errors")
    if isinstance(errors, list):
        for item in errors:
            if not isinstance(item, dict):
                continue
            reason = item.get("reason")
            if reason in _SAFE_GOOGLE_403_REASONS:
                details.append(f"reason {reason}")
                break

    return f", {', '.join(details)}" if details else ""


def _validate_insertable_content(content: str) -> None:
    """Reject characters the Docs API would silently remove from published text."""
    for character in content:
        codepoint = ord(character)
        if (0x0000 <= codepoint <= 0x0008) or (0x000C <= codepoint <= 0x001F) or (
            0xE000 <= codepoint <= 0xF8FF
        ):
            raise ValueError(
                "Google Docs cannot preserve unsupported character "
                f"U+{codepoint:04X} in published content"
            )


def _required_non_empty(value: str, *, label: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{label} must not be blank")
    return normalized


def publish_markdown(
    *,
    content: str,
    title: str,
    folder_id: str | None = None,
    docs_service: Any | None = None,
    drive_service: Any | None = None,
    oauth_client_file: Path | None = None,
    oauth_token_file: Path | None = None,
) -> str:
    """Create a Google Doc and write markdown content as readable plain text."""
    title = _required_non_empty(title, label="title")
    if folder_id is not None:
        folder_id = _required_non_empty(folder_id, label="folder_id")
    _validate_insertable_content(content)

    if (oauth_client_file is None) != (oauth_token_file is None):
        raise ValueError("oauth_client_file and oauth_token_file must be used together")

    credentials: Any | None = None
    if docs_service is None:
        credentials = _selected_google_credentials(
            include_drive=folder_id is not None,
            oauth_client_file=oauth_client_file,
            oauth_token_file=oauth_token_file,
        )
        docs_service = _build_docs_service(credentials=credentials)
    if folder_id and drive_service is None:
        if credentials is None:
            credentials = _selected_google_credentials(
                include_drive=True,
                oauth_client_file=oauth_client_file,
                oauth_token_file=oauth_token_file,
            )
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
        return _required_document_id(document, field="documentId")

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
    return _required_document_id(file, field="id")


def _required_document_id(response: Any, *, field: str) -> str:
    if not isinstance(response, dict):
        raise RuntimeError("Google API create response did not contain a document ID")

    document_id = response.get(field)
    if not isinstance(document_id, str) or not document_id.strip():
        raise RuntimeError("Google API create response did not contain a document ID")
    return document_id.strip()


def _google_scopes(*, include_drive: bool) -> list[str]:
    scopes = [GOOGLE_DOCS_SCOPE]
    if include_drive:
        scopes.append(GOOGLE_DRIVE_FILE_SCOPE)
    return scopes


def _selected_google_credentials(
    *,
    include_drive: bool,
    oauth_client_file: Path | None,
    oauth_token_file: Path | None,
) -> Any:
    if oauth_client_file is None:
        return _build_google_credentials(include_drive=include_drive)
    return _build_google_credentials(
        include_drive=include_drive,
        oauth_client_file=oauth_client_file,
        oauth_token_file=oauth_token_file,
    )


def _build_google_credentials(
    *,
    include_drive: bool,
    oauth_client_file: Path | None = None,
    oauth_token_file: Path | None = None,
) -> Any:
    """Load opt-in installed-app OAuth credentials or the existing ADC credentials."""
    if oauth_client_file is not None and oauth_token_file is not None:
        return _build_installed_app_oauth_credentials(
            client_file=oauth_client_file,
            token_file=oauth_token_file,
            scopes=_google_scopes(include_drive=include_drive),
        )
    if oauth_client_file is not None or oauth_token_file is not None:
        raise ValueError("oauth_client_file and oauth_token_file must be used together")

    try:
        import google.auth
    except ImportError as exc:
        raise RuntimeError(
            "Google API dependencies are not installed. Install ka-destinations with "
            "its package dependencies before publishing to Google Docs."
        ) from exc

    credentials, _project_id = google.auth.default(
        scopes=_google_scopes(include_drive=include_drive)
    )
    return credentials


def _build_installed_app_oauth_credentials(
    *, client_file: Path, token_file: Path, scopes: list[str]
) -> Any:
    """Use an explicit Desktop client and caller-selected private token file."""
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore[import-untyped]
    except ImportError as exc:
        raise RuntimeError(
            "Google API dependencies are not installed. Install ka-destinations with "
            "its package dependencies before publishing to Google Docs."
        ) from exc

    try:
        credentials: Any | None = None
        if os.path.lexists(token_file):
            _prepare_oauth_token_file(token_file)
            if _stored_oauth_token_has_scopes(token_file, scopes):
                credentials = Credentials.from_authorized_user_file(  # type: ignore[no-untyped-call]
                    str(token_file), scopes=scopes
                )
        if credentials is not None and credentials.valid:
            return credentials
        if credentials is not None and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(client_file), scopes=scopes)
            credentials = flow.run_local_server(port=0, access_type="offline", prompt="consent")
        _persist_oauth_token(token_file, credentials)
        return credentials
    except Exception as exc:
        raise InstalledAppOAuthError("installed-app OAuth configuration failed") from exc


def _prepare_oauth_token_file(token_file: Path) -> None:
    """Reject non-private token files before they can be read or refreshed."""
    token_stat = token_file.lstat()
    if not stat.S_ISREG(token_stat.st_mode) or token_stat.st_uid != os.geteuid():
        raise ValueError("OAuth token file is not a private regular file")
    os.chmod(token_file, 0o600)


def _stored_oauth_token_has_scopes(token_file: Path, scopes: list[str]) -> bool:
    """Use a stored token only when it records every scope required for this publish."""
    token_data = json.loads(token_file.read_text(encoding="utf-8"))
    stored_scopes = token_data.get("scopes") if isinstance(token_data, dict) else None
    if not isinstance(stored_scopes, list) or not all(
        isinstance(scope, str) for scope in stored_scopes
    ):
        return False
    return set(scopes).issubset(stored_scopes)


def _persist_oauth_token(token_file: Path, credentials: Any) -> None:
    """Atomically persist credentials only at the caller-selected path, mode 0600."""
    token_json = credentials.to_json()
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=token_file.parent, prefix=".ka-destinations-", delete=False
    ) as temporary_file:
        temporary_path = Path(temporary_file.name)
        try:
            os.chmod(temporary_path, 0o600)
            temporary_file.write(token_json)
            temporary_file.flush()
            os.fsync(temporary_file.fileno())
            os.replace(temporary_path, token_file)
            os.chmod(token_file, 0o600)
        except Exception:
            temporary_path.unlink(missing_ok=True)
            raise


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
