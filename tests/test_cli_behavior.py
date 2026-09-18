"""Behavior tests for the in-process CLI."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import Mock

import pytest
from google.auth.exceptions import DefaultCredentialsError
from googleapiclient.errors import HttpError  # type: ignore[import-untyped]

from ka_destinations import cli, gdocs


def test_publish_dry_run_does_not_call_google_api(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bundle = tmp_path / "bundle.md"
    bundle.write_text("# Bundle\n\nHello.\n", encoding="utf-8")
    publish = Mock()
    monkeypatch.setattr(gdocs, "publish_markdown", publish)

    result = cli.main(["publish", str(bundle), "--title", "Example", "--dry-run"])

    assert result == 0
    publish.assert_not_called()


def test_publish_dry_run_can_emit_json_receipt(
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
            "--output-format",
            "json",
        ]
    )

    captured = capsys.readouterr()
    assert result == 0
    assert json.loads(captured.out) == {
        "bundle_path": str(bundle),
        "character_count": 17,
        "destination": "google_docs",
        "document_url": None,
        "dry_run": True,
        "folder_id": "folder-123",
        "title": "Example",
    }
    publish.assert_not_called()


def test_publish_dry_run_json_receipt_uses_normalized_metadata(
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
            "  Example  ",
            "--folder-id",
            "  folder-123  ",
            "--dry-run",
            "--output-format",
            "json",
        ]
    )

    captured = capsys.readouterr()
    assert result == 0
    assert json.loads(captured.out)["title"] == "Example"
    assert json.loads(captured.out)["folder_id"] == "folder-123"
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


def test_publish_uses_explicit_installed_app_oauth_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    bundle = tmp_path / "bundle.md"
    bundle.write_text("# Bundle\n", encoding="utf-8")
    client_file = tmp_path / "client.json"
    token_file = tmp_path / "token.json"
    publish = Mock(return_value="https://docs.google.com/document/d/doc-id/edit")
    monkeypatch.setattr(gdocs, "publish_markdown", publish)

    result = cli.main(
        [
            "publish",
            str(bundle),
            "--title",
            "Example",
            "--oauth-client-file",
            str(client_file),
            "--oauth-token-file",
            str(token_file),
        ]
    )

    assert result == 0
    publish.assert_called_once_with(
        content="# Bundle\n",
        title="Example",
        folder_id=None,
        oauth_client_file=client_file,
        oauth_token_file=token_file,
    )
    assert capsys.readouterr().err == ""


@pytest.mark.parametrize("option", ["--oauth-client-file", "--oauth-token-file"])
def test_publish_requires_both_installed_app_oauth_files(
    tmp_path: Path, option: str, capsys: pytest.CaptureFixture[str]
) -> None:
    bundle = tmp_path / "bundle.md"
    bundle.write_text("# Bundle\n", encoding="utf-8")

    with pytest.raises(SystemExit) as error:
        cli.main(["publish", str(bundle), "--title", "Example", option, "one.json"])

    assert error.value.code == 2
    assert (
        "--oauth-client-file and --oauth-token-file must be used together"
        in capsys.readouterr().err
    )


def test_publish_can_emit_json_receipt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    bundle = tmp_path / "bundle.md"
    bundle.write_text("# Bundle\n\nHello.\n", encoding="utf-8")
    publish = Mock(return_value="https://docs.google.com/document/d/doc-id/edit")
    monkeypatch.setattr(gdocs, "publish_markdown", publish)

    result = cli.main(
        [
            "publish",
            str(bundle),
            "--title",
            "Example",
            "--output-format",
            "json",
        ]
    )

    captured = capsys.readouterr()
    assert result == 0
    publish.assert_called_once_with(
        content="# Bundle\n\nHello.\n",
        title="Example",
        folder_id=None,
    )
    assert json.loads(captured.out) == {
        "bundle_path": str(bundle),
        "character_count": 17,
        "destination": "google_docs",
        "document_url": "https://docs.google.com/document/d/doc-id/edit",
        "dry_run": False,
        "folder_id": None,
        "title": "Example",
    }


def test_publish_failure_uses_generic_message_for_unknown_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    bundle = tmp_path / "bundle.md"
    bundle.write_text("# Bundle\n\nHello.\n", encoding="utf-8")
    publish = Mock(side_effect=RuntimeError("destination unavailable"))
    monkeypatch.setattr(gdocs, "publish_markdown", publish)

    result = cli.main(["publish", str(bundle), "--title", "Example"])

    captured = capsys.readouterr()
    assert result == 1
    assert captured.out == ""
    assert captured.err == "publish failed: Google Docs API request was unsuccessful\n"
    publish.assert_called_once_with(
        content="# Bundle\n\nHello.\n",
        title="Example",
        folder_id=None,
    )


def test_publish_failure_does_not_echo_synthetic_secret(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    bundle = tmp_path / "bundle.md"
    bundle.write_text("# Bundle\n\nHello.\n", encoding="utf-8")
    synthetic_secret = "synthetic-google-api-token-for-test"
    publish = Mock(side_effect=RuntimeError(f"File {synthetic_secret} was not found."))
    monkeypatch.setattr(gdocs, "publish_markdown", publish)

    result = cli.main(["publish", str(bundle), "--title", "Example"])

    captured = capsys.readouterr()
    assert result == 1
    assert synthetic_secret not in captured.err
    assert captured.err == "publish failed: Google Docs API request was unsuccessful\n"


def test_publish_failure_reports_safe_google_auth_guidance(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    bundle = tmp_path / "bundle.md"
    bundle.write_text("# Bundle\n\nHello.\n", encoding="utf-8")
    synthetic_secret = "synthetic-google-api-token-for-test"
    publish = Mock(side_effect=DefaultCredentialsError(synthetic_secret))  # type: ignore[no-untyped-call]
    monkeypatch.setattr(gdocs, "publish_markdown", publish)

    result = cli.main(["publish", str(bundle), "--title", "Example"])

    captured = capsys.readouterr()
    assert result == 1
    assert synthetic_secret not in captured.err
    assert captured.err == (
        "publish failed: Google authentication failed; check Application Default Credentials\n"
    )


def test_publish_failure_hides_installed_app_oauth_details(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    bundle = tmp_path / "bundle.md"
    bundle.write_text("# Bundle\n", encoding="utf-8")
    synthetic_secret = "synthetic-google-api-token-for-test"
    publish = Mock(side_effect=gdocs.InstalledAppOAuthError(synthetic_secret))
    monkeypatch.setattr(gdocs, "publish_markdown", publish)

    result = cli.main(["publish", str(bundle), "--title", "Example"])

    captured = capsys.readouterr()
    assert result == 1
    assert synthetic_secret not in captured.err
    assert captured.err == (
        "publish failed: Google installed-app OAuth failed; "
        "check the OAuth client and token files\n"
    )


@pytest.mark.parametrize(
    ("reason", "expected_reason"),
    [
        ("insufficientPermissions", "insufficientPermissions"),
        ("accessNotConfigured", "accessNotConfigured"),
    ],
)
def test_publish_failure_reports_safe_google_403_reason(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    reason: str,
    expected_reason: str,
) -> None:
    bundle = tmp_path / "bundle.md"
    bundle.write_text("# Bundle\n\nHello.\n", encoding="utf-8")
    synthetic_secret = "synthetic-google-api-token-for-test"
    arbitrary_response_content = "arbitrary-provider-response-content"
    response = Mock()
    response.status = 403
    content = json.dumps(
        {
            "error": {
                "status": "PERMISSION_DENIED",
                "message": synthetic_secret,
                "errors": [
                    {
                        "reason": reason,
                        "message": arbitrary_response_content,
                        "resource": "sensitive-resource-id",
                    }
                ],
            }
        }
    ).encode()
    publish = Mock(side_effect=HttpError(response, content))
    monkeypatch.setattr(gdocs, "publish_markdown", publish)

    result = cli.main(["publish", str(bundle), "--title", "Example"])

    captured = capsys.readouterr()
    assert result == 1
    assert synthetic_secret not in captured.err
    assert arbitrary_response_content not in captured.err
    assert "sensitive-resource-id" not in captured.err
    assert captured.err == (
        "publish failed: Google API request was forbidden "
        f"(HTTP 403, status PERMISSION_DENIED, reason {expected_reason}); "
        "check Google Docs or Drive access\n"
    )


def test_publish_failure_ignores_untrusted_google_403_fields(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    bundle = tmp_path / "bundle.md"
    bundle.write_text("# Bundle\n\nHello.\n", encoding="utf-8")
    synthetic_secret = "synthetic-google-api-token-for-test"
    arbitrary_response_content = "arbitrary-provider-response-content"
    response = Mock()
    response.status = 403
    content = json.dumps(
        {
            "error": {
                "status": "UNTRUSTED_PROVIDER_STATUS",
                "message": synthetic_secret,
                "errors": [
                    {
                        "reason": "untrustedProviderReason",
                        "message": arbitrary_response_content,
                        "resource": "sensitive-resource-id",
                    }
                ],
            }
        }
    ).encode()
    publish = Mock(side_effect=HttpError(response, content))
    monkeypatch.setattr(gdocs, "publish_markdown", publish)

    result = cli.main(["publish", str(bundle), "--title", "Example"])

    captured = capsys.readouterr()
    assert result == 1
    assert synthetic_secret not in captured.err
    assert arbitrary_response_content not in captured.err
    assert "sensitive-resource-id" not in captured.err
    assert "UNTRUSTED_PROVIDER_STATUS" not in captured.err
    assert "untrustedProviderReason" not in captured.err
    assert captured.err == (
        "publish failed: Google API request was forbidden (HTTP 403); "
        "check Google Docs or Drive access\n"
    )


def test_publish_reports_input_read_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    bundle = tmp_path / "bundle.md"
    bundle.write_text("# Bundle\n", encoding="utf-8")

    def raise_permission_error(self: Path, *, encoding: str) -> str:
        raise PermissionError("permission denied")

    monkeypatch.setattr(Path, "read_text", raise_permission_error)

    with pytest.raises(SystemExit) as error:
        cli.main(["publish", str(bundle), "--title", "Example", "--dry-run"])

    assert error.value.code == 2
    captured = capsys.readouterr()
    assert f"unable to read input file: {bundle}: permission denied" in captured.err


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


def test_publish_trims_non_empty_title_and_folder_id(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    bundle = tmp_path / "bundle.md"
    bundle.write_text("# Bundle\n\nHello.\n", encoding="utf-8")
    publish = Mock(return_value="https://docs.google.com/document/d/doc-id/edit")
    monkeypatch.setattr(gdocs, "publish_markdown", publish)

    result = cli.main(
        [
            "publish",
            str(bundle),
            "--title",
            "  Example  ",
            "--folder-id",
            "  folder-123  ",
        ]
    )

    captured = capsys.readouterr()
    assert result == 0
    publish.assert_called_once_with(
        content="# Bundle\n\nHello.\n",
        title="Example",
        folder_id="folder-123",
    )
    assert captured.out.strip() == "https://docs.google.com/document/d/doc-id/edit"
