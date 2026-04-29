"""Behavior tests for the in-process CLI."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock

import pytest

from ka_destinations import cli, gdocs


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
