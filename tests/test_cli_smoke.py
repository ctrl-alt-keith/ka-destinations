"""Smoke tests for the CLI."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import Mock

import pytest

from ka_destinations import cli, gdocs

ROOT = Path(__file__).resolve().parents[1]


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    pythonpath = str(ROOT / "src")
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        pythonpath
        if existing_pythonpath is None
        else f"{pythonpath}:{existing_pythonpath}"
    )

    return subprocess.run(
        [sys.executable, "-m", "ka_destinations.cli", *args],
        cwd=ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )


def test_top_level_help() -> None:
    result = run_cli("--help")

    assert result.returncode == 0
    assert "usage: ka-destinations" in result.stdout
    assert "publish" in result.stdout


def test_publish_help_lists_required_args() -> None:
    result = run_cli("publish", "--help")

    assert result.returncode == 0
    assert "bundle" in result.stdout
    assert "--title" in result.stdout
    assert "--dry-run" in result.stdout
    assert "--folder-id" in result.stdout


def test_publish_requires_title(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle.md"
    bundle.write_text("# Bundle\n", encoding="utf-8")

    result = run_cli("publish", str(bundle))

    assert result.returncode == 2
    assert "the following arguments are required: --title" in result.stderr


def test_publish_missing_input_file() -> None:
    result = run_cli("publish", "missing.md", "--title", "Example", "--dry-run")

    assert result.returncode == 2
    assert "input file does not exist: missing.md" in result.stderr


def test_publish_rejects_directory_input(tmp_path: Path) -> None:
    result = run_cli("publish", str(tmp_path), "--title", "Example", "--dry-run")

    assert result.returncode == 2
    assert f"input path is not a file: {tmp_path}" in result.stderr


def test_publish_rejects_non_utf8_file(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle.md"
    bundle.write_bytes(b"\xff\xfe\x00")

    result = run_cli("publish", str(bundle), "--title", "Example", "--dry-run")

    assert result.returncode == 2
    assert "input file is not valid UTF-8 text" in result.stderr


def test_publish_dry_run_does_not_call_google_api(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    bundle = tmp_path / "bundle.md"
    bundle.write_text("# Bundle\n\nHello.\n", encoding="utf-8")
    publish = Mock()
    monkeypatch.setattr(gdocs, "publish_markdown", publish)

    result = cli.main(["publish", str(bundle), "--title", "Example", "--dry-run"])

    captured = capsys.readouterr()
    assert result == 0
    assert "Dry run: would publish" in captured.out
    assert 'with title "Example"' in captured.out
    publish.assert_not_called()


def test_publish_dry_run_reports_folder_target(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    bundle = tmp_path / "bundle.md"
    bundle.write_text("# Bundle\n\nHello.\n", encoding="utf-8")
    publish = Mock()
    monkeypatch.setattr(gdocs, "publish_markdown", publish)

    result = cli.main(
        [
            "publish",
            str(bundle),
            "--title",
            "Example",
            "--folder-id",
            "folder-123",
            "--dry-run",
        ]
    )

    captured = capsys.readouterr()
    assert result == 0
    assert 'with title "Example" in Google Drive folder "folder-123".' in captured.out
    publish.assert_not_called()


def test_publish_calls_google_api_with_bundle_content(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    bundle = tmp_path / "bundle.md"
    bundle.write_text("# Bundle\n\nHello.\n", encoding="utf-8")
    publish = Mock(return_value="https://docs.google.com/document/d/doc-id/edit")
    monkeypatch.setattr(gdocs, "publish_markdown", publish)

    result = cli.main(["publish", str(bundle), "--title", "Example"])

    captured = capsys.readouterr()
    assert result == 0
    publish.assert_called_once_with(
        content="# Bundle\n\nHello.\n",
        title="Example",
        folder_id=None,
    )
    assert captured.out.strip() == "https://docs.google.com/document/d/doc-id/edit"


def test_publish_calls_google_api_with_folder_id(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    bundle = tmp_path / "bundle.md"
    bundle.write_text("# Bundle\n\nHello.\n", encoding="utf-8")
    publish = Mock(return_value="https://docs.google.com/document/d/doc-id/edit")
    monkeypatch.setattr(gdocs, "publish_markdown", publish)

    result = cli.main(
        ["publish", str(bundle), "--title", "Example", "--folder-id", "folder-123"]
    )

    captured = capsys.readouterr()
    assert result == 0
    publish.assert_called_once_with(
        content="# Bundle\n\nHello.\n",
        title="Example",
        folder_id="folder-123",
    )
    assert captured.out.strip() == "https://docs.google.com/document/d/doc-id/edit"


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
