"""Smoke tests for the CLI."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

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
