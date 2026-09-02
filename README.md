# ka-destinations

Minimal destination-layer CLI tools that currently implement
destination-specific publishing behavior for the Publication Product
Candidate.

Publication owns the authorized external-delivery transaction and
publication-receipt semantics. An authorized publication authorizer supplies
the consequential authorization. The CLI and destination drivers perform the
runtime work, and this repository currently implements that behavior and emits
the resulting receipts.

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

Publish a caller-supplied local bundle markdown file into a new Google Doc:

```bash
ka-destinations publish bundle.md --title "Example"
```

To create the document in a specific Google Drive folder, pass its folder ID:

```bash
ka-destinations publish bundle.md --title "Example" --folder-id "folder-123"
```

Blank titles and blank folder IDs are rejected before any Google API call.

For a local validation pass that does not call Google APIs:

```bash
ka-destinations publish bundle.md --title "Example" --dry-run
```

For automation-friendly publication receipts, request JSON output:

```bash
ka-destinations publish bundle.md --title "Example" --dry-run --output-format json
```

The JSON receipt includes the destination, title, input path, character count,
folder ID when provided, dry-run status, and published document URL when a live
publish succeeds. The receipt is runtime evidence of the requested or performed
operation; it is not publication authorization, editorial approval, or proof
that the caller-supplied artifact should be retained.

If a live publish fails, the CLI reports `publish failed: ...` on stderr,
returns exit code 1, and does not emit a publication receipt.

Before creating a Google Doc, the publisher rejects control characters and
BMP private-use characters that Google Docs would silently remove. These
content-preservation failures use the same stderr, exit-code, and no-receipt
contract.

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

When `--folder-id` is used, it also requests the Google Drive file scope:
`https://www.googleapis.com/auth/drive.file`.

## Scope Limits

The Source Acquisition Product Candidate owns acquisition semantics, and
`knowledge-adapters` currently implements acquisition and normalization.
Publication owns the authorized external-delivery transaction, while
`ka-destinations` currently implements the destination-specific publish step.

The caller supplies the artifact to publish and is responsible for selecting
the exact artifact covered by the publication authorization. This repository
does not acquire the artifact, make an editorial or retention decision, or
create publication authorization from successful validation or execution.

For contributor-facing product boundaries, see
[`docs/product-boundary.md`](docs/product-boundary.md).

The initial Google Docs flow only creates a new document and inserts the bundle
markdown as readable plain text. It intentionally does not include:

- bidirectional sync
- document updates or patching
- sharing or permissions management
- Gemini-specific behavior
- watch mode
- background sync

> AI-generated. Human-verified. Occasionally argued about.
