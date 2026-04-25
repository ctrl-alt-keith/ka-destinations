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


def test_publish_placeholder_runs() -> None:
    result = run_cli("publish")

    assert result.returncode == 0
    assert result.stdout.strip() == "Publish is not implemented yet."
