# ka-destinations

Minimal destination-layer CLI tools for taking `knowledge-adapters` output and
publishing it into downstream destinations.

## Relationship to knowledge-adapters

`knowledge-adapters` is responsible for acquisition and normalization.
`ka-destinations` is responsible for the final publish step into a destination
system.

Workflow:

`knowledge-adapters` -> `bundle` -> `ka-destinations` -> destination (for
example, Google Docs)

## Current status

This repository currently provides a minimal CLI baseline with a placeholder
`publish` command. It does not yet implement any destination-specific logic,
OAuth flow, or credentials handling.

## Development

```bash
make check
.venv/bin/ka-destinations --help
```
