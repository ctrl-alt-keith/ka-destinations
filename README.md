# ka-destinations

Minimal destination-layer CLI tools for taking `knowledge-adapters` output and
publishing it into downstream destinations.

## Install

```bash
pipx install git+https://github.com/ctrl-alt-keith/ka-destinations.git@main
```

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
make check
```

## Usage

```bash
ka-destinations publish bundle.md --title "Example"
```

## Branches

Use `feat/`, `fix/`, `docs/`, or `chore/` prefixes. Avoid `codex/` for normal
work.

## Current status

`knowledge-adapters` handles acquisition and normalization. `ka-destinations`
handles the final publish step. The current `publish` command is a placeholder;
destination-specific logic, OAuth flow, and credentials handling are not
implemented yet.
```
