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

Publish a local `knowledge-adapters` bundle markdown file into a new Google Doc:

```bash
ka-destinations publish bundle.md --title "Example"
```

For a local validation pass that does not call Google APIs:

```bash
ka-destinations publish bundle.md --title "Example" --dry-run
```

## Google Auth

`ka-destinations` uses Google Application Default Credentials through
`google.auth.default()`. Configure credentials outside the tool; do not put
secrets in this repository.

Common setup options:

- Set `GOOGLE_APPLICATION_CREDENTIALS` to a service account JSON file that has
  access to create Docs for the target Google Workspace.
- Use `gcloud auth application-default login` for local development.

The publish flow requests the Google Docs scope:
`https://www.googleapis.com/auth/documents`.

## Scope Limits

`knowledge-adapters` handles acquisition and normalization. `ka-destinations`
handles the final publish step.

The initial Google Docs flow only creates a new document and inserts the bundle
markdown as readable plain text. It intentionally does not include:

- bidirectional sync
- document updates or patching
- folder selection
- sharing or permissions management
- Gemini-specific behavior
- watch mode
- background sync
